"""
skills.py
---------
A curated dictionary of recognizable skills/tools spanning the job
categories this project classifies. Used to build a clean, actionable
"Skills Gap" list by matching directly against the raw resume/JD text with
regex -- independent of the TF-IDF vectorizer's fixed vocabulary.

This independence matters: the vectorizer can only recognize words it saw
during training. A specific tool name that never appeared in the training
resumes (e.g. "Kafka") is invisible to TF-IDF entirely, so building skill
gaps from the vectorizer's matched/missing keyword lists alone would
silently miss it. Matching directly against text sidesteps that.

Usage:
    from skills import extract_skill_gaps
    result = extract_skill_gaps(resume_text, jd_text)
    result["missing_skills"]  -> [display_name, ...] -- in JD, not in resume
    result["present_skills"]  -> [display_name, ...] -- in JD, and in resume
"""

import re

# Canonical skill display name -> set of raw alias forms to match. Aliases
# are matched case-insensitively as whole words/phrases (not substrings of
# other words), so keep them lowercase here.
SKILL_ALIASES = {
    # -- Programming / Data / IT --
    "Python": {"python"},
    "Java": {"java"},
    "JavaScript": {"javascript", "js"},
    "SQL": {"sql", "mysql", "postgresql", "postgres"},
    "Machine Learning": {"machine learning", "ml"},
    "Deep Learning": {"deep learning"},
    "NLP": {"nlp", "natural language processing"},
    "TensorFlow": {"tensorflow"},
    "PyTorch": {"pytorch"},
    "Scikit-learn": {"scikit learn", "sklearn"},
    "Docker": {"docker"},
    "Kubernetes": {"kubernetes", "k8s"},
    "AWS": {"aws", "amazon web services"},
    "Azure": {"azure"},
    "Google Cloud": {"gcp", "google cloud"},
    "Kafka": {"kafka"},
    "Spark": {"spark", "pyspark"},
    "Airflow": {"airflow"},
    "REST APIs": {"rest api", "rest apis", "restful"},
    "Git": {"git", "github", "gitlab"},
    "CI/CD": {"ci cd", "cicd", "continuous integration"},
    "Linux": {"linux", "unix"},
    "Networking": {"networking"},
    "Cybersecurity": {"cybersecurity"},
    "HTML/CSS": {"html", "css"},
    "React": {"react", "reactjs"},
    "Node.js": {"node js", "nodejs"},
    "Excel": {"excel"},
    "Tableau": {"tableau"},
    "Power BI": {"power bi", "powerbi"},
    "Data Analysis": {"data analysis", "data analytics"},
    # -- Design --
    "Photoshop": {"photoshop"},
    "Illustrator": {"illustrator"},
    "Figma": {"figma"},
    "Adobe XD": {"adobe xd"},
    "UI/UX Design": {"ui ux", "ui design", "ux design"},
    # -- Finance / Accounting --
    "GAAP": {"gaap"},
    "QuickBooks": {"quickbooks"},
    "SAP": {"sap"},
    "Financial Modeling": {"financial modeling", "financial modelling"},
    "Bookkeeping": {"bookkeeping"},
    "Auditing": {"auditing"},
    "Taxation": {"taxation"},
    # -- Sales / Marketing / Business --
    "Salesforce (CRM)": {"salesforce"},
    "SEO": {"seo"},
    "Google Ads": {"google ads", "adwords"},
    "Social Media Marketing": {"social media marketing"},
    "Content Marketing": {"content marketing"},
    "Email Marketing": {"email marketing"},
    "Negotiation": {"negotiation"},
    # -- HR --
    "HRIS Systems": {"hris"},
    "Recruitment": {"recruitment", "recruiting"},
    "Payroll": {"payroll"},
    "Onboarding": {"onboarding"},
    # -- Healthcare --
    "EMR/EHR Systems": {"emr", "ehr"},
    "Patient Care": {"patient care"},
    "Medical Coding": {"medical coding"},
    "CPR Certification": {"cpr"},
    # -- Culinary --
    "Menu Planning": {"menu planning"},
    "Food Safety": {"food safety", "servsafe"},
    "Inventory Management": {"inventory management"},
    # -- Construction / Engineering --
    "AutoCAD": {"autocad"},
    "Project Management": {"project management", "pmp"},
    "Blueprint Reading": {"blueprint reading"},
    "OSHA Compliance": {"osha"},
    "SolidWorks": {"solidworks"},
    # -- Legal --
    "Legal Research": {"legal research"},
    "Contract Drafting": {"contract drafting"},
    "Litigation": {"litigation"},
    # -- Aviation --
    "FAA Regulations": {"faa"},
    "Aircraft Maintenance": {"aircraft maintenance"},
    # -- Teaching --
    "Curriculum Development": {"curriculum development", "curriculum"},
    "Classroom Management": {"classroom management"},
    # -- Agriculture --
    "Crop Management": {"crop management"},
    "Soil Science": {"soil science"},
    # -- General/business tools --
    "Microsoft Office": {"microsoft office", "ms office"},
    "Public Speaking": {"public speaking"},
}

# Pre-compile one regex per alias for speed: matches the alias as a whole
# word/phrase, not as a substring of a longer word (so "sap" doesn't match
# inside "sapling").
_COMPILED = {
    display_name: [re.compile(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])") for alias in aliases]
    for display_name, aliases in SKILL_ALIASES.items()
}


def extract_skill_gaps(resume_text: str, jd_text: str, top_n: int = 10) -> dict:
    """
    Find which curated skills the JD mentions, and split them into ones
    present vs missing from the resume -- by regex matching directly
    against the text, not the TF-IDF vocabulary.

    Parameters
    ----------
    resume_text, jd_text : str (cleaned or raw text both work fine)
    top_n : cap on the number of missing skills returned

    Returns
    -------
    dict with:
        missing_skills : [display_name, ...] -- JD asks for it, resume lacks it
        present_skills : [display_name, ...] -- JD asks for it, resume has it
    """
    jd_lower = f" {jd_text.lower()} "
    resume_lower = f" {resume_text.lower()} "

    missing, present = [], []
    for display_name, patterns in _COMPILED.items():
        in_jd = any(p.search(jd_lower) for p in patterns)
        if not in_jd:
            continue
        in_resume = any(p.search(resume_lower) for p in patterns)
        (present if in_resume else missing).append(display_name)

    return {"missing_skills": missing[:top_n], "present_skills": present}


if __name__ == "__main__":
    # Quick offline smoke test -- confirms it catches a skill even when
    # that word would be entirely absent from a small training vocabulary.
    resume = "Experienced developer with Python and Docker background."
    jd = "Looking for someone skilled in Python, Kafka, and Kubernetes for our backend team."
    result = extract_skill_gaps(resume, jd)
    print("Missing:", result["missing_skills"])
    print("Present:", result["present_skills"])
