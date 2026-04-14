#!/usr/bin/env python3
"""Tiny dev server: serves repo files and handles POST /save to rewrite bubbles.jsonl.

Run from the repo root:
    python3 scripts/serve.py
Then open http://localhost:8765/?prune=1
"""
import http.server
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = 8765


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path != "/save":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            bubbles = data["bubbles"]
            assert isinstance(bubbles, list)
        except Exception as e:
            self.send_error(400, f"bad payload: {e}")
            return

        target = ROOT / "bubbles.jsonl"
        backup = target.with_suffix(".jsonl.bak")
        shutil.copy(target, backup)
        with target.open("w") as f:
            for b in bubbles:
                f.write(json.dumps(b, ensure_ascii=False) + "\n")
        payload = json.dumps({"saved": len(bubbles), "backup": str(backup.name)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    print(f"Serving {ROOT} on http://localhost:{PORT}")
    print(f"Open → http://localhost:{PORT}/?prune=1")
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
