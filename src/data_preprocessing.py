"""
data_preprocessing.py
---------------------
Day 1-2: Load the Kaggle Resume Dataset, clean text, encode labels,
split into train/test, and save processed data.

Usage:
    python src/data_preprocessing.py
"""

import os
import re
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import nltk
import joblib
import logging

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── NLTK downloads ────────────────────────────────────────────────────────────
def download_nltk_resources():
    """Download required NLTK data (runs once)."""
    resources = ["stopwords", "punkt", "wordnet"]
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            logger.warning(f"Could not download NLTK resource '{resource}': {e}")

# ── Text Cleaning ─────────────────────────────────────────────────────────────
def clean_resume_text(text: str) -> str:
    """
    Clean raw resume text:
    1. Strip HTML tags
    2. Remove URLs
    3. Remove special characters / punctuation (keep letters & numbers)
    4. Collapse whitespace
    5. Lowercase
    6. Remove NLTK stopwords
    """
    if not isinstance(text, str):
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)
    # Remove Twitter-style handles and hashtags
    text = re.sub(r"@\w+|#\w+", " ", text)
    # Remove non-alphanumeric characters (keep spaces)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    # Collapse multiple whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Lowercase
    text = text.lower()

    # Remove stopwords
    try:
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words("english"))
        tokens = text.split()
        tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
        text = " ".join(tokens)
    except Exception:
        pass  # If NLTK fails, return text without stopword removal

    return text


