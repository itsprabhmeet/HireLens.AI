path = "api.py"
with open(path, encoding="utf-8") as f:
    content = f.read()

old = '''                "order": "viewCount",
                "videoDuration": "medium",'''

new = '''                "order": "relevance",
                "videoDuration": "medium",'''

if old not in content:
    print("NO MATCH FOUND -- aborting, nothing changed.")
else:
    content = content.replace(old, new, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED SUCCESSFULLY")