"""Receptor HTTP local para demonstrar o envelope do Teams Workflows."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock


class MockWorkflow(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/workflow":
            return self.send_error(404)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 2_000_000:
                return self.send_error(413)
            payload = json.loads(self.rfile.read(size))
            attachment = payload["attachments"][0]
            if (
                payload["type"] != "message"
                or attachment["contentType"]
                != "application/vnd.microsoft.card.adaptive"
                or attachment["content"]["type"] != "AdaptiveCard"
            ):
                return self.send_error(400)
        except (ValueError, KeyError, IndexError, TypeError):
            return self.send_error(400)
        if path := getattr(self.server, "card_path", None):
            with self.server.card_lock:
                pending = path.with_suffix(".tmp")
                try:
                    pending.write_text(json.dumps(payload), encoding="utf-8")
                    pending.replace(path)
                except OSError:
                    return self.send_error(500)
                self.server.last_card = payload
        else:
            self.server.last_card = payload
        self.send_response(202)
        self.end_headers()

    def do_GET(self):
        if self.path != "/last":
            return self.send_error(404)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(getattr(self.server, "last_card", None)).encode())

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    with ThreadingHTTPServer(("0.0.0.0", 8080), MockWorkflow) as server:
        if location := os.getenv("TEAMS_MOCK_CARD_FILE"):
            server.card_path = Path(location)
            server.card_lock = Lock()
            if server.card_path.exists():
                server.last_card = json.loads(server.card_path.read_bytes())
        server.serve_forever()