# ── Synthetic Dataset Generator ───────────────────────────────────────────────
def generate_synthetic_dataset(save_path: str) -> pd.DataFrame:
    """
    Generate a small synthetic resume dataset for testing when the
    Kaggle CSV is not available. Each row has 'Resume_str' and 'Category'.
    """
    logger.info("Generating synthetic dataset (no Kaggle CSV found)...")

    categories = {
        "Data Science": [
            "Experienced data scientist with expertise in Python, machine learning, deep learning, "
            "TensorFlow, PyTorch, scikit-learn. Worked on NLP, computer vision projects. "
            "Strong background in statistics, data analysis, pandas, numpy, SQL.",
            "Data scientist with 5 years experience. Skills: Python, R, machine learning, "
            "neural networks, data visualization, matplotlib, seaborn, Jupyter notebooks, "
            "feature engineering, model evaluation, A/B testing.",
            "Machine learning engineer proficient in Python, scikit-learn, XGBoost, "
            "LightGBM, feature selection, hyperparameter tuning, MLflow, Docker, AWS SageMaker.",
            "Senior data scientist with expertise in statistical modeling, hypothesis testing, "
            "regression analysis, clustering algorithms, Python, pandas, and big data tools.",
            "NLP engineer specializing in text classification, named entity recognition, "
            "transformers, BERT, spaCy, NLTK, sentiment analysis, and information extraction.",
            "Data analyst with skills in SQL, Python, Tableau, Power BI, Excel, "
            "data wrangling, dashboard creation, business intelligence, and KPI tracking.",
            "AI researcher with background in reinforcement learning, generative models, "
            "GANs, diffusion models, PyTorch, research papers, and model benchmarking.",
            "Machine learning ops engineer skilled in MLflow, Kubeflow, model deployment, "
            "Docker, Kubernetes, CI/CD pipelines, monitoring, and model versioning.",
        ],
        "Web Designing": [
            "Creative web designer with expertise in HTML, CSS, JavaScript, React, Vue.js, "
            "responsive design, UI/UX, Figma, Adobe XD, Bootstrap, Tailwind CSS.",
            "Frontend developer skilled in React, Angular, CSS animations, TypeScript, "
            "REST APIs, web performance optimization, cross-browser compatibility.",
            "UI/UX designer with proficiency in Figma, Adobe Illustrator, Sketch, "
            "wireframing, prototyping, user research, usability testing, HTML5, CSS3.",
            "Web developer with experience in JavaScript, jQuery, SASS, Webpack, "
            "accessibility standards, SEO optimization, and mobile-first design.",
            "Full-stack web designer skilled in React, Node.js, MongoDB, Express, "
            "RESTful APIs, GraphQL, responsive layouts, and progressive web apps.",
            "UX researcher experienced in user interviews, A/B testing, heatmaps, "
            "persona creation, journey mapping, and data-driven design decisions.",
            "Motion designer proficient in CSS animations, GSAP, Lottie, After Effects, "
            "interaction design, micro-animations, and performance-aware web animations.",
            "Web accessibility specialist with expertise in WCAG guidelines, ARIA, "
            "screen reader testing, keyboard navigation, and inclusive design practices.",
        ],
        "HR": [
            "Human resources professional with experience in talent acquisition, employee "
            "relations, performance management, HRIS systems, onboarding, payroll processing.",
            "HR manager skilled in recruitment, interviewing, compensation and benefits, "
            "training and development, compliance, workforce planning, labor relations.",
            "HR specialist experienced in applicant tracking systems, job postings, "
            "resume screening, background checks, new hire orientation, HR policies.",
            "Talent acquisition specialist with expertise in sourcing, LinkedIn recruiting, "
            "employer branding, campus hiring, offer negotiation, and retention strategies.",
            "HR business partner with experience in organizational development, change management, "
            "succession planning, employee engagement surveys, and leadership coaching.",
            "Compensation and benefits analyst skilled in salary benchmarking, job evaluation, "
            "benefits administration, ESOP, health insurance, and total rewards design.",
            "Learning and development manager with experience in training needs analysis, "
            "e-learning platforms, LMS administration, and leadership development programs.",
            "HR operations specialist with expertise in HRIS, SAP SuccessFactors, Workday, "
            "payroll processing, compliance reporting, and HR data analytics.",
        ],
        "Advocate": [
            "Lawyer with expertise in civil litigation, contract law, legal research, "
            "court proceedings, client counseling, legal drafting, case management.",
            "Legal advocate specializing in criminal defense, constitutional law, "
            "appellate practice, negotiation, mediation, and legal brief writing.",
            "Attorney with experience in corporate law, mergers and acquisitions, "
            "intellectual property, compliance, regulatory affairs, and legal strategy.",
            "Family law attorney skilled in divorce proceedings, child custody, "
            "adoption, alimony, domestic violence cases, and family court representation.",
            "Corporate counsel with expertise in contract drafting, legal due diligence, "
            "employment law, data privacy, GDPR compliance, and risk management.",
            "Litigation attorney experienced in civil disputes, arbitration, discovery, "
            "depositions, trial preparation, and appellate court arguments.",
            "Intellectual property lawyer specializing in patent prosecution, trademark filing, "
            "copyright infringement, licensing agreements, and IP portfolio management.",
            "Labor law advocate with expertise in employment disputes, wrongful termination, "
            "workplace harassment, labor regulations, and union negotiations.",
        ],
        "Accountant": [
            "Certified accountant with expertise in financial reporting, GAAP, tax preparation, "
            "auditing, budgeting, financial analysis, QuickBooks, SAP, Excel.",
            "Finance professional skilled in accounts payable, accounts receivable, "
            "general ledger, month-end close, variance analysis, forecasting, ERP systems.",
            "CPA with experience in corporate taxation, financial statements, internal controls, "
            "risk assessment, Sarbanes-Oxley compliance, and financial modeling.",
            "Tax consultant with expertise in GST, income tax, TDS, tax planning, "
            "audit representation, tax compliance, and financial advisory services.",
            "Management accountant skilled in cost accounting, budgeting, variance analysis, "
            "profitability reporting, KPI dashboards, and strategic financial planning.",
            "Audit associate experienced in internal audits, risk assessment, internal controls, "
            "SOX compliance, audit planning, and financial statement review.",
            "Financial analyst with skills in financial modeling, DCF valuation, Excel, "
            "PowerPoint, investment analysis, equity research, and market forecasting.",
            "Accounts manager with expertise in client billing, invoice processing, "
            "collections, reconciliations, financial reporting, and ERP administration.",
        ],
        "Sales": [
            "Sales executive with proven track record in B2B sales, lead generation, "
            "CRM tools, Salesforce, pipeline management, contract negotiation, cold calling.",
            "Business development manager skilled in consultative selling, account management, "
            "territory planning, sales forecasting, customer retention, and revenue growth.",
            "Sales representative experienced in retail sales, customer service, "
            "product demonstrations, closing deals, upselling, and market expansion.",
            "Inside sales specialist with expertise in outbound calling, email campaigns, "
            "HubSpot CRM, lead qualification, objection handling, and quota achievement.",
            "Key account manager with experience managing enterprise clients, renewals, "
            "cross-selling, strategic partnerships, and executive-level presentations.",
            "Sales operations analyst skilled in CRM data management, sales reporting, "
            "pipeline analytics, forecasting models, and process optimization.",
            "Channel sales manager with expertise in distributor management, partner programs, "
            "incentive structures, market penetration, and indirect sales strategies.",
            "Pre-sales consultant with background in solution selling, product demos, "
            "RFP responses, technical presentations, and proof of concept delivery.",
        ],
        "Java Developer": [
            "Java developer with expertise in Spring Boot, Hibernate, REST APIs, "
            "microservices, Maven, JUnit, MySQL, Docker, Kubernetes, CI/CD pipelines.",
            "Backend engineer skilled in Java, Spring Framework, JPA, Apache Kafka, "
            "Redis, PostgreSQL, AWS, agile development, code reviews, TDD.",
            "Software developer proficient in Java EE, JSP, Servlets, design patterns, "
            "OOP principles, multi-threading, performance tuning, and system design.",
            "Java architect with experience in distributed systems, event-driven architecture, "
            "CQRS, microservices design, API gateway, and cloud-native development.",
            "Android developer with Java and Kotlin skills, building mobile apps, "
            "Android SDK, Retrofit, Room database, MVVM, and Google Play deployment.",
            "Java full-stack developer proficient in Spring Boot, React, MySQL, "
            "REST APIs, JWT authentication, unit testing, and agile sprints.",
            "DevOps-oriented Java developer with expertise in Jenkins, Docker, "
            "Kubernetes, Terraform, monitoring with Grafana, and automated deployments.",
            "Senior Java engineer with 8 years experience in enterprise applications, "
            "SOA, SOAP web services, Oracle DB, and legacy system modernization.",
        ],
        "Python Developer": [
            "Python developer experienced in Django, Flask, FastAPI, SQLAlchemy, "
            "Celery, Redis, PostgreSQL, Docker, REST APIs, unit testing, pytest.",
            "Backend Python engineer skilled in asyncio, aiohttp, SQLite, MongoDB, "
            "GraphQL, AWS Lambda, serverless architecture, and code optimization.",
            "Full-stack Python developer proficient in Django REST Framework, Vue.js, "
            "PostgreSQL, Redis, CI/CD, GitHub Actions, and cloud deployment.",
            "Python automation engineer with expertise in Selenium, Playwright, pytest, "
            "web scraping, BeautifulSoup, Scrapy, and test automation frameworks.",
            "Data engineering Python developer skilled in Apache Airflow, Spark PySpark, "
            "ETL pipelines, data lakes, S3, Redshift, and dbt transformations.",
            "Python backend developer with experience in microservices, gRPC, Protocol Buffers, "
            "Kafka integration, Redis caching, Celery task queues, and API design.",
            "Scientific Python developer with skills in NumPy, SciPy, Matplotlib, "
            "Jupyter, simulation modeling, and numerical computing for research.",
            "Python security engineer experienced in vulnerability scanning, penetration testing "
            "scripts, cryptography libraries, and secure coding practices.",
        ],
    }

    rows = []
    for category, texts in categories.items():
        for text in texts:
            rows.append({"Resume_str": text, "Category": category})

    df = pd.DataFrame(rows)
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(save_path, index=False)
    logger.info(f"Synthetic dataset saved: {save_path} ({len(df)} rows)")
    return df


