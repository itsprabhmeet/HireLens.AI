"""
explain.py
----------
Day 8-9: SHAP-based explainability layer.
Given a resume TF-IDF vector and a trained model, compute SHAP values
to explain which words/features pushed the fit score up or down.

Usage:
    python src/explain.py
"""

import os
import traceback
import logging
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ── Custom Linear SHAP (pure Python/NumPy — no DLL required) ─────────────────
class LinearSHAP:
    """
    Pure-Python SHAP explainer for linear models (LogisticRegression).

    Computes values mathematically identical to shap.LinearExplainer:
        shap_value[j] = coef[class, j] × (x[j] - E[background[:, j]])

    No compiled C extensions or DLLs required — works on any machine
    regardless of Windows Application Control policies.
    """

    def __init__(self, model, background_data):
        """
        Parameters
        ----------
        model : fitted LogisticRegression
        background_data : sparse or dense array (n_samples × n_features)
            Representative sample of training data used to compute feature means.
        """
        self.model = model
        self.coef = model.coef_          # shape: (n_classes, n_features)
        self.intercept = model.intercept_  # shape: (n_classes,)

        # Compute per-feature mean over background (E[X_j])
        if hasattr(background_data, "toarray"):
            bg_dense = np.asarray(background_data.toarray())
        else:
            bg_dense = np.asarray(background_data)
        self.feature_means = np.nan_to_num(np.mean(bg_dense, axis=0).flatten(), nan=0.0, posinf=0.0, neginf=0.0)

        # Expected value per class = model output on background mean
        bg_mean_vec = self.feature_means.reshape(1, -1)
        raw_logits = np.dot(bg_mean_vec, self.coef.T) + self.intercept
        log_odds = np.clip(np.nan_to_num(raw_logits, nan=0.0), -50.0, 50.0)
        # Softmax to get probability
        exp_lo = np.exp(log_odds - np.max(log_odds))
        proba_bg = (exp_lo / np.sum(exp_lo)).flatten()
        self.expected_value = proba_bg.tolist()  # list, one per class

    def shap_values(self, X):
        """
        Compute SHAP values for input X.

        Parameters
        ----------
        X : array-like (1 × n_features) or sparse

        Returns
        -------
        list of np.ndarray — one (n_features,) array per class,
        matching the format of shap.LinearExplainer.shap_values()
        """
        if hasattr(X, "toarray"):
            x_dense = X.toarray()
        else:
            x_dense = np.array(X)

        # Deviation from background mean
        delta = x_dense - self.feature_means  # (1, n_features)

        # SHAP value for each class: coef[c, :] * delta[0, :]
        shap_per_class = [
            (self.coef[c] * delta[0]).astype(float)
            for c in range(self.coef.shape[0])
        ]
        return shap_per_class


# ── Explainer Factory ─────────────────────────────────────────────────────────
def get_shap_explainer(model, X_train_sample=None):
    """
    Return the best available SHAP explainer for the model.

    Priority:
    1. shap.LinearExplainer (if SHAP library loads without DLL errors)
    2. LinearSHAP (pure-Python fallback — identical math, no DLL needed)
    """
    from sklearn.linear_model import LogisticRegression

    import importlib.util

    if not isinstance(model, LogisticRegression):
        # For tree models, try SHAP TreeExplainer
        try:
            if importlib.util.find_spec("shap") is not None:
                shap_mod = importlib.import_module("shap")
                return shap_mod.TreeExplainer(model)
        except Exception as e:
            logger.warning(f"TreeExplainer unavailable: {e}")
            return None

    # Try native SHAP first
    if X_train_sample is not None:
        try:
            if importlib.util.find_spec("shap") is not None:
                shap_mod = importlib.import_module("shap")
                explainer = shap_mod.LinearExplainer(
                    model, X_train_sample,
                    feature_perturbation="interventional"
                )
                logger.info("Using shap.LinearExplainer (native)")
                return explainer
        except Exception as e:
            logger.warning(f"shap.LinearExplainer unavailable ({e}). Using pure-Python LinearSHAP.")

    # Fallback: our custom pure-Python implementation
    background = X_train_sample if X_train_sample is not None else np.zeros((1, model.coef_.shape[1]))
    bg_n_features = background.shape[1] if hasattr(background, "shape") else None
    expected_n_features = model.coef_.shape[1]
    if bg_n_features is not None and bg_n_features != expected_n_features:
        logger.warning(
            f"Background sample has {bg_n_features} features but the model expects "
            f"{expected_n_features} -- stale data/X_train_sample.pkl from a previous "
            f"vectorizer fit. Using a zero background for this explanation instead of "
            f"crashing; retrain to regenerate a matching sample."
        )
        background = np.zeros((1, expected_n_features))
    explainer = LinearSHAP(model, background)
    logger.info("Using LinearSHAP (pure-Python, no DLL required)")
    return explainer


