"""
app.py -- HireLens.AI: AI-Powered Resume Screening & Job-Fit Classifier
----------------------------------------------------------------------
Streamlit web application with Batch Screening, Hybrid Semantic Matching,
Blind Screening (PII Redaction), and Tailored Interview Question Generation.

Run with:
    streamlit run app.py
"""

import os
import sys
import io
import re
import html
import logging
import numpy as np
import pandas as pd
import joblib
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Allow imports from src/
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.data_preprocessing import clean_resume_text, anonymize_resume_text
from src.explain import explain_resume

# -- Page Config --------------------------------------------------------------
st.set_page_config(
    page_title="HireLens.AI - Smart Resume Screener",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Design Tokens ------------------------------------------------------------
ACCENT = "#818cf8"
ACCENT_2 = "#a78bfa"
CARD_BG = "rgba(255,255,255,0.03)"
CARD_BORDER = "rgba(255,255,255,0.08)"
GOOD = "#4ade80"
WARN = "#fbbf24"
BAD = "#f87171"

# -- Custom CSS ----------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0d0d1a 0%, #0f1524 50%, #0a0e1a 100%);
    }

    [data-testid="stSidebar"] {
        background: rgba(13, 17, 28, 0.97);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px 22px;
    }

    .card-accent-left {
        border-left: 3px solid #818cf8;
    }

    .section-header {
        font-size: 0.92rem;
        font-weight: 700;
        color: rgba(255,255,255,0.75);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 22px 0 10px 0;
    }

    .verdict-text {
        font-size: 1.12rem;
        line-height: 1.6;
        color: rgba(255,255,255,0.94);
        font-weight: 500;
    }

    .narrative-block {
        font-size: 0.93rem;
        line-height: 1.65;
        color: rgba(255,255,255,0.75);
        margin-top: 8px;
    }

    .narrative-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 14px;
        display: block;
    }
    .label-strengths { color: #4ade80; }
    .label-gaps { color: #f87171; }
    .label-suggestions { color: #fbbf24; }

    .stat-row {
        display: flex;
        gap: 24px;
        flex-wrap: wrap;
        margin-top: 14px;
    }
    .stat-item {
        display: flex;
        flex-direction: column;
    }
    .stat-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: rgba(255,255,255,0.9);
    }
    .stat-label {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.42);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 2px;
    }

    .keyword-pill-green {
        display: inline-block;
        background: rgba(74, 222, 128, 0.12);
        border: 1px solid rgba(74, 222, 128, 0.3);
        color: #4ade80;
        border-radius: 20px;
        padding: 3px 11px;
        margin: 3px 4px;
        font-size: 0.78rem;
        font-weight: 500;
    }

    .keyword-pill-red {
        display: inline-block;
        background: rgba(248, 113, 113, 0.1);
        border: 1px solid rgba(248, 113, 113, 0.28);
        color: #f87171;
        border-radius: 20px;
        padding: 3px 11px;
        margin: 3px 4px;
        font-size: 0.78rem;
        font-weight: 500;
    }

    .skill-chip-missing {
        display: inline-block;
        background: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.3);
        color: #fbbf24;
        border-radius: 8px;
        padding: 5px 14px;
        margin: 4px 5px 4px 0;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .skill-chip-present {
        display: inline-block;
        background: rgba(74, 222, 128, 0.08);
        border: 1px solid rgba(74, 222, 128, 0.22);
        color: rgba(74, 222, 128, 0.75);
        border-radius: 8px;
        padding: 5px 14px;
        margin: 4px 5px 4px 0;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .badge-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }

    .badge-blind {
        background: rgba(167, 139, 250, 0.15);
        color: #c4b5fd;
        border: 1px solid rgba(167, 139, 250, 0.3);
    }

    .badge-semantic {
        background: rgba(56, 189, 248, 0.15);
        color: #7dd3fc;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }


    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #818cf8, #a78bfa);
        border-radius: 10px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #818cf8, #a78bfa);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 0.95rem;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 4px 18px rgba(129, 140, 248, 0.25);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(129, 140, 248, 0.38);
    }

    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: rgba(255,255,255,0.9) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: rgba(255,255,255,0.55);
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(129, 140, 248, 0.18) !important;
        color: #c4b5fd !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# -- Helpers & Model Loading ---------------------------------------------------
@st.cache_resource(show_spinner="Loading AI models...")
def load_models():
    """Load all models and artifacts. Cached so they load only once."""
    model_path = "models/classifier_model.pkl"
    vectorizer_path = "models/tfidf_vectorizer.pkl"
    le_path = "models/label_encoder.pkl"
    train_path = "data/X_train_sample.pkl"

    missing = [p for p in [model_path, vectorizer_path, le_path] if not os.path.exists(p)]
    if missing:
        return None, None, None, None

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    le = joblib.load(le_path)
    X_train_sample = joblib.load(train_path) if os.path.exists(train_path) else None

    return model, vectorizer, le, X_train_sample


def extract_text_from_pdf(file) -> str:
    """Extract text from an uploaded PDF file with pdfplumber and PyPDF2 fallback."""
    # Attempt 1: pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        if text.strip():
            return text.strip()
    except Exception:
        pass

    # Attempt 2: PyPDF2 fallback
    try:
        import importlib
        pypdf_module = importlib.import_module("PyPDF2")
        file.seek(0)
        reader = pypdf_module.PdfReader(file)
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text).strip()
    except Exception as e:
        st.error(f"PDF extraction failed: {e}")
        return ""