# ── Main Pipeline ─────────────────────────────────────────────────────────────
def load_and_preprocess(
    data_path: str = "data/resumes_dataset.csv",
    output_dir: str = "data",
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """
    Full preprocessing pipeline:
    1. Load dataset (Kaggle or synthetic fallback)
    2. Clean resume text
    3. Encode labels
    4. Train/test split
    5. Save artifacts

    Returns a dict with train/test splits and metadata.
    """
    os.makedirs(output_dir, exist_ok=True)

    # ── 1. Load data ──────────────────────────────────────────────────────
    if os.path.exists(data_path):
        logger.info(f"Loading dataset from: {data_path}")
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} rows, columns: {list(df.columns)}")

        # Detect resume text column (Kaggle dataset uses 'Resume_str' or 'resume_text')
        text_col = None
        for candidate in ["Resume_str", "resume_text", "resume", "text", "Resume"]:
            if candidate in df.columns:
                text_col = candidate
                break
        if text_col is None:
            raise ValueError(
                f"Could not find resume text column. Available: {list(df.columns)}"
            )

        # Detect label column
        label_col = None
        for candidate in ["Category", "category", "label", "Label"]:
            if candidate in df.columns:
                label_col = candidate
                break
        if label_col is None:
            raise ValueError(
                f"Could not find label column. Available: {list(df.columns)}"
            )

        df = df[[text_col, label_col]].rename(
            columns={text_col: "Resume_str", label_col: "Category"}
        )
    else:
        logger.warning(
            f"Dataset not found at '{data_path}'. Using synthetic data.\n"
            "  → Download the Kaggle Resume Dataset and place it at data/resumes_dataset.csv"
        )
        df = generate_synthetic_dataset(data_path)

    # ── 2. Drop nulls & duplicates ─────────────────────────────────────────
    original_len = len(df)
    df = df.dropna(subset=["Resume_str", "Category"])
    df = df.drop_duplicates(subset=["Resume_str"])
    logger.info(f"Rows after dedup/dropna: {len(df)} (removed {original_len - len(df)})")

    # ── 3. Clean text ──────────────────────────────────────────────────────
    logger.info("Cleaning resume text...")
    df["cleaned_resume"] = df["Resume_str"].apply(clean_resume_text)

    # Drop rows where cleaning produced empty strings
    df = df[df["cleaned_resume"].str.strip().astype(bool)]
    logger.info(f"Rows after cleaning: {len(df)}")

    # ── 4. Label distribution ──────────────────────────────────────────────
    logger.info("Category distribution:")
    for cat, count in df["Category"].value_counts().items():
        logger.info(f"  {cat}: {count}")

    # ── 5. Encode labels ───────────────────────────────────────────────────
    le = LabelEncoder()
    df["label"] = le.fit_transform(df["Category"])
    logger.info(f"Encoded {len(le.classes_)} categories: {list(le.classes_)}")

    # ── 6. Train / test split ──────────────────────────────────────────────
    X = df["cleaned_resume"].to_numpy(dtype=str)
    y = df["label"].to_numpy(dtype=int)
    categories = df["Category"].to_numpy(dtype=str)

    # Adaptive test_size: ensure test set has at least n_classes samples
    n_classes = len(np.unique(y))
    min_test_samples = n_classes  # need at least 1 per class for stratify
    effective_test_size = max(test_size, (min_test_samples + 1) / len(y))
    if effective_test_size >= 1.0:
        effective_test_size = 0.4  # fallback for very small datasets
    logger.info(f"Effective test_size: {effective_test_size:.2f} (n_classes={n_classes}, n_samples={len(y)})")

    X_train, X_test, y_train, y_test, cat_train, cat_test = train_test_split(
        X, y, categories,
        test_size=effective_test_size,
        random_state=random_state,
        stratify=y,
    )
    logger.info(f"Train size: {len(X_train)} | Test size: {len(X_test)}")

    # ── 7. Save artifacts ──────────────────────────────────────────────────
    # Save cleaned full dataframe
    cleaned_path = os.path.join(output_dir, "cleaned_resumes.csv")
    df.to_csv(cleaned_path, index=False)
    logger.info(f"Saved cleaned data: {cleaned_path}")

    # Save label encoder
    os.makedirs("models", exist_ok=True)
    le_path = os.path.join("models", "label_encoder.pkl")
    joblib.dump(le, le_path)
    logger.info(f"Saved label encoder: {le_path}")

    # Save train/test splits
    train_df = pd.DataFrame({"text": X_train, "label": y_train, "category": cat_train})
    test_df = pd.DataFrame({"text": X_test, "label": y_test, "category": cat_test})
    train_df.to_csv(os.path.join(output_dir, "train.csv"), index=False)
    test_df.to_csv(os.path.join(output_dir, "test.csv"), index=False)
    logger.info("Saved train.csv and test.csv")

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "label_encoder": le,
        "classes": list(le.classes_),
        "df": df,
    }


if __name__ == "__main__":
    download_nltk_resources()
    result = load_and_preprocess()
    logger.info("✅ Preprocessing complete!")
    logger.info(f"   Classes: {result['classes']}")
    logger.info(f"   Train samples: {len(result['X_train'])}")
    logger.info(f"   Test samples:  {len(result['X_test'])}")
