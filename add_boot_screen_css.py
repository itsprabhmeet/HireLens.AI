path = "frontend/src/index.css"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor = '''.status-dot-connecting {
  background: var(--text-muted);
  animation: pulseDotConnecting 1.4s ease-in-out infinite;
}'''

addition = '''

.engine-boot-screen {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  background: var(--bg-canvas);
  padding: 24px;
  text-align: center;
}

.engine-boot-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: var(--gradient-primary, var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  animation: engineBootPulse 1.6s ease-in-out infinite;
}

@keyframes engineBootPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.08); opacity: 0.85; }
}

.engine-boot-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
}

.engine-boot-subtitle {
  font-size: 0.85rem;
  color: var(--text-muted);
  max-width: 360px;
  line-height: 1.5;
}

.engine-boot-spinner {
  animation: spin 1s linear infinite;
}'''

if addition.strip() in content:
    print("Already patched -- no change made.")
elif anchor not in content:
    print("NO MATCH FOUND -- aborting, nothing changed.")
else:
    content = content.replace(anchor, anchor + addition, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCHED SUCCESSFULLY")