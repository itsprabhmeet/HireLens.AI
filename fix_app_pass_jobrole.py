path = "frontend/src/App.jsx"
with open(path, encoding="utf-8") as f:
    content = f.read()

old = "<LearningRecommendations skillGaps={evalResult.skill_gaps} />"
new = "<LearningRecommendations skillGaps={evalResult.skill_gaps} jobRole={evalResult.predicted_category} />"

if old not in content:
    print("NO MATCH FOUND -- aborting, nothing changed.")
else:
    content = content.replace(old, new, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED SUCCESSFULLY")