def extract_text_from_docx(file) -> str:
    """Extract text from an uploaded DOCX file."""
    try:
        from docx import Document
        doc = Document(file)
        text = "\n".join(para.text for para in doc.paragraphs)
        return text.strip()
    except Exception as e:
        st.error(f"DOCX extraction failed: {e}")
        return ""


def extract_file_text(file) -> str:
    """Detect file type and extract textual content."""
    fname = file.name.lower()
    if fname.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif fname.endswith(".docx"):
        return extract_text_from_docx(file)
    elif fname.endswith(".txt"):
        try:
            return file.read().decode("utf-8", errors="ignore").strip()
        except Exception:
            return ""
    return ""


def score_color(score: float) -> str:
    if score >= 70:
        return GOOD
    elif score >= 45:
        return WARN
    else:
        return BAD


def score_label(score: float) -> str:
    if score >= 75:
        return "Excellent Match"
    elif score >= 55:
        return "Good Match"
    elif score >= 35:
        return "Partial Match"
    else:
        return "Weak Match"


def render_gauge(score: float):
    """Render an SVG circular gauge for the fit score."""
    color = score_color(score)
    pct = score / 100
    circ = 376.99
    dash = circ * pct
    gap = circ - dash

    svg = f"""
    <div style="display:flex;justify-content:center;align-items:center;margin:4px 0;">
    <svg width="168" height="168" viewBox="0 0 180 180">
        <circle cx="90" cy="90" r="60" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="12"/>
        <circle cx="90" cy="90" r="60" fill="none"
                stroke="{color}" stroke-width="12"
                stroke-dasharray="{dash:.2f} {gap:.2f}"
                stroke-linecap="round"
                transform="rotate(-90 90 90)"/>
        <text x="90" y="85" text-anchor="middle" font-size="28" font-weight="700"
              fill="{color}" font-family="Inter, sans-serif">{score:.0f}%</text>
        <text x="90" y="108" text-anchor="middle" font-size="11"
              fill="rgba(255,255,255,0.45)" font-family="Inter, sans-serif">Fit Score</text>
    </svg>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)


def render_interview_questions(questions: list):
    """Render recommended technical interview questions card."""
    if not questions:
        return
    st.markdown('<div class="section-header">🎯 Recommended Interview Questions</div>', unsafe_allow_html=True)
    q_html = '<div class="card" style="margin-bottom:14px;">'
    q_html += '<div style="font-size:0.82rem;color:rgba(255,255,255,0.5);margin-bottom:12px;">Targeted technical questions to probe detected skill gaps during screening calls:</div>'
    for i, q in enumerate(questions, 1):
        skill_name = q.get("skill", "")
        category = q.get("category", "")
        q_text = q.get("question", "")
        q_html += f"""
        <div style="background:rgba(255,255,255,0.02);border-left:3px solid #818cf8;border-radius:8px;padding:12px 14px;margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <span style="font-size:0.75rem;font-weight:700;color:#a78bfa;text-transform:uppercase;letter-spacing:0.05em;">{i}. {category}</span>
                <span style="font-size:0.72rem;background:rgba(248,113,113,0.15);color:#f87171;border:1px solid rgba(248,113,113,0.3);padding:2px 8px;border-radius:12px;">Missing: {skill_name}</span>
            </div>
            <div style="font-size:0.9rem;color:rgba(255,255,255,0.9);line-height:1.5;">"{q_text}"</div>
        </div>
        """
    q_html += '</div>'
    st.markdown(q_html, unsafe_allow_html=True)


def render_categorized_skills(categorized_skills: dict):
    """Render categorized skills breakdown."""
    if not categorized_skills:
        return
    st.markdown('<div class="section-header">📊 Skills Competency Breakdown</div>', unsafe_allow_html=True)
    c_html = '<div class="card" style="margin-bottom:14px;"><div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:14px;">'
    for category, groups in categorized_skills.items():
        matched = groups.get("matched", [])
        missing = groups.get("missing", [])
        c_html += f"""
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:12px 14px;">
            <div style="font-size:0.8rem;font-weight:700;color:rgba(255,255,255,0.85);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.04em;">{category}</div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.4);margin-bottom:4px;">Matched ({len(matched)})</div>
            <div style="margin-bottom:8px;">
        """
        if matched:
            for w, _ in matched:
                c_html += f'<span class="keyword-pill-green" style="font-size:0.75rem;padding:2px 8px;">{w}</span> '
        else:
            c_html += '<span style="color:rgba(255,255,255,0.3);font-size:0.75rem;">None</span>'

        c_html += f"""
            </div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.4);margin-bottom:4px;">Missing ({len(missing)})</div>
            <div>
        """
        if missing:
            for w, _ in missing:
                c_html += f'<span class="keyword-pill-red" style="font-size:0.75rem;padding:2px 8px;">{w}</span> '
        else:
            c_html += '<span style="color:#4ade80;font-size:0.75rem;">All present!</span>'

        c_html += '</div></div>'

    c_html += '</div></div>'
    st.markdown(c_html, unsafe_allow_html=True)


def render_highlighted_resume(resume_text: str, matched_keywords: list) -> str:
    """Highlight matched keywords in the resume text."""
    escaped = html.escape(resume_text)
    words = sorted([w for w, _ in matched_keywords], key=lambda x: len(x), reverse=True)
    for word in words:
        if len(word) > 2:
            pattern = re.compile(rf"\b({re.escape(word)})\b", re.IGNORECASE)
            escaped = pattern.sub(
                r'<mark style="background:rgba(74,222,128,0.25);color:#4ade80;font-weight:600;padding:2px 5px;border-radius:4px;border:1px solid rgba(74,222,128,0.4);">\1</mark>',
                escaped,
            )
    return f'<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px;max-height:420px;overflow-y:auto;font-family:monospace;font-size:0.86rem;line-height:1.6;white-space:pre-wrap;color:rgba(255,255,255,0.85);">{escaped}</div>'


def run_training_pipeline():
    """Run the full training pipeline with a progress bar."""
    from src.data_preprocessing import download_nltk_resources, load_and_preprocess
    from src.feature_extraction import run_feature_extraction
    from src.train_model import run_training

    progress = st.progress(0, text="Downloading resources...")
    download_nltk_resources()

    progress.progress(20, text="Preprocessing data...")
    load_and_preprocess()

    progress.progress(50, text="Extracting TF-IDF & Semantic features...")
    X_train_tfidf, X_test_tfidf, _ = run_feature_extraction()

    sample_size = min(200, X_train_tfidf.shape[0])
    idx = np.random.choice(X_train_tfidf.shape[0], sample_size, replace=False)
    joblib.dump(X_train_tfidf[idx], "data/X_train_sample.pkl")

    progress.progress(75, text="Training classifier...")
    run_training()

    progress.progress(100, text="Training complete!")
    st.cache_resource.clear()
    st.success("Models trained and saved successfully!")


# -- Sidebar ------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center;padding:16px 0 10px">
                <div style="font-size:2.2rem;">🎯</div>
                <div style="font-size:1.3rem;font-weight:700;color:rgba(255,255,255,0.95);">
                    HireLens.AI
                </div>
                <div style="font-size:0.76rem;color:rgba(255,255,255,0.45);margin-top:2px;">
                    Explainable AI Recruitment Intelligence
                </div>
            </div>
            <hr style="border-color:rgba(255,255,255,0.08);margin:10px 0 14px 0;">
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Screening Mode")
        mode = st.radio(
            "Select Mode",
            ["Single Candidate", "Batch Screening (Leaderboard)"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("### Bias Mitigation")
        blind_mode = st.toggle(
            "🛡️ Blind Screening Mode",
            value=False,
            help="Automatically redacts candidate names, emails, phone numbers, and profile URLs to ensure unbiased evaluation.",
        )
        if blind_mode:
            st.caption("PII will be automatically masked in reports.")

        st.markdown("---")
        st.markdown("### Resume Source")

        single_resume_text = ""
        batch_files = []

        if mode == "Single Candidate":
            input_method = st.radio(
                "Input Type",
                ["Upload PDF/DOCX", "Paste Text"],
                key="single_input_method",
            )
            if input_method == "Upload PDF/DOCX":
                uploaded_file = st.file_uploader(
                    "Upload Resume",
                    type=["pdf", "docx", "txt"],
                    help="Supports PDF, DOCX, and TXT",
                    key="single_file",
                )
                if uploaded_file:
                    single_resume_text = extract_file_text(uploaded_file)
                    if single_resume_text:
                        st.success(f"Loaded: {uploaded_file.name} ({len(single_resume_text.split())} words)")
            else:
                single_resume_text = st.text_area(
                    "Paste Resume Text",
                    height=180,
                    placeholder="Paste the candidate's resume here...",
                    key="single_paste",
                )
        else:
            batch_files = st.file_uploader(
                "Upload Multiple Resumes",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True,
                help="Upload multiple candidate resumes for comparative ranking.",
                key="batch_files_uploader",
            )
            if batch_files:
                st.info(f"{len(batch_files)} resumes ready for batch screening.")

        st.markdown("---")
        st.markdown("### AI Models Status")
        model, vectorizer, le, X_train_sample = load_models()
        if model is not None:
            st.success("Models Active")
            st.markdown(
                f"<div style='font-size:0.75rem;color:rgba(255,255,255,0.45);'>"
                f"Categories: {len(le.classes_)} domains loaded"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("Models not initialized")
            if st.button("Train Models Now", key="train_btn"):
                with st.spinner("Training models..."):
                    try:
                        run_training_pipeline()
                    except Exception as e:
                        st.error(f"Training failed: {e}")

        st.markdown("---")
        st.markdown(
            """
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.3);text-align:center;">
            HireLens.AI &middot; Explainable AI + NLP
            </div>
            """,
            unsafe_allow_html=True,
        )

    return mode, blind_mode, single_resume_text, batch_files, model, vectorizer, le, X_train_sample


# -- Main App ------------------------------------------------------------------
def main():
    mode, blind_mode, single_resume_text, batch_files, model, vectorizer, le, X_train_sample = render_sidebar()

    # App Header
    st.markdown(
        """
        <div style="padding: 20px 0 14px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <h1 style="font-size:2.2rem;font-weight:800;margin:0;
                    background:linear-gradient(90deg,#818cf8,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    display:inline-block;">
                    HireLens.AI
                </h1>
                <span class="badge-tag badge-semantic">Hybrid AI Engine</span>
            </div>
            <p style="color:rgba(255,255,255,0.5);font-size:0.95rem;margin-top:4px;">
                Intelligent candidate evaluation combining Explainable AI (SHAP), semantic embeddings, and automated interview question generation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Job Description Section (Shared by Single & Batch modes)
    st.markdown('<div class="section-header">Job Description</div>', unsafe_allow_html=True)

    jd_source = st.radio(
        "How would you like to provide the job description?",
        ["Paste Text", "Paste Job Link"],
        key="jd_source",
        horizontal=True,
    )

    if jd_source == "Paste Job Link":
        link_col, btn_col = st.columns([4, 1])
        with link_col:
            jd_url = st.text_input(
                "Job posting URL",
                label_visibility="collapsed",
                placeholder="https://...",
                key="jd_url_input",
            )
        with btn_col:
            fetch_clicked = st.button("Fetch", key="fetch_jd_btn")

        if fetch_clicked:
            if not jd_url.strip():
                st.warning("Paste a job posting URL first.")
            else:
                with st.spinner("Fetching job description..."):
                    from job_fetcher import fetch_job_description_from_url
                    fetch_result = fetch_job_description_from_url(jd_url)

                if fetch_result["success"]:
                    st.session_state["jd_input"] = fetch_result["text"]
                    st.success(fetch_result["message"])
                else:
                    st.warning(fetch_result["message"])
    jd_text = st.text_area(
        label="Job Description",
        label_visibility="collapsed",
        height=140,
        placeholder=(
            "Paste the job description or role requirements here...\n\n"
            "Example: We are seeking a Senior Python Developer with experience in FastAPI, "
            "PostgreSQL, Docker, Kubernetes, microservices architecture, and cloud deployment."
        ),
        key="global_jd_input",
    )

    # ──────────────────────────────────────────────────────────────────────────
    # MODE 1: SINGLE CANDIDATE DEEP DIVE
    # ──────────────────────────────────────────────────────────────────────────
    if mode == "Single Candidate":
        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            analyze_clicked = st.button("Analyze Resume", key="single_analyze_btn")
        with col_info:
            if not single_resume_text:
                st.info("👈 Upload or paste a resume in the sidebar to begin.")
            elif not jd_text:
                st.info("Enter a job description above, then click Analyze.")

        st.markdown("---")

        if analyze_clicked:
            if not single_resume_text:
                st.error("Please provide a resume in the sidebar.")
                return
            if not jd_text.strip():
                st.error("Please enter a job description.")
                return
            if model is None:
                st.error("Models not ready. Click **Train Models Now** in the sidebar.")
                return

            with st.spinner("Analyzing candidate fit & computing explainability..."):
                raw_text_to_use = single_resume_text
                redaction_info = None

                if blind_mode:
                    anon_res = anonymize_resume_text(single_resume_text)
                    raw_text_to_use = anon_res["anonymized_text"]
                    redaction_info = anon_res["redaction_counts"]

                cleaned_resume = clean_resume_text(raw_text_to_use)
                cleaned_jd = clean_resume_text(jd_text)

                if not cleaned_resume:
                    st.error("Could not extract meaningful text from the resume.")
                    return

                result = explain_resume(
                    cleaned_resume,
                    cleaned_jd,
                    model,
                    vectorizer,
                    le,
                    X_train_sample=X_train_sample,
                )

            # Blind mode notification banner
            if blind_mode and redaction_info:
                total_redacted = sum(redaction_info.values())
                st.markdown(
                    f"""
                    <div style="background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.3);border-radius:10px;padding:10px 16px;margin-bottom:14px;font-size:0.85rem;color:#c4b5fd;">
                        🛡️ <b>Blind Screening Active:</b> Redacted {total_redacted} PII elements ({redaction_info['emails']} emails, {redaction_info['phones']} phones, {redaction_info['links']} links, {redaction_info['names']} names) to ensure objective evaluation.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            fit_score = result["fit_score"]
            predicted_cat = result["predicted_category"]
            jd_relevance = result.get("jd_relevance", 0)
            category_alignment = result.get("category_alignment", 0)
            confidence = result["confidence"]
            semantic_sim = result.get("semantic_similarity", 0)
            narrative = result.get("narrative", {})

            # Hero Section: Score Gauge + Recruiter Summary
            st.markdown('<div class="section-header">Evaluation Result</div>', unsafe_allow_html=True)
            hero_col1, hero_col2 = st.columns([1, 2.5])
            with hero_col1:
                render_gauge(fit_score)
                st.markdown(
                    f"""<div style="text-align:center;color:{score_color(fit_score)};
                        font-weight:700;font-size:0.95rem;margin-top:-6px;">
                        {score_label(fit_score)}
                    </div>""",
                    unsafe_allow_html=True,
                )
            with hero_col2:
                st.markdown(
                    f"""
                    <div class="card card-accent-left">
                        <div class="verdict-text">{narrative.get('verdict', '')}</div>
                        <div class="stat-row">
                            <div class="stat-item">
                                <div class="stat-value">{predicted_cat}</div>
                                <div class="stat-label">Predicted Role</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{jd_relevance:.0f}%</div>
                                <div class="stat-label">Hybrid Relevance</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{semantic_sim:.0f}%</div>
                                <div class="stat-label">Semantic Sim</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{category_alignment:.0f}%</div>
                                <div class="stat-label">Category Alignment</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Narrative Card: Strengths / Gaps / Suggestions
            strengths = narrative.get("strengths", "")
            gaps = narrative.get("gaps", "")
            suggestions = narrative.get("suggestions", "")

            narrative_html = f'<div class="card" style="margin-top:14px;">'
            if strengths:
                narrative_html += (
                    f'<span class="narrative-label label-strengths">Key Strengths</span>'
                    f'<div class="narrative-block">{strengths}</div>'
                )
            if gaps:
                narrative_html += (
                    f'<span class="narrative-label label-gaps">Identified Skill Gaps</span>'
                    f'<div class="narrative-block">{gaps}</div>'
                )
            if suggestions:
                narrative_html += (
                    f'<span class="narrative-label label-suggestions">Actionable Recommendation</span>'
                    f'<div class="narrative-block">{suggestions}</div>'
                )
            narrative_html += '</div>'
            st.markdown(narrative_html, unsafe_allow_html=True)

        # -- Skills to Build -- curated, text-matched (independent of the
        # classifier's TF-IDF vocabulary), directly actionable ----------------
        skill_gaps = result.get("skill_gaps", {})
        missing_skills = skill_gaps.get("missing_skills", [])
        present_skills = skill_gaps.get("present_skills", [])

        if missing_skills or present_skills:
            st.markdown('<div class="section-header">Skills to Build</div>', unsafe_allow_html=True)
            skills_html = '<div class="card">'
            if missing_skills:
                skills_html += (
                    '<span class="narrative-label label-gaps">Not yet on the resume</span>'
                    '<div style="margin-top:10px;">'
                    + " ".join(f'<span class="skill-chip-missing">{s}</span>' for s in missing_skills)
                    + "</div>"
                )
            if present_skills:
                skills_html += (
                    '<span class="narrative-label label-strengths" style="margin-top:18px;">Already covered</span>'
                    '<div style="margin-top:10px;">'
                    + " ".join(f'<span class="skill-chip-present">{s}</span>' for s in present_skills)
                    + "</div>"
                )
            skills_html += "</div>"
            st.markdown(skills_html, unsafe_allow_html=True)

        # -- Recommended Technical Interview Questions ------------------------
        interview_questions = narrative.get("interview_questions", [])
        render_interview_questions(interview_questions)

        # -- Categorized Skills Competency Breakdown ---------------------------
        categorized_skills = result.get("categorized_skills", {})
        render_categorized_skills(categorized_skills)

        # -- Diagnostic Evidence -----------------------------------------------
        st.markdown('<div class="section-header">Diagnostic Evidence</div>', unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs([
            "Keywords",
            "SHAP Feature Attribution",
            "Category Probabilities",
            "Resume Text Inspector"
        ])

        with tab1:
            kcol1, kcol2 = st.columns(2)
            with kcol1:
                matched = result.get("matched_keywords", [])
                st.markdown(
                    f'<div class="section-header" style="margin-top:4px;">Matched Skills ({len(matched)})</div>',
                    unsafe_allow_html=True,
                )
                if matched:
                    pills = " ".join(f'<span class="keyword-pill-green">{w}</span>' for w, _ in matched)
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.caption("No direct keyword matches found.")
            with kcol2:
                missing = result.get("missing_keywords", [])
                st.markdown(
                    f'<div class="section-header" style="margin-top:4px;">Missing Requirements ({len(missing)})</div>',
                    unsafe_allow_html=True,
                )
                if missing:
                    pills = " ".join(f'<span class="keyword-pill-red">{w}</span>' for w, _ in missing)
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.caption("All key requirements satisfied!")

            with tab2:
                st.markdown(
                    """
                    <div style="font-size:0.82rem;color:rgba(255,255,255,0.45);margin-bottom:10px;">
                    <b style="color:#4ade80">Green bars</b> -- terms that increased the fit score &nbsp;|&nbsp;
                    <b style="color:#f87171">Red bars</b> -- terms that decreased it
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                shap_fig = result.get("shap_figure")
                waterfall_fig = result.get("waterfall_figure")

                st.markdown('<div class="card">', unsafe_allow_html=True)
                if shap_fig is not None:
                    st.pyplot(shap_fig, use_container_width=True)
                else:
                    st.warning("SHAP figure could not be rendered.")
                st.markdown('</div>', unsafe_allow_html=True)

                if waterfall_fig is not None:
                    st.markdown('<div class="section-header">Cumulative Waterfall Plot</div>', unsafe_allow_html=True)
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.pyplot(waterfall_fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                all_proba = result.get("all_proba", {})
                if all_proba:
                    sorted_proba = sorted(all_proba.items(), key=lambda x: x[1], reverse=True)
                    for cat, prob in sorted_proba[:4]:
                        col_label, col_bar = st.columns([2, 5])
                        with col_label:
                            st.markdown(
                                f'<span style="color:rgba(255,255,255,0.75);font-size:0.85rem;">{cat}</span>',
                                unsafe_allow_html=True,
                            )
                        with col_bar:
                            st.progress(int(prob), text=f"{prob:.1f}%")

            with tab4:
                st.markdown(
                    """
                    <div style="font-size:0.82rem;color:rgba(255,255,255,0.45);margin-bottom:8px;">
                    Extracted resume text with matched JD requirements highlighted in <span style="color:#4ade80;font-weight:600;">green</span>:
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                highlighted_html = render_highlighted_resume(raw_text_to_use, result.get("matched_keywords", []))
                st.markdown(highlighted_html, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────────
    # MODE 2: BATCH SCREENING LEADERBOARD
    # ──────────────────────────────────────────────────────────────────────────
    else:
        st.markdown('<div class="section-header">Batch Candidate Screening</div>', unsafe_allow_html=True)

        col_bbtn, col_binfo = st.columns([1, 3])
        with col_bbtn:
            batch_btn = st.button("Screen All Candidates", key="batch_screen_btn")
        with col_binfo:
            if not batch_files:
                st.info("👈 Upload candidate resumes in the sidebar (supports multiple files).")
            elif not jd_text:
                st.info("Enter a target job description above, then click Screen All Candidates.")

        if batch_btn:
            if not batch_files:
                st.error("Please upload multiple resumes in the sidebar.")
                return
            if not jd_text.strip():
                st.error("Please enter a target job description.")
                return
            if model is None:
                st.error("Models not ready. Click **Train Models Now** in the sidebar.")
                return

            batch_results = []
            progress_bar = st.progress(0, text="Initializing batch screener...")

            cleaned_jd = clean_resume_text(jd_text)

            for i, file in enumerate(batch_files):
                pct = int(((i + 1) / len(batch_files)) * 100)
                progress_bar.progress(pct, text=f"Screening candidate {i+1} of {len(batch_files)} ({file.name})...")

                raw_text = extract_file_text(file)
                if not raw_text.strip():
                    continue

                candidate_label = file.name
                if blind_mode:
                    anon_res = anonymize_resume_text(raw_text)
                    raw_text = anon_res["anonymized_text"]
                    candidate_label = f"Candidate #{i+1:02d}"

                cleaned_resume = clean_resume_text(raw_text)
                if not cleaned_resume:
                    continue

                try:
                    res = explain_resume(
                        cleaned_resume,
                        cleaned_jd,
                        model,
                        vectorizer,
                        le,
                        X_train_sample=X_train_sample,
                    )
                    batch_results.append({
                        "filename": file.name,
                        "candidate": candidate_label,
                        "fit_score": res["fit_score"],
                        "category": res["predicted_category"],
                        "relevance": res["jd_relevance"],
                        "alignment": res["category_alignment"],
                        "matched_count": len(res["matched_keywords"]),
                        "missing_count": len(res["missing_keywords"]),
                        "status": score_label(res["fit_score"]),
                        "verdict": res.get("narrative", {}).get("verdict", ""),
                        "full_res": res,
                        "raw_text": raw_text,
                    })
                except Exception as e:
                    logging.warning(f"Failed to screen {file.name}: {e}")

            progress_bar.empty()
            st.session_state["batch_results"] = batch_results

        # Display Batch Results
        if "batch_results" in st.session_state and st.session_state["batch_results"]:
            results = st.session_state["batch_results"]
            results.sort(key=lambda x: x["fit_score"], reverse=True)

            # Summary Metrics Row
            total_cand = len(results)
            avg_score = np.mean([r["fit_score"] for r in results]) if results else 0
            top_cand = results[0] if results else None
            shortlisted = sum(1 for r in results if r["fit_score"] >= 55)

            st.markdown('<div class="section-header">Candidate Leaderboard</div>', unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total Screened", f"{total_cand} Resumes")
            with m2:
                st.metric("Shortlisted (≥55%)", f"{shortlisted} Candidates")
            with m3:
                st.metric("Average Score", f"{avg_score:.1f}%")
            with m4:
                top_name = top_cand["candidate"] if top_cand else "N/A"
                top_val = f"{top_cand['fit_score']:.1f}%" if top_cand else "0%"
                st.metric("Top Ranked", top_name, top_val)

            # Leaderboard Table Dataframe
            df_rows = []
            for rank, r in enumerate(results, 1):
                df_rows.append({
                    "Rank": f"#{rank}",
                    "Candidate": r["candidate"],
                    "Fit Score (%)": r["fit_score"],
                    "Status": r["status"],
                    "Predicted Role": r["category"],
                    "JD Relevance (%)": r["relevance"],
                    "Category Alignment (%)": r["alignment"],
                    "Matched Skills": r["matched_count"],
                    "Missing Skills": r["missing_count"],
                    "Quick Verdict": r["verdict"][:90] + "..." if len(r["verdict"]) > 90 else r["verdict"],
                })
            df_table = pd.DataFrame(df_rows)

            st.dataframe(
                df_table,
                use_container_width=True,
                hide_index=True,
            )

            # Export CSV Button
            csv_buffer = io.StringIO()
            df_table.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue().encode("utf-8")

            col_dl, col_space = st.columns([1, 3])
            with col_dl:
                st.download_button(
                    label="📥 Download CSV Audit Report",
                    data=csv_data,
                    file_name="hirelens_candidate_leaderboard.csv",
                    mime="text/csv",
                    key="download_csv_btn",
                )

            # Candidate Drill-Down Selector 
            st.markdown("---")
            st.markdown('<div class="section-header">Candidate Deep-Dive Inspector</div>', unsafe_allow_html=True)

            candidate_options = [f"#{i+1}: {r['candidate']} ({r['fit_score']}%)" for i, r in enumerate(results)]
            selected_idx = st.selectbox("Select candidate to inspect full profile:", range(len(candidate_options)), format_func=lambda i: candidate_options[i])

            if selected_idx is not None and selected_idx < len(results):
                chosen = results[selected_idx]
                c_res = chosen["full_res"]
                c_narrative = c_res.get("narrative", {})

                dcol1, dcol2 = st.columns([1, 2.5])
                with dcol1:
                    render_gauge(chosen["fit_score"])
                    st.markdown(
                        f"""<div style="text-align:center;color:{score_color(chosen['fit_score'])};
                            font-weight:700;font-size:0.95rem;margin-top:-6px;">
                            {chosen['status']}
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with dcol2:
                    st.markdown(
                        f"""
                        <div class="card card-accent-left">
                            <div class="verdict-text">{c_narrative.get('verdict', '')}</div>
                            <div class="stat-row">
                                <div class="stat-item">
                                    <div class="stat-value">{chosen['category']}</div>
                                    <div class="stat-label">Role Category</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value">{chosen['relevance']:.0f}%</div>
                                    <div class="stat-label">Relevance</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value">{chosen['matched_count']}</div>
                                    <div class="stat-label">Matched Skills</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value">{chosen['missing_count']}</div>
                                    <div class="stat-label">Missing Skills</div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Interview Questions for chosen candidate
                c_questions = c_narrative.get("interview_questions", [])
                render_interview_questions(c_questions)

                # Categorized Skills Breakdown for chosen candidate
                render_categorized_skills(c_res.get("categorized_skills", {}))

                # SHAP Plot for chosen candidate
                if c_res.get("shap_figure") is not None:
                    st.markdown('<div class="section-header">Candidate SHAP Feature Attribution</div>', unsafe_allow_html=True)
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.pyplot(c_res["shap_figure"], use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