def compute_shap_values(
    explainer,
    resume_tfidf,
    predicted_class_idx: int,
):
    """
    Compute SHAP values for a single resume vector.

    Parameters
    ----------
    explainer : SHAP explainer or LinearSHAP instance
    resume_tfidf : sparse or dense array (1 x n_features)
    predicted_class_idx : index of the predicted class (for multi-class)

    Returns
    -------
    np.ndarray of shape (n_features,) — SHAP values for the predicted class
    """
    # Convert sparse to dense if needed
    if hasattr(resume_tfidf, "toarray"):
        resume_dense = resume_tfidf.toarray()
    else:
        resume_dense = np.array(resume_tfidf)

    shap_values = explainer.shap_values(resume_dense)

    # shap_values is a list — one array per class (both shap lib and LinearSHAP)
    if isinstance(shap_values, list):
        class_vals = shap_values[predicted_class_idx]
        # Could be 1D (LinearSHAP) or 2D shape (1, n_features) from shap lib
        values = np.array(class_vals).flatten()
    else:
        values = np.array(shap_values).flatten()

    return values


def get_top_shap_features(
    shap_values: np.ndarray,
    feature_names: np.ndarray,
    top_n: int = 15,
) -> dict:
    """
    Extract top positive and negative SHAP features.

    Returns
    -------
    dict with:
        'positive': [(feature, shap_val), ...] — pushed score UP
        'negative': [(feature, shap_val), ...] — pushed score DOWN
    """
    # Only consider features that actually appeared in the resume (non-zero SHAP)
    nonzero_mask = shap_values != 0
    if not nonzero_mask.any():
        return {"positive": [], "negative": []}

    values = shap_values[nonzero_mask]
    names = feature_names[nonzero_mask]

    # Sort by absolute value
    sorted_idx = np.argsort(np.abs(values))[::-1]
    values = values[sorted_idx]
    names = names[sorted_idx]

    positive = [(names[i], round(values[i], 5)) for i in range(len(values)) if values[i] > 0][:top_n]
    negative = [(names[i], round(values[i], 5)) for i in range(len(values)) if values[i] < 0][:top_n]

    return {"positive": positive, "negative": negative}


# ── Plotting ──────────────────────────────────────────────────────────────────
def plot_shap_bar(
    shap_features: dict,
    predicted_category: str,
    fit_score: float,
    save_path: str = None,
) -> plt.Figure:
    """
    Create a horizontal bar chart of top SHAP features.
    Green bars = positive contributions, red bars = negative contributions.

    Returns matplotlib Figure (can be passed directly to st.pyplot).
    """
    positive = shap_features.get("positive", [])[:10]
    negative = shap_features.get("negative", [])[:10]

    all_features = positive + negative
    if not all_features:
        logger.warning("No SHAP features to plot.")
        return None

    labels = [f[0] for f in all_features]
    values = [f[1] for f in all_features]
    colors = ["#2ecc71" if v > 0 else "#e74c3c" for v in values]

    # Sort by value for better visualization
    paired = sorted(zip(values, labels, colors), key=lambda x: x[0])
    values, labels, colors = zip(*paired) if paired else ([], [], [])

    fig, ax = plt.subplots(figsize=(9, max(5, len(labels) * 0.5 + 1)))
    fig.patch.set_facecolor("#131829")
    ax.set_facecolor("#131829")

    bars = ax.barh(labels, values, color=colors, height=0.6, edgecolor="none")

    # Add value labels on bars
    for bar, val in zip(bars, values):
        x_pos = bar.get_width()
        offset = 0.001 if val >= 0 else -0.001
        ax.text(
            x_pos + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{val:+.4f}",
            va="center",
            ha="left" if val >= 0 else "right",
            color="white",
            fontsize=8,
        )

    ax.axvline(0, color="white", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("SHAP Value (contribution to fit score)", color="white", fontsize=10)
    ax.set_title(
        f"Feature Importance — Predicted: {predicted_category} (Score: {fit_score:.1f}%)",
        color="white",
        fontsize=11,
        pad=12,
    )
    ax.tick_params(colors="white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#333")
    ax.spines["bottom"].set_color("#333")

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
        fig.savefig(save_path, dpi=150, facecolor=fig.get_facecolor())
        logger.info(f"SHAP plot saved: {save_path}")

    return fig


def plot_shap_waterfall(
    shap_values: np.ndarray,
    feature_names: np.ndarray,
    base_value: float,
    save_path: str = None,
    top_n: int = 15,
) -> plt.Figure:
    """
    Simple waterfall-style plot showing cumulative SHAP value contributions.
    Simulates shap.plots.waterfall without needing SHAP's full display system.
    """
    # Get top features by absolute SHAP value
    abs_vals = np.abs(shap_values)
    top_idx = abs_vals.argsort()[::-1][:top_n]

    selected_vals = shap_values[top_idx]
    selected_names = feature_names[top_idx]

    # Sort by value for waterfall order
    order = np.argsort(selected_vals)
    selected_vals = selected_vals[order]
    selected_names = selected_names[order]

    cumulative = np.cumsum(selected_vals)
    starts = np.concatenate([[base_value], base_value + cumulative[:-1]])

    colors = ["#2ecc71" if v > 0 else "#e74c3c" for v in selected_vals]

    fig, ax = plt.subplots(figsize=(10, max(6, top_n * 0.5 + 1)))
    fig.patch.set_facecolor("#131829")
    ax.set_facecolor("#131829")

    for i, (name, val, start, color) in enumerate(
        zip(selected_names, selected_vals, starts, colors)
    ):
        ax.barh(i, val, left=start, color=color, height=0.6, edgecolor="none", alpha=0.85)

    ax.set_yticks(range(len(selected_names)))
    ax.set_yticklabels(selected_names, color="white", fontsize=9)
    ax.set_xlabel("SHAP Value", color="white", fontsize=10)
    ax.set_title("SHAP Waterfall — Feature Contributions", color="white", fontsize=12)
    ax.axvline(0, color="white", linewidth=0.5, alpha=0.4)
    ax.tick_params(colors="white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#333")
    ax.spines["bottom"].set_color("#333")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, facecolor=fig.get_facecolor())

    return fig


