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

## 🏗️ System Architecture

```
Resume (PDF/DOCX/Text) + Job Description
            ↓
   Text Extraction & Cleaning
   (pdfplumber, python-docx, regex, NLTK)
            ↓
   TF-IDF Vectorization
   (scikit-learn, 10k features, 1-2 grams)
            ↓
   Logistic Regression Classifier
   (trained on ~2000 labeled resumes)
            ↓
   Composite Fit Score
   (model confidence + cosine similarity)
            ↓
   SHAP Explainability Layer
   (LinearExplainer → top +/- features)
            ↓
   Streamlit Interface
   (score gauge, keyword pills, SHAP charts)
```

---

## 🧪 Running Individual Components

```bash
# Step 1: Preprocess data
python src/data_preprocessing.py

# Step 2: Extract TF-IDF features
python src/feature_extraction.py

# Step 3: Train classifier
python src/train_model.py

# Step 4: Test explanation (requires trained models)
python src/explain.py

# Step 5: Launch app
streamlit run app.py
```

---

## 💡 Viva Q&A Quick Reference

| Question | Key Answer |
|----------|-----------|
| Why TF-IDF instead of BERT? | Faster, interpretable, SHAP works natively with linear models, sufficient for keyword-based matching |
| How is SHAP different from a similarity score? | SHAP shows *which specific words* contributed positively/negatively — not just a number |
| How do you handle resumes with no keywords? | TF-IDF produces a near-zero vector → low cosine sim → low fit score + SHAP shows missing terms |
| Category classification vs fit scoring? | Classification = which job family; fit score = how strong is the match to *this specific JD* |
| Limitations of TF-IDF? | No semantic understanding (synonym-blind), bag-of-words (loses order), OOV terms get 0 weight |
| How to scale? | Batch vectorization, model serving API (FastAPI), pre-computed resume embeddings |

---

## 🎯 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| NLP | NLTK (stopwords, tokenization) |
| Feature Extraction | TF-IDF (scikit-learn) |
| ML Model | Logistic Regression |
| Explainability | SHAP (LinearExplainer) |
| Resume Parsing | pdfplumber, python-docx |
| Interface | Streamlit |
| Visualization | Matplotlib, Seaborn |

---

*Built for MCA Minor Project — Intelligent Resume Screening System using NLP and Explainable AI*
