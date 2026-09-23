# HireLens.AI — Explainable AI Recruitment Intelligence

> **MCA Minor Project** — NLP + Machine Learning + Explainable AI  
> **v2.0.0** · FastAPI Backend · React 19 + Vite Frontend

A full-stack AI-powered resume screening system that scores how well a candidate matches a job description and **explains *why*** using SHAP — not a black box. Supports single and batch screening, blind (anonymised) mode, automated interview question generation, and a live job description URL fetcher.

---

## 🚀 Quick Start

### 1. Create a virtual environment & install dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

> **Optional** — spaCy English model (for NER):
> ```bash
> python -m spacy download en_core_web_sm
> ```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Get the dataset

| Option | Steps |
|--------|-------|
| **A (Recommended)** | Download the [Kaggle Resume Dataset](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset) and place `Resume.csv` / `UpdatedResumeDataSet.csv` at `data/resumes_dataset.csv` |
| **B** | Skip — the app auto-generates a synthetic dataset for testing |

### 4. Train the ML models

```bash
python src/data_preprocessing.py
python src/feature_extraction.py
python src/train_model.py
```

**Or** use the API endpoint after launching the server:  
`POST /api/train` — triggers the full training pipeline programmatically.

### 5. Launch the app

```bash
# Modern full-stack mode (React SPA served by FastAPI) — DEFAULT
bash run.sh

# Full-stack developer mode (Vite HMR + FastAPI live reload)
bash run.sh dev
```

| Mode | URL |
|------|-----|
| Modern (production) | http://127.0.0.1:8000 |
| Dev (Vite HMR) | http://127.0.0.1:5173 |

---

## 📁 Project Structure

```
HireLens.AI/
├── api.py                         ← FastAPI backend (v2.0.0) — ML, NLP & SHAP pipelines
├── run.sh                         ← Unified launcher (modern | dev)
├── fix_job_url_endpoint.py        ← Utility: patch job URL endpoint
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py      ← Text cleaning, PII anonymisation, train/test split
│   ├── feature_extraction.py      ← TF-IDF vectorisation, cosine similarity, keyword matching
│   ├── train_model.py             ← Logistic Regression training + evaluation
│   ├── explain.py                 ← SHAP explainability layer (bar & waterfall charts)
│   ├── narrative.py               ← Rule-based offline narrative engine (verdict, strengths, gaps)
│   ├── job_fetcher.py             ← Job description extractor from URLs (JSON-LD + heuristic)
│   └── skills.py                  ← Skills taxonomy & competency categorisation
│
├── frontend/                      ← React 19 + Vite SPA
│   ├── src/
│   │   ├── App.jsx                ← Root app & state management
│   │   ├── main.jsx
│   │   ├── index.css              ← Global design system
│   │   ├── presets.js             ← Job description presets library
│   │   └── components/
│   │       ├── Navbar.jsx
│   │       ├── JobDescriptionSection.jsx
│   │       ├── ResumeUpload.jsx
│   │       ├── ScoreGauge.jsx
│   │       ├── LeaderboardTable.jsx
│   │       ├── CandidateDrawer.jsx
│   │       ├── NarrativeCard.jsx
│   │       ├── InterviewQuestionsCard.jsx
│   │       ├── ShapVisualizer.jsx
│   │       ├── SkillsMatrix.jsx
│   │       └── ResumeInspectorModal.jsx
│   ├── package.json
│   └── vite.config.js
│
├── models/
│   ├── classifier_model.pkl       ← Saved Logistic Regression model
│   ├── tfidf_vectorizer.pkl       ← Saved TF-IDF vectorizer
│   └── label_encoder.pkl          ← Saved label encoder
│
└── data/
    ├── resumes_dataset.csv        ← Kaggle dataset (user-provided)
    ├── cleaned_resumes.csv        ← Generated after preprocessing
    ├── train.csv / test.csv       ← Generated train/test split
    ├── X_train_sample.pkl         ← SHAP background sample
    └── confusion_matrix.png       ← Generated after training
```

---

## 🌟 Key Features

| # | Feature | Details |
|---|---------|---------|
| 1 | **Hybrid AI Matching Engine** | Combines sparse lexical precision (TF-IDF keyword coverage) with dense semantic embeddings (`all-MiniLM-L6-v2`) to capture exact credentials *and* conceptual synonyms |
| 2 | **Batch Candidate Screening & Leaderboard** | Upload multiple PDF/DOCX/TXT files at once; candidates auto-ranked by fit score with a 1-click CSV audit export |
| 3 | **🛡️ Blind Screening Mode** | PII redaction strips names, emails, phone numbers, and profile URLs (LinkedIn/GitHub) to eliminate unconscious hiring bias |
| 4 | **🎯 Interview Question Generator** | Identifies specific skill gaps and generates targeted recruiter questions to probe candidate depth |
| 5 | **Explainable AI (SHAP)** | Feature attributions (bar & waterfall charts) reveal *why* a resume scored high or low |
| 6 | **Narrative Engine** | Deterministic, offline rule-based engine converts numeric scores into a plain-language recruiter write-up (verdict, strengths, gaps, suggestions) |
| 7 | **Job URL Fetcher** | Extracts job descriptions from ATS URLs (Greenhouse, Lever, Workday, SmartRecruiters) via JSON-LD schema.org parsing |
| 8 | **Skills Competency Matrix** | Categorises skills across Programming Languages, Frameworks, Cloud & DevOps, Databases, System Design, and Soft Skills |
| 9 | **Modern Interface** | React 19 SPA with high-performance responsive UI and SVG gauges |