# ── Full Explanation Pipeline ─────────────────────────────────────────────────
def explain_resume(
    resume_text: str,
    jd_text: str,
    model,
    vectorizer,
    label_encoder,
    X_train_sample=None,
    top_n: int = 15,
) -> dict:
    """
    End-to-end explanation for a resume against a job description.

    Returns
    -------
    dict with:
        predicted_category, fit_score, cosine_similarity,
        shap_features (positive/negative), shap_figure
    """
    try:
        from feature_extraction import (
            transform_single_text,
            compute_jd_resume_similarity,
            compute_hybrid_relevance,
        )
        from train_model import compute_fit_score
        from narrative import generate_narrative
    except ImportError:
        from src.feature_extraction import (
            transform_single_text,
            compute_jd_resume_similarity,
            compute_hybrid_relevance,
        )
        from src.train_model import compute_fit_score
        from src.narrative import generate_narrative

    # 1. Vectorize
    resume_vec = transform_single_text(resume_text, vectorizer)
    jd_vec = transform_single_text(jd_text, vectorizer)

    # 2. Predict
    pred_label = model.predict(resume_vec)[0]
    pred_proba = model.predict_proba(resume_vec)[0]
    predicted_category = label_encoder.inverse_transform([pred_label])[0]

    # 3. Cosine similarity
    cosine_sim = compute_jd_resume_similarity(resume_text, jd_text, vectorizer)

    # 4. Hybrid JD relevance (combining TF-IDF coverage + Semantic similarity)
    hybrid_result = compute_hybrid_relevance(resume_text, jd_text, vectorizer)

    # 5. Fit score — combines Hybrid Relevance and Category Alignment
    fit_score, category_alignment = compute_fit_score(
        model, resume_vec, jd_vec,
        jd_relevance=hybrid_result["relevance"],
        resume_pred_label=pred_label,
    )

    # 6. Keyword matching & Categorized Skills
    keyword_match = {
        "matched": hybrid_result["matched"][:20],
        "missing": hybrid_result["missing"][:20],
    }
    categorized_skills = hybrid_result.get("categorized_skills", {})

    # 7. SHAP explanation
    feature_names = np.array(vectorizer.get_feature_names_out())
    shap_features = {"positive": [], "negative": []}
    shap_fig = None
    waterfall_fig = None
    shap_error = None

    try:
        explainer = get_shap_explainer(model, X_train_sample)
        shap_vals = compute_shap_values(explainer, resume_vec, predicted_class_idx=pred_label)
        shap_features = get_top_shap_features(shap_vals, feature_names, top_n=top_n)
        shap_fig = plot_shap_bar(shap_features, predicted_category, fit_score)

        # Base value for waterfall
        base_val = explainer.expected_value
        if isinstance(base_val, (list, np.ndarray)):
            base_val = base_val[pred_label]
        waterfall_fig = plot_shap_waterfall(shap_vals, feature_names, base_val, top_n=top_n)

    except Exception as e:
        shap_error = f"{type(e).__name__}: {e}"
        logger.warning(f"Explanation failed: {e}")
        logger.warning(traceback.format_exc())

    narrative_input = {
        "fit_score": fit_score,
        "jd_relevance": round(hybrid_result["relevance"] * 100, 1),
        "category_alignment": round(category_alignment * 100, 1),
        "predicted_category": predicted_category,
        "matched_keywords": keyword_match.get("matched", []),
        "missing_keywords": keyword_match.get("missing", []),
        "shap_features": shap_features,
    }
    narrative = generate_narrative(narrative_input, resume_text=resume_text)

    return {
        "predicted_category": predicted_category,
        "fit_score": fit_score,
        "jd_relevance": round(hybrid_result["relevance"] * 100, 1),
        "lexical_relevance": round(hybrid_result.get("lexical_relevance", 0.0) * 100, 1),
        "semantic_similarity": round(hybrid_result.get("semantic_similarity", 0.0) * 100, 1),
        "category_alignment": round(category_alignment * 100, 1),
        "cosine_similarity": round(cosine_sim * 100, 1),
        "confidence": round(float(pred_proba.max()) * 100, 1),
        "all_proba": {
            label_encoder.inverse_transform([i])[0]: round(float(p) * 100, 1)
            for i, p in enumerate(pred_proba)
        },
        "matched_keywords": keyword_match.get("matched", []),
        "missing_keywords": keyword_match.get("missing", []),
        "categorized_skills": categorized_skills,
        "shap_features": shap_features,
        "shap_figure": shap_fig,
        "waterfall_figure": waterfall_fig,
        "narrative": narrative,
        "shap_error": shap_error,
    }



