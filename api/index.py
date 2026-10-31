import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import analyze_sentiment, generate_report


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.endswith("/health"):
            self._send_json(200, {"status": "ok", "pipeline": "ATB VoC Pipeline", "stages": 4})
            return
        self._send_json(200, {"status": "ok", "service": "ATB VoC Pipeline API"})

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            payload = {}

        if parsed.path.endswith("/analyze"):
            self._send_json(200, analyze_sentiment(payload.get("comment", "")))
            return

        if parsed.path.endswith("/report"):
            self._send_json(200, generate_report(payload))
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
