from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
from pathlib import Path
import json, os

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
VISITS_FILE = DATA_DIR / "visits.txt"

class Handler(BaseHTTPRequestHandler):
    def send_body(self, status, body, content_type="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health/live":
            return self.send_body(200, "LIVE")
        if self.path == "/health/ready":
            try:
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                with VISITS_FILE.open("a", encoding="utf-8"):
                    pass
                return self.send_body(200, "READY")
            except OSError:
                return self.send_body(503, "NOT READY")
        if self.path == "/api/visits":
            try:
                count = len(VISITS_FILE.read_text(encoding="utf-8").splitlines()) if VISITS_FILE.exists() else 0
                return self.send_body(200, json.dumps({"visits": count}), "application/json")
            except OSError:
                return self.send_body(500, json.dumps({"error": "Cannot read volume"}), "application/json")
        if self.path == "/visit":
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with VISITS_FILE.open("a", encoding="utf-8") as f:
                f.write(datetime.now(timezone.utc).isoformat() + "\n")
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return
        count = len(VISITS_FILE.read_text(encoding="utf-8").splitlines()) if VISITS_FILE.exists() else 0
        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Kubernetes Demo</title>
<style>body{{font-family:Arial;background:#edf3fb;color:#1d2c44;margin:0;min-height:100vh;display:grid;place-items:center}}
main{{background:white;padding:32px;border-radius:16px;max-width:650px;width:85%;box-shadow:0 12px 35px #1d2c441a}}
h1{{color:#1769aa}}.pill{{background:#e0f5e8;color:#17643a;border-radius:20px;padding:7px 12px;font-size:13px}}
a{{display:inline-block;background:#1769aa;color:white;padding:11px 16px;border-radius:8px;text-decoration:none}}
code{{background:#edf3fb;padding:3px 6px;border-radius:4px}}</style></head><body><main>
<span class="pill">KUBERNETES APP RUNNING</span><h1>Persistent Storage Demo</h1>
<p>This app runs in a Docker container on Kubernetes.</p><p><strong>Recorded visits:</strong> {count}</p>
<p><a href="/visit">Record a visit</a></p><h2>Health endpoints</h2>
<ul><li><code>/health/live</code> — liveness probe</li><li><code>/health/ready</code> — readiness probe</li>
<li><code>/api/visits</code> — visit count in JSON</li></ul>
<p>Visit timestamps are saved to <code>/data/visits.txt</code> on a persistent volume.</p></main></body></html>"""
        return self.send_body(200, page)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
