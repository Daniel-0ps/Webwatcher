from flask import Flask, render_template_string
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

TEMPLATE = """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <title>WebWatcher - Test dynamique</title>
  <style>
    .banner{background:#fee;padding:8px}
    main{max-width:60ch;margin:2rem auto;font-family:system-ui,sans-serif}
    #ts{font-size:.9rem;color:#666}
  </style>
</head>
<body>
  <div class="banner">
    <strong>Bandeau dynamique</strong> — à ignorer pendant les tests
    <div id="ts">{{ now }}</div>
  </div>
  <main>
    <h1>Page de test (Flask)</h1>
    <p id="content">{{ content }}</p>
  </main>
</body>
</html>"""

CONTENT_FILE = Path("data/content.txt")

def read_content() -> str:
    if CONTENT_FILE.exists():
        return CONTENT_FILE.read_text(encoding="utf-8").strip()
    return "Version 1 — Contenu principal."

@app.route("/")
def home():
    return render_template_string(
        TEMPLATE,
        now=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        content=read_content(),
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
