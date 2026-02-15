#!/usr/bin/env python3
"""Python web server for Majestic RP legal portal (no Node.js required)."""

from __future__ import annotations

import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT / "public"
PORT = int(os.getenv("PORT", "3000"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

SYSTEM_PROMPT = (
    "Ты — юридический AI-ассистент проекта Majestic RP. "
    "Объясняй нормы простым языком, но обязательно указывай: "
    "1) конкретную статью/пункт (если известен), "
    "2) суть нарушения, "
    "3) пример санкции, "
    "4) пометку, что финальное решение принимает уполномоченный сотрудник. "
    "Если данных недостаточно — прямо скажи, что нужна уточняющая информация."
)


def json_response(handler: BaseHTTPRequestHandler, code: int, payload: dict) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def ask_gemini(question: str) -> tuple[int, dict]:
    if not GEMINI_API_KEY:
        return 500, {"error": "GEMINI_API_KEY is not configured on server."}

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\nВопрос: {question}"}],
            }
        ]
    }

    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
            answer = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text")
            )
            if not answer:
                return 502, {"error": "Empty response from Gemini."}
            return 200, {"answer": answer}
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
            msg = parsed.get("error", {}).get("message", "Gemini API error.")
        except json.JSONDecodeError:
            msg = body or "Gemini API error."
        return exc.code, {"error": msg}
    except Exception as exc:  # network/runtime
        return 500, {"error": "Failed to reach Gemini API.", "details": str(exc)}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/ask":
            json_response(self, 404, {"error": "Not found."})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            json_response(self, 400, {"error": "Invalid JSON body."})
            return

        question = str(body.get("question", "")).strip()
        if not question:
            json_response(self, 400, {"error": "Question is required."})
            return

        code, payload = ask_gemini(question)
        json_response(self, code, payload)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", ""}:
            return self._send_file(PUBLIC_DIR / "index.html")

        clean = self.path.lstrip("/").split("?", 1)[0]
        target = (PUBLIC_DIR / clean).resolve()

        if not str(target).startswith(str(PUBLIC_DIR.resolve())):
            self.send_error(403)
            return

        if target.exists() and target.is_file():
            return self._send_file(target)

        return self._send_file(PUBLIC_DIR / "index.html")

    def _send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404)
            return

        content = path.read_bytes()
        mime, _ = mimetypes.guess_type(str(path))
        self.send_response(200)
        self.send_header("Content-Type", f"{mime or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Majestic legal portal running on http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
