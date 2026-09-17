"""
api.py - FastAPI Backend Service for HireLens.AI
------------------------------------------------
Serves the Machine Learning, Hybrid Semantic NLP, and SHAP Explainability
pipelines to the modern web frontend.
"""

import os
import io
import sys
import logging
from typing import List, Optional
import numpy as np
import joblib
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add workspace and src to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from src.data_preprocessing import clean_resume_text, anonymize_resume_text
from src.explain import explain_resume

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HireLens.AI API",
    description="Explainable AI Recruitment Intelligence Backend",
    version="2.0.0",
)

# Enable CORS for local development and SPA frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Model Cache
_MODEL = None
_VECTORIZER = None
_LABEL_ENCODER = None
_X_TRAIN_SAMPLE = None


def get_models():
    """Load model artifacts with in-memory caching."""
    global _MODEL, _VECTORIZER, _LABEL_ENCODER, _X_TRAIN_SAMPLE
    if _MODEL is None:
        model_path = os.path.join(BASE_DIR, "models", "classifier_model.pkl")
        vectorizer_path = os.path.join(BASE_DIR, "models", "tfidf_vectorizer.pkl")
        le_path = os.path.join(BASE_DIR, "models", "label_encoder.pkl")
        sample_path = os.path.join(BASE_DIR, "data", "X_train_sample.pkl")

        if os.path.exists(model_path) and os.path.exists(vectorizer_path) and os.path.exists(le_path):
            _MODEL = joblib.load(model_path)
            _VECTORIZER = joblib.load(vectorizer_path)
            _LABEL_ENCODER = joblib.load(le_path)
            if os.path.exists(sample_path):
                _X_TRAIN_SAMPLE = joblib.load(sample_path)
            logger.info("HireLens models loaded successfully into API memory.")
        else:
            logger.warning("Models not found on disk. Run training first.")
    return _MODEL, _VECTORIZER, _LABEL_ENCODER, _X_TRAIN_SAMPLE


def extract_file_content(filename: str, content_bytes: bytes) -> str:
    """Extract plain text from PDF, DOCX, or TXT binary bytes."""
    fname = filename.lower()
    text = ""
    # PDF
    if fname.endswith(".pdf"):
        # Attempt 1: pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
                pages_text = [page.extract_text() or "" for page in pdf.pages]
                text = "\n".join(pages_text).strip()
            if text:
                return text
        except Exception:
            pass

        # Attempt 2: PyPDF2 fallback
        try:
            import importlib
            pypdf_mod = importlib.import_module("PyPDF2")
            reader = pypdf_mod.PdfReader(io.BytesIO(content_bytes))
            pages_text = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages_text).strip()
        except Exception as e:
            logger.warning(f"PDF extraction error: {e}")
            return ""

    # DOCX
    elif fname.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(content_bytes))
            return "\n".join(p.text for p in doc.paragraphs).strip()
        except Exception as e:
            logger.warning(f"DOCX extraction error: {e}")
            return ""

    # Plain text
    elif fname.endswith(".txt"):
        return content_bytes.decode("utf-8", errors="ignore").strip()

    return ""


