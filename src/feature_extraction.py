"""
feature_extraction.py
---------------------
Day 3-4: Build TF-IDF vectors from the cleaned resume data.
Fits the vectorizer on training data, transforms both train/test sets,
saves the vectorizer, and analyzes top keywords per category.

Usage:
    python src/feature_extraction.py
"""

import os
import logging
import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ── TF-IDF Vectorizer ─────────────────────────────────────────────────────────
def build_tfidf_vectorizer(
    max_features: int = 10000,
    ngram_range: tuple = (1, 2),
    min_df: int = 2,
    max_df: float = 0.9,
    sublinear_tf: bool = True,
) -> TfidfVectorizer:
    """
    Create a TF-IDF vectorizer with sensible defaults for resume text.

    Parameters
    ----------
    max_features : int
        Maximum number of features (vocabulary size).
    ngram_range : tuple
        (1,2) captures unigrams + bigrams (e.g. 'machine learning' as one feature).
    min_df : int
        Ignore terms appearing in fewer than this many documents.
    max_df : float
        Ignore terms appearing in more than this fraction of documents.
    sublinear_tf : bool
        Apply log normalization to term frequency (reduces impact of very frequent terms).
    """
    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
        sublinear_tf=sublinear_tf,
        strip_accents="unicode",
        analyzer="word",
        token_pattern=r"\b[a-zA-Z][a-zA-Z0-9]{1,}\b",  # words ≥ 2 chars starting with letter
    )


def fit_and_transform(
    train_texts: list,
    test_texts: list,
    vectorizer: TfidfVectorizer = None,
    save_path: str = "models/tfidf_vectorizer.pkl",
) -> tuple:
    """
    Fit TF-IDF on training data, transform both splits.
    Saves the fitted vectorizer to disk.

    Returns
    -------
    (X_train_tfidf, X_test_tfidf, vectorizer)
    """
    if vectorizer is None:
        vectorizer = build_tfidf_vectorizer()

    logger.info("Fitting TF-IDF vectorizer on training data...")
    X_train = vectorizer.fit_transform(train_texts)
    X_test = vectorizer.transform(test_texts)

    vocab_size = len(vectorizer.vocabulary_)
    logger.info(f"Vocabulary size: {vocab_size:,}")
    logger.info(f"Train matrix shape: {X_train.shape}")
    logger.info(f"Test matrix shape:  {X_test.shape}")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(vectorizer, save_path)
    logger.info(f"Vectorizer saved: {save_path}")

    return X_train, X_test, vectorizer


def transform_single_text(text: str, vectorizer: TfidfVectorizer):
    """
    Transform a single text (resume or job description) using a fitted vectorizer.
    Returns a sparse matrix of shape (1, n_features).
    """
    return vectorizer.transform([text])


# ── Vocabulary Analysis ───────────────────────────────────────────────────────
def get_top_keywords_per_category(
    df: pd.DataFrame,
    vectorizer: TfidfVectorizer,
    text_col: str = "cleaned_resume",
    label_col: str = "Category",
    top_n: int = 20,
) -> dict:
    """
    For each job category, find the top-N TF-IDF keywords by mean TF-IDF score.
    Useful for understanding what words define each category.

    Returns
    -------
    dict  {category: [(word, score), ...]}
    """
    feature_names = np.array(vectorizer.get_feature_names_out())
    result = {}

    for category in df[label_col].unique():
        mask = df[label_col] == category
        texts = df.loc[mask, text_col].tolist()
        if not texts:
            continue
        tfidf_matrix = vectorizer.transform(texts)
        mean_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
        top_indices = mean_scores.argsort()[::-1][:top_n]
        top_words = [(feature_names[i], round(mean_scores[i], 4)) for i in top_indices]
        result[category] = top_words

    return result


def compute_jd_resume_similarity(
    resume_text: str,
    jd_text: str,
    vectorizer: TfidfVectorizer,
) -> float:
    """
    Compute cosine similarity between a resume and a job description
    using TF-IDF vectors.

    Returns
    -------
    float: similarity score in [0, 1]
    """
    from sklearn.metrics.pairwise import cosine_similarity

    resume_vec = vectorizer.transform([resume_text])
    jd_vec = vectorizer.transform([jd_text])
    score = cosine_similarity(resume_vec, jd_vec)[0][0]
    return float(score)


