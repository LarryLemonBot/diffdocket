from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "index.html"
CSS_PATH = ROOT / "styles.css"


def _response(status: str, content_type: str, body: bytes):
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "public, max-age=300"),
    ]
    return status, headers, [body]


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path in {"", "/"}:
        status, headers, body = _response("200 OK", "text/html; charset=utf-8", HTML_PATH.read_bytes())
    elif path == "/styles.css":
        status, headers, body = _response("200 OK", "text/css; charset=utf-8", CSS_PATH.read_bytes())
    else:
        status, headers, body = _response("404 Not Found", "text/plain; charset=utf-8", b"Not found")

    start_response(status, headers)
    return body

