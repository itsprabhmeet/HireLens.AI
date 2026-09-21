path = "api.py"
with open(path, encoding="utf-8") as f:
    content = f.read()

changes = 0

old_func_sig = '''def fetch_youtube_tutorials(skill: str, max_results: int = 6) -> list:
    """
    Fetch top YouTube tutorial videos for a skill, sorted by view count.
    Requires YOUTUBE_API_KEY in a local .env file (see README).
    """
    if not YOUTUBE_API_KEY:
        logger.warning("YOUTUBE_API_KEY not set -- returning no tutorials.")
        return []

    try:
        search_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": f"{skill} tutorial",
                "type": "video",
                "maxResults": 10,
                "order": "viewCount",
                "relevanceLanguage": "en",
                "safeSearch": "strict",
                "key": YOUTUBE_API_KEY,
            },
            timeout=8,
        )'''

new_func_sig = '''def fetch_youtube_tutorials(skill: str, job_role: str = "", max_results: int = 6) -> list:
    """
    Fetch top YouTube tutorial videos for a skill, sorted by view count.
    Requires YOUTUBE_API_KEY in a local .env file (see README).

    Query is role-aware ("{skill} course for {job_role}") rather than a bare
    "{skill} tutorial" -- the latter tends to surface generic consumer
    content (e.g. "Networking" pulling WiFi-password videos). videoDuration
    is restricted to medium/long to exclude YouTube Shorts entirely, since
    short-form video is never a real course regardless of view count.
    """
    if not YOUTUBE_API_KEY:
        logger.warning("YOUTUBE_API_KEY not set -- returning no tutorials.")
        return []

    query = f"{skill} course for {job_role}" if job_role else f"{skill} course"

    try:
        search_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": 10,
                "order": "viewCount",
                "videoDuration": "medium",
                "relevanceLanguage": "en",
                "safeSearch": "strict",
                "key": YOUTUBE_API_KEY,
            },
            timeout=8,
        )'''

if old_func_sig in content:
    content = content.replace(old_func_sig, new_func_sig, 1)
    changes += 1

old_endpoint = '''@app.get("/api/youtube-tutorials")
def get_youtube_tutorials(skill: str):
    """Get top YouTube tutorial videos for a given skill name."""
    return {"skill": skill, "videos": fetch_youtube_tutorials(skill)}'''

new_endpoint = '''@app.get("/api/youtube-tutorials")
def get_youtube_tutorials(skill: str, job_role: str = ""):
    """Get top YouTube tutorial videos for a given skill name, tailored to a job role."""
    return {"skill": skill, "videos": fetch_youtube_tutorials(skill, job_role)}'''

if old_endpoint in content:
    content = content.replace(old_endpoint, new_endpoint, 1)
    changes += 1

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Applied {changes} of 2 expected changes.")