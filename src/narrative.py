"""
narrative.py
------------
Rule-based narrative engine: turns the numeric analysis (fit score,
JD relevance, category alignment, matched/missing keywords, SHAP features)
into recruiter-style written feedback -- no external API, fully offline
and deterministic (same input always produces the same output).

Usage:
    from narrative import generate_narrative
    narrative = generate_narrative(result, predicted_category)
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# -- Deterministic phrase picker --------------------------------------------
def _pick(pool: list, seed_text: str) -> str:
    """
    Pick one phrase from a pool deterministically based on seed_text
    (e.g. the resume text), so the same resume+JD always produces the
    same wording, but different resumes get varied phrasing rather than
    always picking pool[0].
    """
    if not pool:
        return ""
    idx = sum(ord(c) for c in seed_text[:200]) % len(pool)
    return pool[idx]


def _clean_word(word: str) -> str:
    """Turn an underscore/raw TF-IDF token into a display-friendly phrase."""
    return word.replace("_", " ").strip()


def _join_list(terms: list) -> str:
    """Join a list of terms into a natural English list: 'a', 'a and b', 'a, b, and c'."""
    if not terms:
        return ""
    if len(terms) == 1:
        return terms[0]
    if len(terms) == 2:
        return f"{terms[0]} and {terms[1]}"
    return ", ".join(terms[:-1]) + f", and {terms[-1]}"


# -- Verdict ------------------------------------------------------------------
_VERDICT_EXCELLENT = [
    "This is a strong match -- the resume covers both the role category and the "
    "specific skills this job description calls for.",
    "A confident match. The resume's background lines up closely with what this "
    "job is asking for, both in role type and specific requirements.",
    "Strong alignment across the board -- this candidate looks well suited to "
    "this specific opening, not just the general job family.",
]

_VERDICT_GOOD = [
    "A solid match overall, though there are a few gaps worth flagging before "
    "moving forward.",
    "This resume holds up well against the job description, with some room "
    "for improvement in specific areas.",
    "Good alignment on the fundamentals, but a handful of requirements in the "
    "JD aren't clearly reflected in the resume yet.",
]

_VERDICT_PARTIAL = [
    "A partial match -- some relevant background is there, but significant "
    "parts of the job description aren't reflected in this resume.",
    "There's some overlap here, but this resume reads as only loosely aligned "
    "with what the job is asking for.",
    "Mixed signal: parts of the resume fit, but several core requirements from "
    "the JD don't show up.",
]

_VERDICT_WEAK = [
    "This resume does not look like a strong fit for this specific role -- "
    "very little of the job description is reflected in it.",
    "Weak match. Either the role category is different from what this JD is "
    "asking for, or the specific skills required aren't present.",
    "This resume and job description don't have much in common -- worth double "
    "checking this is the right role to screen this candidate against.",
]

_VERDICT_ALIGNMENT_CAVEAT = [
    " Notably, the resume doesn't even read as the same type of role as the "
    "job description -- that's a bigger flag than any single missing keyword.",
    " One thing stands out: the overall role type in the resume doesn't match "
    "what this job description is describing, independent of specific skills.",
]


def _build_verdict(fit_score: float, jd_relevance: float, category_alignment: float, seed_text: str) -> str:
    if fit_score >= 75:
        verdict = _pick(_VERDICT_EXCELLENT, seed_text)
    elif fit_score >= 55:
        verdict = _pick(_VERDICT_GOOD, seed_text)
    elif fit_score >= 35:
        verdict = _pick(_VERDICT_PARTIAL, seed_text)
    else:
        verdict = _pick(_VERDICT_WEAK, seed_text)

    # If category alignment is the clear weak link (much lower than relevance),
    # call that out explicitly -- it's a structurally different problem than
    # "missing a few keywords".
    if category_alignment < 30 and (jd_relevance - category_alignment) > 25:
        verdict += _pick(_VERDICT_ALIGNMENT_CAVEAT, seed_text)

    return verdict


# -- Strengths ------------------------------------------------------------------
_STRENGTHS_INTRO = [
    "The resume shows clear strength around {items}.",
    "Where this resume is strongest: {items}.",
    "Standout areas: {items} all show up clearly and carry real weight in the match.",
]

_STRENGTHS_WEAK_INTRO = [
    "There's a small amount of overlap around {items}, but it's not enough to "
    "carry a meaningful match on its own.",
    "The only common ground is {items} -- too thin to call a real strength.",
]

_NO_STRENGTHS = [
    "No standout keyword overlaps pulled the score up -- the match is thin across the board.",
]


def _build_strengths(matched_keywords: list, shap_positive: list, fit_score: float, seed_text: str, top_n: int = 5) -> str:
    # Prefer JD-weighted matches (already sorted by importance); fall back to
    # positive SHAP terms if matches are sparse.
    terms = [_clean_word(w) for w, _ in matched_keywords[:top_n]]
    if len(terms) < 3 and shap_positive:
        extra = [_clean_word(w) for w, _ in shap_positive if _clean_word(w) not in terms]
        terms += extra[: max(0, 3 - len(terms))]

    if not terms:
        return _pick(_NO_STRENGTHS, seed_text)

    items = _join_list(terms)
    # Below a low fit-score threshold, don't frame leftover matches as
    # "standout" -- that reads as contradicting the verdict.
    pool = _STRENGTHS_INTRO if fit_score >= 35 else _STRENGTHS_WEAK_INTRO
    template = _pick(pool, seed_text)
    return template.format(items=items)


# -- Gaps -----------------------------------------------------------------------
_GAPS_INTRO = [
    "The resume doesn't show any sign of {items} -- worth checking whether that's "
    "a true gap or just missing from the resume's wording.",
    "Missing from the resume, but present in the job description: {items}.",
    "The job description leans on {items}, none of which come through in this resume.",
]

_NO_GAPS = [
    "No significant JD requirements are missing from the resume -- good keyword coverage.",
]


def _build_gaps(missing_keywords: list, seed_text: str, top_n: int = 5) -> str:
    terms = [_clean_word(w) for w, _ in missing_keywords[:top_n]]
    if not terms:
        return _pick(_NO_GAPS, seed_text)

    items = _join_list(terms)
    template = _pick(_GAPS_INTRO, seed_text)
    return template.format(items=items)


# -- Suggestions ------------------------------------------------------------------
def _build_suggestions(missing_keywords: list, top_n: int = 3) -> str:
    top_missing = [_clean_word(w) for w, _ in missing_keywords[:top_n]]
    if not top_missing:
        return ""
    items = _join_list(top_missing)
    return (
        f"If this candidate genuinely has experience with {items}, making that "
        f"explicit in the resume would meaningfully raise the match against "
        f"this JD."
    )


# -- Interview Question Generator --------------------------------------------
_QUESTION_BANK = {
    "cloud": (
        "Cloud & Infrastructure",
        "Could you describe your hands-on experience with cloud providers (AWS/GCP/Azure) and automated CI/CD deployment pipelines?"
    ),
    "docker": (
        "Containerization",
        "How have you used Docker or container orchestration tools to ensure application reproducibility across environments?"
    ),
    "kubernetes": (
        "Kubernetes & Orchestration",
        "Can you walk us through how you manage cluster deployments, ingress, and auto-scaling in a Kubernetes environment?"
    ),
    "sql": (
        "Database Architecture",
        "Can you discuss a time you optimized a slow query or designed an efficient schema for a relational or NoSQL database?"
    ),
    "nosql": (
        "NoSQL Data Stores",
        "When would you choose a document or key-value store over a traditional SQL database, and what trade-offs did you encounter?"
    ),
    "microservices": (
        "System Design",
        "How do you approach inter-service communication, distributed tracing, and fault-tolerance when designing microservices?"
    ),
    "api": (
        "API Design & Integration",
        "What principles do you adhere to when building secure, scalable RESTful or GraphQL APIs for third-party consumption?"
    ),
    "machine learning": (
        "ML Engineering",
        "How do you handle feature engineering, model drift monitoring, and hyperparameter tuning in production ML pipelines?"
    ),
    "nlp": (
        "Natural Language Processing",
        "Which text representation and tokenization techniques or transformer architectures have you implemented for NLP tasks?"
    ),
    "react": (
        "Frontend State Management",
        "How do you manage complex application state and minimize unnecessary re-renders in modern component-based frontends?"
    ),
    "testing": (
        "Testing & Quality Assurance",
        "What is your strategy for unit, integration, and end-to-end test coverage to ensure regression-free releases?"
    ),
    "security": (
        "Application Security",
        "What measures do you take to safeguard applications against common vulnerabilities (e.g. OWASP Top 10, auth validation)?"
    ),
    "agile": (
        "Agile Delivery",
        "How do you manage sprint planning, technical debt prioritization, and cross-functional stakeholder communication?"
    ),
}


def generate_interview_questions(missing_keywords: list, max_questions: int = 4) -> list:
    """
    Generate tailored technical interview questions based on missing JD keywords.
    Helps recruiters probe candidate capabilities during screening interviews.

    Returns:
    --------
    list of dict: [{"skill": str, "category": str, "question": str}, ...]
    """
    questions = []
    used_topics = set()

    for word, _ in missing_keywords:
        w_clean = _clean_word(word).lower()
        # Check against question bank triggers
        for trigger, (category, q_text) in _QUESTION_BANK.items():
            if trigger in w_clean or w_clean in trigger:
                if category not in used_topics:
                    questions.append({
                        "skill": word,
                        "category": category,
                        "question": q_text,
                    })
                    used_topics.add(category)
                break
        if len(questions) >= max_questions:
            break

    # If fewer than 2 questions were matched, add custom contextual questions for top missing skills
    if len(questions) < max_questions:
        for word, _ in missing_keywords:
            w_clean = _clean_word(word)
            if not any(q["skill"].lower() == word.lower() for q in questions):
                questions.append({
                    "skill": word,
                    "category": f"Competency: {w_clean.title()}",
                    "question": f"The job requirement highlights '{w_clean}'. Can you discuss any past exposure, transferable skills, or how quickly you could get up to speed with this?",
                })
            if len(questions) >= max_questions:
                break

    return questions


# -- Public entry point ------------------------------------------------------------
def generate_narrative(result: dict, resume_text: str = "") -> dict:
    """
    Build the full human-style write-up from an explain_resume() result dict.

    Parameters
    ----------
    result : dict returned by explain.explain_resume()
    resume_text : str, used only as a deterministic seed for phrase variety

    Returns
    -------
    dict with keys: verdict, strengths, gaps, suggestions, interview_questions
    """
    seed_text = resume_text or result.get("predicted_category", "seed")

    fit_score = result.get("fit_score", 0.0)
    jd_relevance = result.get("jd_relevance", 0.0)
    category_alignment = result.get("category_alignment", 0.0)
    matched = result.get("matched_keywords", [])
    missing = result.get("missing_keywords", [])
    shap_positive = result.get("shap_features", {}).get("positive", [])

    verdict = _build_verdict(fit_score, jd_relevance, category_alignment, seed_text)
    strengths = _build_strengths(matched, shap_positive, fit_score, seed_text)
    gaps = _build_gaps(missing, seed_text)
    suggestions = _build_suggestions(missing)
    interview_questions = generate_interview_questions(missing)

    return {
        "verdict": verdict,
        "strengths": strengths,
        "gaps": gaps,
        "suggestions": suggestions,
        "interview_questions": interview_questions,
    }


if __name__ == "__main__":
    # Quick offline smoke test with fabricated data -- no models needed.
    fake_result = {
        "fit_score": 89.4,
        "jd_relevance": 84.3,
        "category_alignment": 95.0,
        "predicted_category": "Data Science",
        "matched_keywords": [("nlp", 0.9), ("machine learning", 0.8), ("python", 0.7)],
        "missing_keywords": [("cloud", 0.6), ("aws", 0.4)],
        "shap_features": {"positive": [("scikit", 0.3)], "negative": []},
    }
    out = generate_narrative(fake_result, resume_text="sample resume text for seeding")
    for k, v in out.items():
        print(f"{k.upper()}: {v}\n")