"""
job_fetcher.py
---------------
Best-effort job description extraction from a URL. Tries structured
JobPosting schema.org JSON-LD first (most reliable -- used by many ATS
platforms like Greenhouse, Lever, Workday, SmartRecruiters), then falls
back to a generic "biggest text block" heuristic. Known-hostile domains
(LinkedIn, Indeed, etc.) are short-circuited immediately with a clear
message instead of wasting a request that's guaranteed to be blocked or
return a login wall.

Usage:
    from job_fetcher import fetch_job_description_from_url
    result = fetch_job_description_from_url(url)
    if result["success"]:
        jd_text = result["text"]
    else:
        # show result["message"] and fall back to manual paste
        ...
"""

import json
import logging
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

REQUEST_TIMEOUT = 10  # seconds

# Domains known to actively block automated fetching or require a login to
# see the full posting. We short-circuit these immediately with a clear
# message rather than making a request that's guaranteed to fail or return
# a login wall / partial content.
BLOCKED_DOMAINS = {
    "linkedin.com": "LinkedIn blocks automated access to job postings and requires a login to view full details.",
    "indeed.com": "Indeed blocks automated access for most job postings.",
    "glassdoor.com": "Glassdoor blocks automated access to job postings.",
    "naukri.com": "Naukri blocks automated access to job postings.",
}


def _domain_of(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def _is_known_blocked(url: str):
    domain = _domain_of(url)
    for blocked, message in BLOCKED_DOMAINS.items():
        if domain == blocked or domain.endswith("." + blocked):
            return message
    return None


def _extract_from_json_ld(soup: BeautifulSoup):
    """
    Many ATS platforms embed a schema.org JobPosting object as JSON-LD --
    structured data meant to be machine-read. This is the most reliable
    extraction path when present.
    """
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except Exception:
            continue

        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            item_type = item.get("@type", "")
            is_job_posting = (
                "JobPosting" in item_type if isinstance(item_type, list) else item_type == "JobPosting"
            )
            if is_job_posting and item.get("description"):
                desc_soup = BeautifulSoup(item["description"], "html.parser")
                text = desc_soup.get_text(separator="\n").strip()
                if len(text) > 100:
                    return text
    return None


def _extract_generic(soup: BeautifulSoup):
    """
    Fallback heuristic: strip obvious non-content elements, then find the
    element with the most visible text -- usually the job description body
    on simpler sites without structured data.
    """
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "svg", "form"]):
        tag.decompose()

    best_text = ""
    for el in soup.find_all(["article", "main", "div", "section"]):
        text = el.get_text(separator="\n").strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        if len(text) > len(best_text):
            best_text = text

    # Guard against grabbing an entire page's nav/boilerplate soup if no
    # good container was found -- require a reasonable minimum length.
    return best_text if len(best_text) > 200 else None


def fetch_job_description_from_url(url: str) -> dict:
    """
    Best-effort fetch + extraction of a job description from a URL.

    Returns
    -------
    dict with:
        success : bool
        text    : str (extracted JD text, empty if failed)
        message : str (human-readable status/explanation)
        source  : "structured" | "generic" | None
    """
    url = url.strip()
    if not url:
        return {"success": False, "text": "", "message": "No URL provided.", "source": None}

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    blocked_reason = _is_known_blocked(url)
    if blocked_reason:
        return {
            "success": False,
            "text": "",
            "message": f"{blocked_reason} Please copy the job description text and paste it directly instead.",
            "source": None,
        }

    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Job URL fetch failed: {e}")
        return {
            "success": False,
            "text": "",
            "message": (
                "Couldn't reach that page (it may be blocking automated access, require a "
                "login, or the link may be incorrect). Please paste the job description text instead."
            ),
            "source": None,
        }

    soup = BeautifulSoup(response.text, "html.parser")

    structured_text = _extract_from_json_ld(soup)
    if structured_text:
        return {"success": True, "text": structured_text, "message": "Extracted successfully.", "source": "structured"}

    generic_text = _extract_generic(soup)
    if generic_text:
        return {
            "success": True,
            "text": generic_text,
            "message": (
                "Extracted using a best-effort method -- please double-check it looks right, "
                "some pages include extra boilerplate text."
            ),
            "source": "generic",
        }

    return {
        "success": False,
        "text": "",
        "message": "Couldn't find a clear job description on that page. Please paste the text directly instead.",
        "source": None,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python job_fetcher.py <url>")
        sys.exit(1)
    result = fetch_job_description_from_url(sys.argv[1])
    print(f"Success: {result['success']}")
    print(f"Source:  {result['source']}")
    print(f"Message: {result['message']}")
    print(f"\n--- Extracted text ({len(result['text'])} chars) ---\n")
    print(result["text"][:2000])
