"""
app.py -- AI-Powered Resume Screening & Job-Fit Classifier
----------------------------------------------------------
Streamlit web application entry point.

Run with:
    streamlit run app.py
"""

import os
import sys
import io
import logging
import numpy as np
import pandas as pd
import joblib
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Allow imports from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# -- Page Config --------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="\U0001F916",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Design tokens (single source of truth so accent stays consistent) --------
ACCENT = "#818cf8"
ACCENT_2 = "#a78bfa"
CARD_BG = "rgba(255,255,255,0.03)"
CARD_BORDER = "rgba(255,255,255,0.08)"
TEXT_DIM = "rgba(255,255,255,0.55)"
TEXT_FAINT = "rgba(255,255,255,0.35)"
GOOD = "#4ade80"
WARN = "#fbbf24"
BAD = "#f87171"

# -- Custom CSS -----------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

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

    /* Neutral card -- used for almost everything. Accent is reserved for the
       CTA button and the hero score, so it actually stands out. */
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
        font-size: 0.95rem;
        font-weight: 600;
        color: rgba(255,255,255,0.75);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 26px 0 12px 0;
    }

    .verdict-text {
        font-size: 1.15rem;
        line-height: 1.6;
        color: rgba(255,255,255,0.92);
        font-weight: 500;
    }

    .narrative-block {
        font-size: 0.95rem;
        line-height: 1.65;
        color: rgba(255,255,255,0.72);
        margin-top: 10px;
    }

    .narrative-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 16px;
        display: block;
    }
    .label-strengths { color: #4ade80; }
    .label-gaps { color: #f87171; }
    .label-suggestions { color: #fbbf24; }

    .stat-row {
        display: flex;
        gap: 28px;
        flex-wrap: wrap;
        margin-top: 14px;
    }
    .stat-item {
        display: flex;
        flex-direction: column;
    }
    .stat-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: rgba(255,255,255,0.88);
    }
    .stat-label {
        font-size: 0.72rem;
        color: rgba(255,255,255,0.4);
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
        padding: 3px 12px;
        margin: 3px 4px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .keyword-pill-red {
        display: inline-block;
        background: rgba(248, 113, 113, 0.1);
        border: 1px solid rgba(248, 113, 113, 0.28);
        color: #f87171;
        border-radius: 20px;
        padding: 3px 12px;
        margin: 3px 4px;
        font-size: 0.8rem;
        font-weight: 500;
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
        padding: 12px 32px;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 4px 20px rgba(129, 140, 248, 0.25);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 26px rgba(129, 140, 248, 0.4);
    }

    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: rgba(255,255,255,0.9) !important;
    }

    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 12px !important;
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


# -- Helpers ----------------------------------------------------------------
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
    """Extract text from an uploaded PDF file."""
    try:
        import pdfplumber
        with pdfplumber.open(file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip()
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
    """Render an SVG-based circular gauge for the fit score -- the one
    place the accent gradient is used at full strength, since this is the
    single number everything else supports."""
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


def run_training_pipeline():
    """Run the full training pipeline with a progress bar."""
    from data_preprocessing import download_nltk_resources, load_and_preprocess
    from feature_extraction import run_feature_extraction
    from train_model import run_training

    progress = st.progress(0, text="Downloading NLTK resources...")
    download_nltk_resources()

    progress.progress(20, text="Preprocessing data...")
    load_and_preprocess()

    progress.progress(50, text="Extracting TF-IDF features...")
    X_train_tfidf, X_test_tfidf, _ = run_feature_extraction()

    import joblib as jb
    sample_size = min(200, X_train_tfidf.shape[0])
    idx = np.random.choice(X_train_tfidf.shape[0], sample_size, replace=False)
    jb.dump(X_train_tfidf[idx], "data/X_train_sample.pkl")

    progress.progress(75, text="Training classifier...")
    run_training()

    progress.progress(100, text="Training complete!")
    st.cache_resource.clear()
    st.success("Models trained and saved! You can now analyze resumes.")


# -- Sidebar ------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center;padding:20px 0 10px">
                <div style="font-size:2.2rem;">&#129302;</div>
                <div style="font-size:1.25rem;font-weight:700;color:rgba(255,255,255,0.92);">
                    AI Resume Screener
                </div>
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);margin-top:4px;">
                    NLP + ML + Explainable AI
                </div>
            </div>
            <hr style="border-color:rgba(255,255,255,0.08);margin:12px 0;">
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Model Setup")

        model, vectorizer, le, X_train_sample = load_models()
        if model is not None:
            st.success("Models loaded")
            st.markdown(
                f"<div style='font-size:0.78rem;color:rgba(255,255,255,0.45);'>"
                f"Classes: {', '.join(le.classes_[:4])}{'...' if len(le.classes_) > 4 else ''}"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("Models not trained yet")
            if st.button("Train Models Now", key="train_btn"):
                with st.spinner("Training... this may take 1-2 minutes."):
                    try:
                        run_training_pipeline()
                    except Exception as e:
                        st.error(f"Training failed: {e}")

        st.markdown("---")
        st.markdown("### Resume Input")
        input_method = st.radio(
            "How would you like to provide the resume?",
            ["Upload PDF/DOCX", "Paste Text"],
            key="input_method",
        )

        resume_text = ""
        if input_method == "Upload PDF/DOCX":
            uploaded_file = st.file_uploader(
                "Upload Resume",
                type=["pdf", "docx"],
                help="Supports PDF and DOCX formats",
            )
            if uploaded_file:
                if uploaded_file.name.endswith(".pdf"):
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = extract_text_from_docx(uploaded_file)
                if resume_text:
                    st.success(f"Extracted {len(resume_text.split())} words")
        else:
            resume_text = st.text_area(
                "Paste Resume Text",
                height=200,
                placeholder="Paste the full resume text here...",
                key="resume_text_input",
            )

        st.markdown("---")
        st.markdown(
            """
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.3);text-align:center;">
            Built for MCA Minor Project<br>
            NLP &middot; ML &middot; Explainable AI
            </div>
            """,
            unsafe_allow_html=True,
        )

    return resume_text, model, vectorizer, le, X_train_sample


# -- Main UI --------------------------------------------------------------------
def main():
    resume_text, model, vectorizer, le, X_train_sample = render_sidebar()

    st.markdown(
        """
        <div style="padding: 30px 0 10px;">
            <h1 style="font-size:2.1rem;font-weight:800;margin:0;
                background:linear-gradient(90deg,#818cf8,#a78bfa);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                display:inline-block;">
                AI-Powered Resume Screener
            </h1>
            <p style="color:rgba(255,255,255,0.45);font-size:1rem;margin-top:6px;">
                Score resume-job fit and read a plain-language screener's verdict
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-header">Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area(
        label="Job Description",
        label_visibility="collapsed",
        height=160,
        placeholder=(
            "Paste the job description here...\n\n"
            "Example: We are looking for a Data Scientist with expertise in Python, "
            "machine learning, NLP, and experience with scikit-learn or TensorFlow..."
        ),
        key="jd_input",
    )

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        analyze_clicked = st.button("Analyze Resume", key="analyze_btn")
    with col_info:
        if not resume_text:
            st.info("Upload or paste a resume in the sidebar to get started.")
        elif not jd_text:
            st.info("Enter a job description above, then click Analyze.")

    st.markdown("---")

    if analyze_clicked:
        if not resume_text:
            st.error("Please provide a resume (upload or paste in the sidebar).")
            return
        if not jd_text.strip():
            st.error("Please enter a job description.")
            return
        if model is None:
            st.error("Models not trained. Click **Train Models Now** in the sidebar.")
            return

        with st.spinner("Analyzing resume..."):
            from data_preprocessing import clean_resume_text
            from explain import explain_resume

            cleaned_resume = clean_resume_text(resume_text)
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

        fit_score = result["fit_score"]
        predicted_cat = result["predicted_category"]
        jd_relevance = result.get("jd_relevance", result.get("cosine_similarity", 0))
        category_alignment = result.get("category_alignment", 0)
        confidence = result["confidence"]
        narrative = result.get("narrative", {})

        # -- Hero: gauge + narrative verdict, side by side -----------------
        st.markdown('<div class="section-header">Result</div>', unsafe_allow_html=True)

        hero_col1, hero_col2 = st.columns([1, 2.4])
        with hero_col1:
            render_gauge(fit_score)
            st.markdown(
                f"""<div style="text-align:center;color:{score_color(fit_score)};
                    font-weight:600;font-size:0.95rem;margin-top:-6px;">
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
                            <div class="stat-label">Predicted Category</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{jd_relevance:.0f}%</div>
                            <div class="stat-label">JD Relevance</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{category_alignment:.0f}%</div>
                            <div class="stat-label">Category Alignment</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{confidence:.0f}%</div>
                            <div class="stat-label">Model Confidence</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # -- Narrative body: strengths / gaps / suggestions ------------------
        strengths = narrative.get("strengths", "")
        gaps = narrative.get("gaps", "")
        suggestions = narrative.get("suggestions", "")

        narrative_html = f"""<div class="card" style="margin-top:14px;">"""
        if strengths:
            narrative_html += (
                f'<span class="narrative-label label-strengths">Strengths</span>'
                f'<div class="narrative-block">{strengths}</div>'
            )
        if gaps:
            narrative_html += (
                f'<span class="narrative-label label-gaps">Gaps</span>'
                f'<div class="narrative-block">{gaps}</div>'
            )
        if suggestions:
            narrative_html += (
                f'<span class="narrative-label label-suggestions">Suggestion</span>'
                f'<div class="narrative-block">{suggestions}</div>'
            )
        narrative_html += "</div>"
        st.markdown(narrative_html, unsafe_allow_html=True)

        # -- Evidence, in tabs, secondary to the narrative --------------------
        st.markdown('<div class="section-header">Evidence</div>', unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["Keywords", "SHAP Explanation", "Category Probabilities"])

        with tab1:
            kcol1, kcol2 = st.columns(2)
            with kcol1:
                matched = result.get("matched_keywords", [])
                st.markdown(
                    f'<div class="section-header" style="margin-top:6px;">Matched ({len(matched)})</div>',
                    unsafe_allow_html=True,
                )
                if matched:
                    pills = " ".join(f'<span class="keyword-pill-green">{w}</span>' for w, _ in matched)
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.markdown(
                        '<span style="color:rgba(255,255,255,0.4);font-size:0.85rem;">No keyword matches found.</span>',
                        unsafe_allow_html=True,
                    )
            with kcol2:
                missing = result.get("missing_keywords", [])
                st.markdown(
                    f'<div class="section-header" style="margin-top:6px;">Missing ({len(missing)})</div>',
                    unsafe_allow_html=True,
                )
                if missing:
                    pills = " ".join(f'<span class="keyword-pill-red">{w}</span>' for w, _ in missing)
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.markdown(
                        '<span style="color:rgba(255,255,255,0.4);font-size:0.85rem;">All JD keywords matched!</span>',
                        unsafe_allow_html=True,
                    )

        with tab2:
            st.markdown(
                """
                <div style="font-size:0.82rem;color:rgba(255,255,255,0.45);margin-bottom:12px;">
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
                sf = result.get("shap_features", {})
                if sf.get("positive") or sf.get("negative"):
                    rows = (
                        [{"Keyword": w, "Contribution": v, "Direction": "Positive"} for w, v in sf["positive"]]
                        + [{"Keyword": w, "Contribution": v, "Direction": "Negative"} for w, v in sf["negative"]]
                    )
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)
                else:
                    st.warning("SHAP explanation could not be computed for this resume.")
                    shap_error = result.get("shap_error")
                    if shap_error:
                        with st.expander("Show technical details"):
                            st.code(shap_error)
            st.markdown('</div>', unsafe_allow_html=True)

            if waterfall_fig is not None:
                st.markdown('<div class="section-header">Waterfall Plot</div>', unsafe_allow_html=True)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.pyplot(waterfall_fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            all_proba = result.get("all_proba", {})
            if all_proba:
                sorted_proba = sorted(all_proba.items(), key=lambda x: x[1], reverse=True)
                top3 = sorted_proba[:3]
                rest = sorted_proba[3:]

                st.markdown(
                    '<div class="section-header" style="margin-top:6px;">Top Categories</div>',
                    unsafe_allow_html=True,
                )
                for cat, prob in top3:
                    col_label, col_bar = st.columns([2, 5])
                    with col_label:
                        st.markdown(
                            f'<span style="color:rgba(255,255,255,0.75);font-size:0.85rem;">{cat}</span>',
                            unsafe_allow_html=True,
                        )
                    with col_bar:
                        st.progress(int(prob), text=f"{prob:.1f}%")

                if rest:
                    with st.expander(f"Show all {len(sorted_proba)} categories"):
                        for cat, prob in rest:
                            col_label, col_bar = st.columns([2, 5])
                            with col_label:
                                st.markdown(
                                    f'<span style="color:rgba(255,255,255,0.75);font-size:0.85rem;">{cat}</span>',
                                    unsafe_allow_html=True,
                                )
                            with col_bar:
                                st.progress(int(prob), text=f"{prob:.1f}%")

    elif not analyze_clicked:
        st.markdown('<div class="section-header">How It Works</div>', unsafe_allow_html=True)
        hcol1, hcol2, hcol3, hcol4 = st.columns(4)
        steps = [
            ("1", "Upload Resume", "PDF, DOCX, or paste text in the sidebar"),
            ("2", "Enter Job Description", "Paste the JD in the field above"),
            ("3", "Click Analyze", "The pipeline scores the match"),
            ("4", "Read the Verdict", "A plain-language write-up, backed by the evidence"),
        ]
        for col, (num, title, desc) in zip([hcol1, hcol2, hcol3, hcol4], steps):
            with col:
                st.markdown(
                    f"""
                    <div class="card" style="padding:18px;text-align:center;">
                        <div style="font-size:1.4rem;font-weight:700;color:#818cf8;margin-bottom:6px;">{num}</div>
                        <div style="font-weight:600;color:rgba(255,255,255,0.85);font-size:0.9rem;">{title}</div>
                        <div style="color:rgba(255,255,255,0.4);font-size:0.77rem;margin-top:4px;">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.markdown(
            """
            <div style="text-align:center;margin-top:20px;">
                <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    color:rgba(255,255,255,0.6);border-radius:20px;padding:4px 14px;margin:4px;font-size:0.8rem;display:inline-block;">
                    Python 3.10+</span>
                <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    color:rgba(255,255,255,0.6);border-radius:20px;padding:4px 14px;margin:4px;font-size:0.8rem;display:inline-block;">
                    TF-IDF</span>
                <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    color:rgba(255,255,255,0.6);border-radius:20px;padding:4px 14px;margin:4px;font-size:0.8rem;display:inline-block;">
                    Logistic Regression</span>
                <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    color:rgba(255,255,255,0.6);border-radius:20px;padding:4px 14px;margin:4px;font-size:0.8rem;display:inline-block;">
                    SHAP Explainability</span>
                <span style="background:rgba(129,140,248,0.15);border:1px solid rgba(129,140,248,0.3);
                    color:#a78bfa;border-radius:20px;padding:4px 14px;margin:4px;font-size:0.8rem;display:inline-block;">
                    Rule-Based Narrative Engine</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