---

## 🏗️ System Architecture

```
Resume (PDF / DOCX / TXT)  +  Job Description (text or URL)
                ↓
  Text Extraction & Cleaning
  (pdfplumber / PyPDF2, python-docx, NLTK)
                ↓
  [Optional] PII Anonymisation
  (Regex + heuristic — names, emails, phones, profile URLs)
                ↓
  Hybrid Feature Representation
  • Sparse: TF-IDF Vectorisation (scikit-learn, 1-2 grams)
  • Dense:  Sentence Embeddings (all-MiniLM-L6-v2)
                ↓
  Logistic Regression Classifier  +  Category Alignment Score
                ↓
  Composite Fit Score
  (Hybrid Relevance [Lexical + Semantic]  +  Category Alignment)
                ↓
  Explainability & Intelligence Layer
  • SHAP Attribution Layer (LinearExplainer + pure-Python fallback)
  • Offline Narrative Engine  (narrative.py)
  • Skill Gap -> Interview Question Generator  (skills.py)
                ↓
  FastAPI Backend (api.py)  <->  React 19 + Vite Frontend
  (Candidate Leaderboard, SVG Score Gauge, Keyword Pills,
   Skills Matrix, SHAP Visualizer, CSV Export, Blind Mode)
```

---

## 🔌 API Reference

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Model readiness check + supported job categories |
| `GET` | `/api/health` | Alias for `/api/status` |
| `POST` | `/api/screen` | Screen a **single** resume (text paste or file upload) |
| `POST` | `/api/batch-screen` | Screen **multiple** resumes; returns ranked leaderboard |
| `POST` | `/api/fetch-job-url` | Extract a job description from an ATS URL |
| `POST` | `/api/train` | Trigger full ML training pipeline and reload models |

### `/api/screen` — request body (multipart/form-data)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `jd_text` | `string` | ✅ | Job description text |
| `resume_text` | `string` | ⬜ | Pasted resume text |
| `file` | `File` | ⬜ | PDF, DOCX, or TXT upload |
| `blind_mode` | `bool` | ⬜ | `false` by default |

### `/api/batch-screen` — request body (multipart/form-data)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `jd_text` | `string` | ✅ | Job description text |
| `files` | `File[]` | ✅ | One or more PDF/DOCX/TXT files |
| `blind_mode` | `bool` | ⬜ | `false` by default |

---

## 🧪 Running Individual Pipeline Steps

```bash
# Step 1: Preprocess raw data
python src/data_preprocessing.py

# Step 2: Extract TF-IDF features & fit vectorizer
python src/feature_extraction.py

# Step 3: Train Logistic Regression classifier
python src/train_model.py

# Step 4: Test SHAP explanation & hybrid similarity
python src/explain.py

# Step 5A: Launch modern full-stack app
bash run.sh

# Step 5B: Full-stack developer mode (HMR + live reload)
bash run.sh dev
```

---

## 💡 Viva Q&A Quick Reference

| Question | Key Answer |
|----------|-----------|
| Why Hybrid (TF-IDF + Embeddings)? | TF-IDF ensures exact tools/certifications aren't missed; Sentence Transformers catch synonyms (e.g. "Kubernetes" ~ "container orchestration") |
| How does Blind Screening work? | PII redaction strips names, emails, phones, and profile URLs before analysis — merit-first evaluation without unconscious bias |
| How is SHAP different from a similarity score? | SHAP shows *which specific words* pushed the score up or down — not just a flat number |
| How are interview questions generated? | The narrative engine analyses missing JD requirements and maps them to technical question templates targeting those exact gaps |
| What is Category Alignment? | The JD itself is passed through the role classifier to verify the job description and candidate background belong to the same functional family |
| How does Batch Screening scale? | Processes all documents sequentially, sorts by fit score, and returns a ranked leaderboard with a CSV audit export |
| Why FastAPI + React for v2? | Decouples the ML backend from the UI, enables a rich React SPA, and exposes a clean REST API for future integrations |
| How does the Job URL Fetcher work? | Tries `JobPosting` JSON-LD (schema.org) first, then falls back to a "biggest text block" heuristic; hostile domains (LinkedIn, Indeed) are short-circuited immediately |

---

## 🎯 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.10+ |
| **Backend API** | FastAPI + Uvicorn |
| **Frontend** | React 19 + Vite 8 (JSX, Vanilla CSS) |
| **NLP & Semantics** | SentenceTransformers (`all-MiniLM-L6-v2`), NLTK |
| **Feature Extraction** | TF-IDF (scikit-learn, 1-2 grams) |
| **ML Model** | Logistic Regression (L2 regularised) |
| **Explainability** | SHAP (LinearExplainer + pure-Python LinearSHAP fallback) |
| **Resume Parsing** | pdfplumber, PyPDF2, python-docx |
| **Bias Mitigation** | Regex & heuristic PII anonymiser |
| **Job URL Parsing** | requests + BeautifulSoup4 (JSON-LD schema.org + heuristic) |
| **Visualisation** | Matplotlib, Seaborn, Plotly |
| **Serialisation** | joblib |

---

*Built by **Prabhmeet Singh** — HireLens.AI: Intelligent Resume Screening using NLP, Explainable AI & a Modern Full-Stack Architecture*
