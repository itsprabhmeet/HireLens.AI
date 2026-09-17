# AI-Powered Resume Screening & Job-Fit Classifier

> **MCA Minor Project** — NLP + Machine Learning + Explainable AI

A system that automatically scores how well a resume matches a job description and **explains why** using SHAP — not a black box.

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

You'll also need to download the spaCy English model (optional, for NER stretch goal):

```bash
python -m spacy download en_core_web_sm
```

### 2. Get the dataset

- **Option A (Recommended):** Download the [Kaggle Resume Dataset](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset)
  - Place `Resume.csv` or `UpdatedResumeDataSet.csv` at `data/resumes_dataset.csv`
- **Option B:** Skip this step — the app will generate a synthetic dataset automatically for testing

### 3. Train the model

```bash
python src/data_preprocessing.py
python src/feature_extraction.py
python src/train_model.py
```

**Or** just launch the app and click **"Train Models Now"** in the sidebar — it runs everything for you!

### 4. Launch the app

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
resume-screening-system/
├── data/
│   ├── resumes_dataset.csv        ← Kaggle dataset (you provide this)
│   ├── cleaned_resumes.csv        ← generated after preprocessing
│   ├── train.csv / test.csv       ← generated train/test split
│   └── confusion_matrix.png       ← generated after training
├── src/
│   ├── data_preprocessing.py      ← text cleaning, label encoding, train/test split
│   ├── feature_extraction.py      ← TF-IDF vectorization, cosine similarity, keyword matching
│   ├── train_model.py             ← Logistic Regression training + evaluation
│   └── explain.py                 ← SHAP explainability layer + plots
├── models/
│   ├── tfidf_vectorizer.pkl       ← saved TF-IDF vectorizer
│   ├── classifier_model.pkl       ← saved trained model
│   └── label_encoder.pkl          ← saved label encoder
├── app.py                         ← Streamlit web application
├── requirements.txt
└── README.md
```

---

## 🌟 Key Features

1. **Hybrid AI Matching Engine**: Combines sparse lexical precision (TF-IDF weighted keyword coverage) with dense semantic representations (`sentence-transformers: all-MiniLM-L6-v2`) to capture both exact technical credentials and conceptual synonyms.
2. **Batch Candidate Screening & Leaderboard**: Upload multiple resumes (PDF/DOCX/TXT) at once. HireLens automatically screens all candidates against the JD, ranks them on an interactive leaderboard, and provides a 1-click **CSV Audit Report export**.
3. **🛡️ Blind Screening Mode (PII Redaction)**: Anonymizes candidate names, emails, phone numbers, and profile URLs (LinkedIn/GitHub) to eliminate hiring bias and promote ethical, merit-based screening.
4. **🎯 Automated Technical Interview Questions**: Identifies specific missing skill gaps and formulates tailored interview questions for recruiters to probe candidate depth during screening calls.
5. **Explainable AI (SHAP)**: Uses feature attributions (bar and waterfall plots) to illuminate *why* the model scored a resume high or low.
6. **Skills Competency Breakdown**: Categorizes skills across Programming Languages, Frameworks, Cloud & DevOps, Databases, System Design, and Soft Skills.

---

## 🏗️ System Architecture

```
Resume (PDF/DOCX/Text) + Job Description
            ↓
   Text Extraction & Cleaning
   (pdfplumber / PyPDF2, python-docx, PII Anonymizer, NLTK)
            ↓
   Hybrid Feature Representation
   • TF-IDF Vectorization (scikit-learn, 1-2 grams)
   • Dense Neural Embeddings (SentenceTransformers: all-MiniLM-L6-v2)
            ↓
   Logistic Regression Classifier + Category Alignment
            ↓
   Composite Fit Score
   (Hybrid Relevance [Lexical + Semantic] + Category Alignment)
            ↓
   Explainability & Intelligence
   • SHAP Attribution Layer (Bar & Waterfall Charts)
   • Recruiter Narrative Engine
   • Skill Gap Interview Question Generator
            ↓
   Streamlit Interface
   (Candidate Leaderboard, SVG Gauge, Keyword Pills, PII Masking, CSV Export)
```

---

## 🧪 Running Individual Components

```bash
# Step 1: Preprocess data
python src/data_preprocessing.py

# Step 2: Extract features & fit vectorizer
python src/feature_extraction.py

# Step 3: Train classifier
python src/train_model.py

# Step 4: Test explanation & hybrid similarity
python src/explain.py

# Step 5: Launch app
streamlit run app.py
```

---

## 💡 Viva Q&A Quick Reference

| Question | Key Answer |
|----------|-----------|
| Why Hybrid (TF-IDF + Embeddings)? | TF-IDF ensures critical exact tools/certifications aren't missed; Sentence Transformers catch synonyms (e.g. "Kubernetes" ~ "container orchestration"). |
| How does Blind Screening work? | Automated PII redaction strips names, emails, phone numbers, and profile URLs before analysis to ensure merit-first evaluation without unconscious bias. |
| How is SHAP different from a similarity score? | SHAP shows *which specific words* contributed positively/negatively — not just a flat number. |
| How are interview questions generated? | The rule-based narrative engine analyzes missing JD requirements and maps them to technical question templates targeting those exact gaps. |
| What is Category Alignment? | We pass the JD itself through the role classifier to verify that the job description and candidate background belong to the same functional family. |
| How does Batch Screening scale? | Processes multiple documents concurrently and formats results into a ranked leaderboard with CSV audit export for high-volume recruitment. |

---

## 🎯 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| NLP & Semantics | SentenceTransformers (`all-MiniLM-L6-v2`), NLTK |
| Feature Extraction | TF-IDF (scikit-learn) |
| ML Model | Logistic Regression (L2 regularized) |
| Explainability | SHAP (LinearExplainer + Pure-Python LinearSHAP fallback) |
| Resume Parsing | pdfplumber, PyPDF2, python-docx |
| Bias Mitigation | Regex & Heuristic PII Anonymizer |
| Interface | Streamlit |
| Visualization | Matplotlib, Seaborn |

---

*Built by Prabhmeet Singh — Intelligent Resume Screening System using NLP and Explainable AI*
