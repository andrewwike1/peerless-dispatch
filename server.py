from flask import Flask, request, jsonify, Response
import os
import threading

app = Flask(__name__)

UPDATE_TOKEN = os.environ.get("UPDATE_TOKEN", "changeme")
current_html = None
html_lock = threading.Lock()
HTML_FILE = "dashboard.html"

if os.path.exists(HTML_FILE):
    with open(HTML_FILE, "r") as f:
        current_html = f.read()

LOADING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="60">
<title>Peerless Dispatch</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0f1117;color:#e8eaf0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;gap:20px}
  h2{color:#ff3333;font-size:1.6rem}
  p{color:#8892a4;font-size:.95rem}
  .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#ff3333;
    animation:pulse 1.4s infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}
</style>
</head>
<body>
  <span class="dot"></span>
  <h2>Peerless Dispatch Dashboard</h2>
  <p>Dashboard is being generated — auto-refreshes every 60 seconds.</p>
</body>
</html>"""


@app.route("/")
def index():
    with html_lock:
        html = current_html or LOADING_HTML
    return Response(html, mimetype="text/html")


@app.route("/update", methods=["POST"])
def update():
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {UPDATE_TOKEN}":
        return jsonify({"error": "unauthorized"}), 401

    html = request.get_data(as_text=True)
    if not html:
        return jsonify({"error": "empty body"}), 400

    with html_lock:
        global current_html
        current_html = html
        with open(HTML_FILE, "w") as f:
            f.write(html)

    return jsonify({"status": "updated", "bytes": len(html)})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