def format_evaluation_payload(result: dict, display_name: str, filename: str, text_to_screen: str, blind_mode: bool, redaction_counts: dict) -> dict:
    """Format and normalize all explainability and scoring outputs for the frontend."""
    import re
    narrative = result.get("narrative", {})
    if not isinstance(narrative, dict):
        narrative = {}

    def to_str_list(val):
        if isinstance(val, list):
            return [str(x).strip() for x in val if str(x).strip()]
        elif isinstance(val, str):
            items = [s.strip("- •\t") for s in re.split(r'[\n•]+|(?<=[.!?])\s+', val) if s.strip("- •\t")]
            return items if items else ([val] if val.strip() else [])
        return []

    clean_narrative = {
        "verdict": str(narrative.get("verdict", "Candidate evaluated against job description.")),
        "overall_fit": str(narrative.get("overall_fit", "Evaluated")),
        "strengths": to_str_list(narrative.get("strengths", [])),
        "gaps": to_str_list(narrative.get("gaps", [])),
        "suggestions": to_str_list(narrative.get("suggestions", [])),
        "interview_questions": narrative.get("interview_questions", []),
    }

    # Normalize SHAP features to a dict of { feature: weight }
    raw_shap = result.get("shap_features", {})
    shap_dict = {}
    if isinstance(raw_shap, dict):
        if "positive" in raw_shap or "negative" in raw_shap:
            for feat, val in raw_shap.get("positive", []):
                shap_dict[str(feat)] = float(val)
            for feat, val in raw_shap.get("negative", []):
                shap_dict[str(feat)] = float(val)
        else:
            for k, v in raw_shap.items():
                try:
                    shap_dict[str(k)] = float(v)
                except (ValueError, TypeError):
                    pass
    elif isinstance(raw_shap, list):
        for item in raw_shap:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                shap_dict[str(item[0])] = float(item[1])
            elif isinstance(item, dict) and "feature" in item:
                shap_dict[str(item["feature"])] = float(item.get("value", item.get("score", 0)))

    # Normalize matched & missing keywords to lists of [word, count]
    matched_kws = []
    for item in result.get("matched_keywords", []):
        if isinstance(item, (list, tuple)):
            matched_kws.append([str(item[0]), int(item[1]) if len(item) > 1 else 1])
        else:
            matched_kws.append([str(item), 1])

    missing_kws = []
    for item in result.get("missing_keywords", []):
        if isinstance(item, (list, tuple)):
            missing_kws.append([str(item[0]), int(item[1]) if len(item) > 1 else 1])
        else:
            missing_kws.append([str(item), 1])

    # Normalize categorized_skills so lists inside are clean strings
    raw_cats = result.get("categorized_skills", {})
    clean_cats = {}
    if isinstance(raw_cats, dict):
        for cat_name, cat_val in raw_cats.items():
            if isinstance(cat_val, dict):
                clean_cats[cat_name] = {
                    "matched": [str(m[0] if isinstance(m, (list, tuple)) else m) for m in cat_val.get("matched", [])],
                    "missing": [str(m[0] if isinstance(m, (list, tuple)) else m) for m in cat_val.get("missing", [])],
                }
            elif isinstance(cat_val, list):
                clean_cats[cat_name] = {"matched": [str(x) for x in cat_val], "missing": []}

    return {
        "candidate": display_name,
        "filename": filename,
        "fit_score": float(result["fit_score"]),
        "predicted_category": str(result["predicted_category"]),
        "jd_relevance": float(result.get("jd_relevance", 0)),
        "lexical_relevance": float(result.get("lexical_relevance", result.get("jd_relevance", 0))),
        "semantic_similarity": float(result.get("semantic_similarity", 0)),
        "category_alignment": float(result.get("category_alignment", 0)),
        "confidence": float(result.get("confidence", 0)),
        "all_proba": result.get("all_proba", {}),
        "matched_keywords": matched_kws,
        "missing_keywords": missing_kws,
        "matched_count": len(matched_kws),
        "missing_count": len(missing_kws),
        "categorized_skills": clean_cats,
        "shap_features": shap_dict,
        "narrative": clean_narrative,
        "blind_mode": blind_mode,
        "redaction_counts": redaction_counts,
        "raw_text": text_to_screen,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/status")
@app.get("/api/health")
def get_system_status():
    """Check AI model readiness and supported categories."""
    model, vectorizer, le, _ = get_models()
    if model is not None:
        return {
            "status": "ready",
            "models_loaded": True,
            "categories": list(le.classes_),
            "total_categories": len(le.classes_),
        }
    return {
        "status": "not_initialized",
        "models_loaded": False,
        "categories": [],
        "total_categories": 0,
    }


@app.post("/api/screen")
async def screen_single_resume(
    jd_text: str = Form(...),
    resume_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    blind_mode: bool = Form(False),
):
    """
    Screen a single resume against a target job description.
    Supports either direct text paste or file upload (.pdf, .docx, .txt).
    """
    model, vectorizer, le, sample = get_models()
    if model is None:
        raise HTTPException(status_code=503, detail="Models not trained or loaded.")

    raw_text = ""
    filename = "Pasted Resume"
    if file is not None:
        filename = file.filename
        content = await file.read()
        raw_text = extract_file_content(filename, content)
    elif resume_text:
        raw_text = resume_text

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the resume input.")

    # Blind screening mode
    redaction_counts = {"emails": 0, "phones": 0, "links": 0, "names": 0}
    text_to_screen = raw_text
    display_name = filename
    if blind_mode:
        anon_result = anonymize_resume_text(raw_text)
        text_to_screen = anon_result["anonymized_text"]
        redaction_counts = anon_result["redaction_counts"]
        display_name = "Candidate #01 (Anonymized)"

    cleaned_resume = clean_resume_text(text_to_screen)
    cleaned_jd = clean_resume_text(jd_text)

    if not cleaned_resume:
        raise HTTPException(status_code=400, detail="Text cleaning produced empty content.")

    result = explain_resume(
        cleaned_resume,
        cleaned_jd,
        model,
        vectorizer,
        le,
        X_train_sample=sample,
    )

    return format_evaluation_payload(
        result,
        display_name=display_name,
        filename=filename,
        text_to_screen=text_to_screen,
        blind_mode=blind_mode,
        redaction_counts=redaction_counts,
    )


@app.post("/api/batch-screen")
async def screen_batch_resumes(
    jd_text: str = Form(...),
    files: List[UploadFile] = File(...),
    blind_mode: bool = Form(False),
):
    """
    Screen multiple resumes simultaneously and return a ranked candidate list.
    """
    model, vectorizer, le, sample = get_models()
    if model is None:
        raise HTTPException(status_code=503, detail="Models not trained or loaded.")

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    cleaned_jd = clean_resume_text(jd_text)
    if not cleaned_jd:
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    evaluations = []

    for i, file in enumerate(files):
        content = await file.read()
        raw_text = extract_file_content(file.filename, content)
        if not raw_text.strip():
            continue

        text_to_screen = raw_text
        candidate_label = file.filename
        redaction_counts = {"emails": 0, "phones": 0, "links": 0, "names": 0}

        if blind_mode:
            anon = anonymize_resume_text(raw_text)
            text_to_screen = anon["anonymized_text"]
            redaction_counts = anon["redaction_counts"]
            candidate_label = f"Candidate #{i+1:02d}"

        cleaned_resume = clean_resume_text(text_to_screen)
        if not cleaned_resume:
            continue

        try:
            res = explain_resume(
                cleaned_resume,
                cleaned_jd,
                model,
                vectorizer,
                le,
                X_train_sample=sample,
            )
            cand_payload = format_evaluation_payload(
                res,
                display_name=candidate_label,
                filename=file.filename,
                text_to_screen=text_to_screen,
                blind_mode=blind_mode,
                redaction_counts=redaction_counts,
            )
            cand_payload["id"] = f"cand_{i+1}"
            evaluations.append(cand_payload)
        except Exception as e:
            logger.warning(f"Failed to screen {file.filename}: {e}")

    # Rank descending by fit_score
    evaluations.sort(key=lambda x: x["fit_score"], reverse=True)
    for rank, ev in enumerate(evaluations, 1):
        ev["rank"] = rank

    return {
        "total_screened": len(evaluations),
        "candidates": evaluations,
    }


@app.post("/api/train")
def trigger_training():
    """Trigger the training pipeline to retrain models on dataset."""
    try:
        from src.data_preprocessing import download_nltk_resources, load_and_preprocess
        from src.feature_extraction import run_feature_extraction
        from src.train_model import run_training

        download_nltk_resources()
        load_and_preprocess()
        run_feature_extraction()
        run_training()

        # Reload cache
        global _MODEL, _VECTORIZER, _LABEL_ENCODER, _X_TRAIN_SAMPLE
        _MODEL = None
        get_models()

        return {"status": "success", "message": "Models retrained and reloaded into memory."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")


# ── Mount Built Frontend SPA ──────────────────────────────────────────────────
frontend_dist = os.path.join(BASE_DIR, "frontend", "dist")
if os.path.isdir(frontend_dist):
    from fastapi.responses import FileResponse

    @app.get("/")
    async def serve_spa_root():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa_path(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
