"""Receptor HTTP local para demonstrar o envelope do Teams Workflows."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


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
        server.serve_forever()