def get_matching_keywords(
    resume_text: str,
    jd_text: str,
    vectorizer: TfidfVectorizer,
    top_n: int = 20,
) -> dict:
    """
    Find keywords from the JD that appear in the resume (matched)
    and important JD keywords missing from the resume (missing).

    Returns
    -------
    dict with 'matched' and 'missing' lists of (keyword, jd_tfidf_score)
    """
    feature_names = np.array(vectorizer.get_feature_names_out())

    resume_vec = vectorizer.transform([resume_text]).toarray().flatten()
    jd_vec = vectorizer.transform([jd_text]).toarray().flatten()

    # Get top-N JD keywords by TF-IDF score
    top_jd_indices = jd_vec.argsort()[::-1][:top_n]
    top_jd_keywords = {
        feature_names[i]: jd_vec[i]
        for i in top_jd_indices
        if jd_vec[i] > 0
    }

    matched = []
    missing = []
    for word, score in top_jd_keywords.items():
        # Check if this word appears in resume vector
        word_idx = np.where(feature_names == word)[0]
        if len(word_idx) > 0 and resume_vec[word_idx[0]] > 0:
            matched.append((word, round(score, 4)))
        else:
            missing.append((word, round(score, 4)))

    return {"matched": matched, "missing": missing}

def compute_jd_relevance(resume_text, jd_text, vectorizer):
    """
    Weighted relevance score: for every term present in the JD, weighted by
    its TF-IDF importance WITHIN the JD, check whether it's present in the
    resume. This means missing a heavily-emphasized JD term (e.g. a required
    skill mentioned several times) hurts the score more than missing an
    incidental one — unlike a flat matched/total keyword count.

    Returns
    -------
    dict with:
        'relevance': float in [0, 1]
        'matched':  [(word, jd_weight), ...] sorted by importance, descending
        'missing':  [(word, jd_weight), ...] sorted by importance, descending
    """
    feature_names = np.array(vectorizer.get_feature_names_out())
    resume_vec = vectorizer.transform([resume_text]).toarray().flatten()
    jd_vec = vectorizer.transform([jd_text]).toarray().flatten()

    jd_nonzero_idx = np.where(jd_vec > 0)[0]
    if len(jd_nonzero_idx) == 0:
        return {"relevance": 0.0, "matched": [], "missing": []}

    matched, missing = [], []
    matched_weight, missing_weight = 0.0, 0.0

    for idx in jd_nonzero_idx:
        weight = float(jd_vec[idx])
        word = feature_names[idx]
        if resume_vec[idx] > 0:
            matched_weight += weight
            matched.append((word, round(weight, 4)))
        else:
            missing_weight += weight
            missing.append((word, round(weight, 4)))

    total_weight = matched_weight + missing_weight
    relevance = matched_weight / total_weight if total_weight > 0 else 0.0

    matched.sort(key=lambda x: -x[1])
    missing.sort(key=lambda x: -x[1])

    return {"relevance": relevance, "matched": matched, "missing": missing}

# ── Main ──────────────────────────────────────────────────────────────────────
def run_feature_extraction(
    data_dir: str = "data",
    models_dir: str = "models",
):
    """End-to-end feature extraction pipeline."""
    train_path = os.path.join(data_dir, "train.csv")
    test_path = os.path.join(data_dir, "test.csv")
    cleaned_path = os.path.join(data_dir, "cleaned_resumes.csv")

    if not os.path.exists(train_path):
        logger.error(
            "train.csv not found. Run data_preprocessing.py first:\n"
            "  python src/data_preprocessing.py"
        )
        return

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    full_df = pd.read_csv(cleaned_path)

    X_train_raw = train_df["text"].tolist()
    X_test_raw = test_df["text"].tolist()

    # Fit and transform
    vectorizer_path = os.path.join(models_dir, "tfidf_vectorizer.pkl")
    X_train_tfidf, X_test_tfidf, vectorizer = fit_and_transform(
        X_train_raw, X_test_raw, save_path=vectorizer_path
    )

    # Save transformed matrices
    joblib.dump(X_train_tfidf, os.path.join(models_dir, "X_train_tfidf.pkl"))
    joblib.dump(X_test_tfidf, os.path.join(models_dir, "X_test_tfidf.pkl"))
    logger.info("Saved TF-IDF matrices.")

    # Save a SHAP background sample from THIS SAME fit -- must be regenerated
    # any time the vectorizer changes, or SHAP explanations will fail with a
    # feature-count mismatch against a stale sample.
    sample_size = min(200, X_train_tfidf.shape[0])
    sample_idx = np.random.RandomState(42).choice(X_train_tfidf.shape[0], sample_size, replace=False)
    joblib.dump(X_train_tfidf[sample_idx], os.path.join(data_dir, "X_train_sample.pkl"))
    logger.info("Saved SHAP background sample: %s", os.path.join(data_dir, "X_train_sample.pkl"))

    # Analyze top keywords
    logger.info("\n── Top Keywords Per Category ──────────────────────────────")
    top_keywords = get_top_keywords_per_category(full_df, vectorizer)
    for category, keywords in top_keywords.items():
        top5 = ", ".join([f"{w}({s})" for w, s in keywords[:5]])
        logger.info(f"  {category}: {top5}")

    logger.info("✅ Feature extraction complete!")
    return X_train_tfidf, X_test_tfidf, vectorizer


if __name__ == "__main__":
    run_feature_extraction()