# ── Demo / Test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    # Reconfigure stdout to UTF-8 so emoji/unicode prints don't crash on Windows cp1252
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Load artifacts
    model_path = "models/classifier_model.pkl"
    vectorizer_path = "models/tfidf_vectorizer.pkl"
    le_path = "models/label_encoder.pkl"

    if not all(os.path.exists(p) for p in [model_path, vectorizer_path, le_path]):
        logger.error("Models not found. Run the full pipeline first:\n"
                     "  python src/data_preprocessing.py\n"
                     "  python src/feature_extraction.py\n"
                     "  python src/train_model.py")
        exit(1)

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    le = joblib.load(le_path)

    sample_resume = (
        "Experienced data scientist with 4 years of experience in Python, "
        "machine learning, scikit-learn, TensorFlow, NLP, pandas, and SQL. "
        "Built classification models, recommendation systems, and dashboards."
    )
    sample_jd = (
        "We are looking for an HR Business Partner to manage employee relations, "
        "onboarding, performance management, and compensation planning. "
        "Experience with HRIS systems and labor law compliance required."
    )

    result = explain_resume(sample_resume, sample_jd, model, vectorizer, le)

    print(f"\n{'='*50}")
    print(f"Predicted Category : {result['predicted_category']}")
    print(f"Fit Score          : {result['fit_score']}%")
    print(f"Cosine Similarity  : {result['cosine_similarity']}%")
    print(f"Model Confidence   : {result['confidence']}%")
    print(f"\nMatched Keywords   : {[k for k, _ in result['matched_keywords'][:5]]}")
    print(f"Missing Keywords   : {[k for k, _ in result['missing_keywords'][:5]]}")
    print(f"\nTop Positive SHAP  : {result['shap_features']['positive'][:5]}")
    print(f"\nTop Negative SHAP  : {result['shap_features']['negative'][:5]}")
    print(f"\n{'-'*50}")
    n = result.get("narrative", {})
    print(f"VERDICT     : {n.get('verdict', '')}")
    print(f"STRENGTHS   : {n.get('strengths', '')}")
    print(f"GAPS        : {n.get('gaps', '')}")
    print(f"SUGGESTIONS : {n.get('suggestions', '')}")

    if result["shap_figure"]:
        result["shap_figure"].savefig("data/shap_demo.png", dpi=150, facecolor="#131829")
        print("SHAP plot saved: data/shap_demo.png")

    print("[DONE] Explanation complete!")
