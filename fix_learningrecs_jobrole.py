path = "frontend/src/components/LearningRecommendations.jsx"
with open(path, encoding="utf-8") as f:
    content = f.read()

changes = 0

old_sig = "export default function LearningRecommendations({ skillGaps = {} }) {"
new_sig = "export default function LearningRecommendations({ skillGaps = {}, jobRole = '' }) {"
if old_sig in content:
    content = content.replace(old_sig, new_sig, 1)
    changes += 1

old_fetch = "const response = await fetch(`/api/youtube-tutorials?skill=${encodeURIComponent(skill)}`);"
new_fetch = "const response = await fetch(`/api/youtube-tutorials?skill=${encodeURIComponent(skill)}&job_role=${encodeURIComponent(jobRole)}`);"
if old_fetch in content:
    content = content.replace(old_fetch, new_fetch, 1)
    changes += 1

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Applied {changes} of 2 expected changes.")