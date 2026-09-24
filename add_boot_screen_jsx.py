path = "frontend/src/App.jsx"
with open(path, encoding="utf-8") as f:
    content = f.read()

old = '''  return (
    <div className="app-layout">
      {/* Top Navigation */}
      <Navbar'''

new = '''  if (!backendChecked) {
    return (
      <div className="engine-boot-screen">
        <div className="engine-boot-icon-wrapper">
          <Loader2 size={28} className="engine-boot-spinner" color="#ffffff" />
        </div>
        <div className="engine-boot-title">Waking up the engine...</div>
        <div className="engine-boot-subtitle">
          The AI models are loading. This can take up to a minute if the server has been idle.
        </div>
      </div>
    );
  }

  return (
    <div className="app-layout">
      {/* Top Navigation */}
      <Navbar'''

if old not in content:
    print("NO MATCH FOUND -- aborting, nothing changed.")
else:
    content = content.replace(old, new, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED SUCCESSFULLY")