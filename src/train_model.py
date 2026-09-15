"""
train_model.py
--------------
Day 5-7: Train a Logistic Regression classifier on TF-IDF resume features.
Evaluates accuracy, precision/recall, and confusion matrix.
Saves the trained model and label encoder.

Usage:
    python src/train_model.py
"""

import os
import logging
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ── Model Definitions ─────────────────────────────────────────────────────────
def get_logistic_regression() -> LogisticRegression:
    """
    Primary classifier: Logistic Regression with L2 regularization.
    Works well with sparse TF-IDF features, fast, interpretable.
    """
    return LogisticRegression(
        C=5.0,               # Regularization strength (lower = stronger reg)
        max_iter=1000,
        solver="lbfgs",      # handles multi-class natively in sklearn >= 1.5
        n_jobs=-1,
        random_state=42,
    )


def get_random_forest() -> RandomForestClassifier:
    """Secondary classifier for comparison during viva."""
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        n_jobs=-1,
        random_state=42,
    )


# ── Training ──────────────────────────────────────────────────────────────────
def train_model(
    X_train,
    y_train,
    model_type: str = "logistic_regression",
):
    """
    Train the specified model on TF-IDF features.

    Parameters
    ----------
    X_train : sparse matrix or array
    y_train : array of integer labels
    model_type : 'logistic_regression' or 'random_forest'

    Returns trained model.
    """
    if model_type == "logistic_regression":
        model = get_logistic_regression()
    elif model_type == "random_forest":
        model = get_random_forest()
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    logger.info(f"Training {model_type}...")
    model.fit(X_train, y_train)
    logger.info("Training complete.")
    return model


# ── Evaluation ────────────────────────────────────────────────────────────────
def evaluate_model(
    model,
    X_test,
    y_test,
    class_names: list,
    output_dir: str = "data",
) -> dict:
    """
    Evaluate model and save confusion matrix plot.

    Returns
    -------
    dict with accuracy, classification report, confusion matrix
    """
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=class_names)
    cm = confusion_matrix(y_test, y_pred)

    logger.info(f"\n{'='*50}")
    logger.info(f"Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    logger.info(f"\nClassification Report:\n{report}")

    # Save confusion matrix plot
    _save_confusion_matrix(cm, class_names, output_dir)

    return {
        "accuracy": acc,
        "classification_report": report,
        "confusion_matrix": cm,
        "y_pred": y_pred,
    }


def _save_confusion_matrix(cm: np.ndarray, class_names: list, output_dir: str):
    """Save a styled confusion matrix heatmap."""
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(max(8, len(class_names)), max(6, len(class_names) - 2)))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax,
    )
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Actual", fontsize=12)
    ax.set_title("Confusion Matrix — Resume Category Classifier", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    save_path = os.path.join(output_dir, "confusion_matrix.png")
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info(f"Confusion matrix saved: {save_path}")


# ── Fit Score ─────────────────────────────────────────────────────────────────
def compute_category_alignment(model, resume_pred_label: int, jd_tfidf) -> float:
    """
    Measures whether the JD itself 'reads like' the same category as the resume.

    We run the JD text through the SAME category classifier used on resumes,
    then check how much probability mass it assigns to the resume's predicted
    category. If the resume is classified 'Java Developer' but the JD reads
    almost entirely as 'HR', this returns a low number — a clear, explainable
    signal that the resume doesn't belong to this job's category at all,
    independent of any keyword overlap.

    Returns
    -------
    float in [0, 1]
    """
    jd_proba = model.predict_proba(jd_tfidf)[0]
    return float(jd_proba[resume_pred_label])


def compute_fit_score(
    model: LogisticRegression,
    resume_tfidf,
    jd_tfidf,
    jd_relevance: float,
    resume_pred_label: int,
    relevance_weight: float = 0.65,
    alignment_weight: float = 0.35,
) -> tuple:
    """
    Composite fit score combining:
    - JD Relevance (65%): weighted coverage of JD keywords in the resume
      (see feature_extraction.compute_jd_relevance) — the primary signal,
      since it directly measures overlap with THIS job description.
    - Category Alignment (35%): whether the JD itself classifies into the
      resume's predicted category — a sanity check that catches wrong-category
      resumes even when a few keywords coincidentally overlap.

    This replaces the old formula, which mixed in raw category-classification
    CONFIDENCE (how sure the model is about the resume's category in isolation)
    — a number that has nothing to do with fit against a specific JD.

    Returns
    -------
    (fit_score, category_alignment) : (float 0-100, float 0-1)
    """
    category_alignment = compute_category_alignment(model, resume_pred_label, jd_tfidf)

    raw_score = (relevance_weight * jd_relevance) + (alignment_weight * category_alignment)
    fit_score = round(min(max(raw_score * 100, 0), 100), 1)
    return fit_score, category_alignment


# ── Save / Load ───────────────────────────────────────────────────────────────
def save_model(model, path: str = "models/classifier_model.pkl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    logger.info(f"Model saved: {path}")


def load_model(path: str = "models/classifier_model.pkl"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at: {path}. Run train_model.py first.")
    return joblib.load(path)


# ── Main ──────────────────────────────────────────────────────────────────────
def run_training(models_dir: str = "models", data_dir: str = "data"):
    """End-to-end training pipeline."""

    # Load TF-IDF matrices
    X_train_path = os.path.join(models_dir, "X_train_tfidf.pkl")
    X_test_path = os.path.join(models_dir, "X_test_tfidf.pkl")

    if not os.path.exists(X_train_path):
        logger.error(
            "TF-IDF matrices not found. Run feature_extraction.py first:\n"
            "  python src/feature_extraction.py"
        )
        return

    X_train = joblib.load(X_train_path)
    X_test = joblib.load(X_test_path)

    # Load labels
    train_df = pd.read_csv(os.path.join(data_dir, "train.csv"))
    test_df = pd.read_csv(os.path.join(data_dir, "test.csv"))
    y_train = train_df["label"].values
    y_test = test_df["label"].values

    # Load label encoder for class names
    le = joblib.load(os.path.join(models_dir, "label_encoder.pkl"))
    class_names = list(le.classes_)

    # ── Train ──────────────────────────────────────────────────────────────
    model = train_model(X_train, y_train, model_type="logistic_regression")

    # ── Evaluate ───────────────────────────────────────────────────────────
    results = evaluate_model(model, X_test, y_test, class_names, output_dir=data_dir)

    # ── Save model ─────────────────────────────────────────────────────────
    save_model(model, path=os.path.join(models_dir, "classifier_model.pkl"))

    logger.info("✅ Training pipeline complete!")
    logger.info(f"   Final Accuracy: {results['accuracy']*100:.2f}%")
    return model, results


if __name__ == "__main__":
    run_training()
