"""
Ollama-compatible proxy that routes requests into Jarvis command handling.

Use this when a mobile app (e.g. Off Grid AI) expects an Ollama endpoint,
but you want commands to execute through Jarvis modules.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, request, stream_with_context

logger = logging.getLogger("offgrid_jarvis_proxy")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class CapturingVoiceEngine:
    """Captures spoken output instead of playing it on desktop speakers."""

    def __init__(self) -> None:
        self.last_response = ""

    def speak(self, text: str, *args: Any, **kwargs: Any) -> None:
        self.last_response = str(text)

    def listen(self, *args: Any, **kwargs: Any) -> str:
        return ""

    def force_stop(self) -> None:
        return


class JarvisBridge:
    """Bootstraps Jarvis command handler and executes text requests."""

    def __init__(self, config_path: str = "config.json") -> None:
        self.config_path = config_path
        self.voice = CapturingVoiceEngine()
        self.config = self._load_config(config_path)
        self.handler = self._build_handler()

    def _load_config(self, config_path: str) -> dict:
        cfg = Path(config_path)
        if not cfg.exists():
            logger.warning("Config not found at %s; using defaults.", cfg)
            return {}
        with cfg.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _build_handler(self):
        try:
            from modules.ai_assistant import AIAssistant
            from modules.app_controller import ApplicationController
            from modules.command_handler import CommandHandler
            from modules.email_manager import EmailManager

            ai_assistant = AIAssistant(self.config)
            app_controller = ApplicationController(self.config)
            email_manager = EmailManager(self.config)

            handler = CommandHandler(
                voice_engine=self.voice,
                system_controller=None,
                app_controller=app_controller,
                ai_assistant=ai_assistant,
                email_manager=email_manager,
            )
            logger.info("Jarvis command handler initialized for Off Grid proxy.")
            return handler
        except Exception as exc:
            logger.exception("Failed to initialize Jarvis handler: %s", exc)
            return None

    def run_text(self, text: str) -> str:
        query = (text or "").strip()
        if not query:
            return "I did not catch that."

        if self.handler is None:
            return "Jarvis command handler is not initialized yet."

        self.voice.last_response = ""

        try:
            self.handler.process_command(query)

            if self.voice.last_response:
                return self.voice.last_response

            ai = getattr(self.handler, "ai_assistant", None)
            if ai is not None:
                ai_reply = ai.query(query)
                if ai_reply:
                    return str(ai_reply)

            return "Command received."
        except Exception as exc:
            logger.exception("Error executing query '%s': %s", query, exc)
            return "I hit an internal error while handling that request."


app = Flask(__name__)
bridge = JarvisBridge(config_path=os.getenv("JARVIS_CONFIG", "config.json"))
MODEL_NAME = os.getenv("OFFGRID_MODEL_NAME", "jarvis-assistant")
PROXY_TOKEN = os.getenv("JARVIS_PROXY_TOKEN")


@app.before_request
def require_proxy_auth():
    """Protect command execution endpoints with a bearer token."""
    if request.path in {"/api/generate", "/api/chat", "/v1/chat/completions", "/v1/completions"}:
        provided = request.headers.get("Authorization", "").replace("Bearer ", "", 1).strip()
        if not PROXY_TOKEN or provided != PROXY_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
    return None


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _extract_user_text(payload: dict) -> str:
    """Extract latest user text from Ollama/OpenAI-style payloads."""

    def _from_content_field(content: Any) -> str:
        if isinstance(content, str):
            return content.strip()

        # OpenAI-style multimodal content blocks
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    if item.strip():
                        parts.append(item.strip())
                    continue

                if isinstance(item, dict):
                    text_val = item.get("text") or item.get("input_text") or item.get("content")
                    if isinstance(text_val, str) and text_val.strip():
                        parts.append(text_val.strip())

            return " ".join(parts).strip()

        if isinstance(content, dict):
            text_val = (
                content.get("text")
                or content.get("input_text")
                or content.get("content")
                or content.get("query")
                or content.get("prompt")
            )
            if isinstance(text_val, str):
                return text_val.strip()

        return ""

    messages = payload.get("messages", [])

    if isinstance(messages, list) and messages:
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "user":
                extracted = _from_content_field(msg.get("content", ""))
                if extracted:
                    return extracted

    prompt = payload.get("prompt", "")
    if isinstance(prompt, str):
        if prompt.strip():
            return prompt.strip()

    # Additional client variants
    direct = payload.get("input") or payload.get("query") or payload.get("text")
    if isinstance(direct, str):
        return direct.strip()

    if isinstance(direct, list):
        return _from_content_field(direct)

    return ""


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


@app.route("/", methods=["GET"])
def root() -> dict:
    return {"service": "offgrid-jarvis-ollama-proxy", "status": "ok"}


@app.route("/api/version", methods=["GET"])
def api_version() -> dict:
    return {"version": "0.1.0"}


@app.route("/api/tags", methods=["GET"])
def api_tags() -> dict:
    return {
        "models": [
            {
                "name": MODEL_NAME,
                "model": MODEL_NAME,
                "modified_at": _iso_now(),
                "size": 0,
                "digest": "jarvis-proxy",
                "details": {
                    "format": "jarvis-proxy",
                    "family": "jarvis",
                    "parameter_size": "n/a",
                    "quantization_level": "n/a",
                },
            }
        ]
    }


@app.route("/api/generate", methods=["POST"])
def api_generate():
    payload = request.get_json(silent=True) or {}
    prompt = str(payload.get("prompt", "")).strip()
    response_text = bridge.run_text(prompt)
    stream = _as_bool(payload.get("stream", False))

    if stream:
        def _gen():
            yield json.dumps(
                {
                    "model": payload.get("model", MODEL_NAME),
                    "created_at": _iso_now(),
                    "response": response_text,
                    "done": False,
                }
            ) + "\n"
            yield json.dumps(
                {
                    "model": payload.get("model", MODEL_NAME),
                    "created_at": _iso_now(),
                    "response": "",
                    "done": True,
                }
            ) + "\n"

        return Response(stream_with_context(_gen()), mimetype="application/x-ndjson")

    return jsonify(
        {
            "model": payload.get("model", MODEL_NAME),
            "created_at": _iso_now(),
            "response": response_text,
            "done": True,
        }
    )


@app.route("/api/chat", methods=["POST"])
def api_chat():
    payload = request.get_json(silent=True) or {}
    user_text = _extract_user_text(payload)
    stream = _as_bool(payload.get("stream", False))

    response_text = bridge.run_text(user_text)

    if stream:
        def _gen():
            yield json.dumps(
                {
                    "model": payload.get("model", MODEL_NAME),
                    "created_at": _iso_now(),
                    "message": {"role": "assistant", "content": response_text},
                    "done": False,
                }
            ) + "\n"
            yield json.dumps(
                {
                    "model": payload.get("model", MODEL_NAME),
                    "created_at": _iso_now(),
                    "message": {"role": "assistant", "content": ""},
                    "done": True,
                }
            ) + "\n"

        return Response(stream_with_context(_gen()), mimetype="application/x-ndjson")

    return jsonify(
        {
            "model": payload.get("model", MODEL_NAME),
            "created_at": _iso_now(),
            "message": {"role": "assistant", "content": response_text},
            "done": True,
        }
    )


@app.route("/v1/models", methods=["GET"])
def v1_models():
    return jsonify(
        {
            "object": "list",
            "data": [
                {
                    "id": MODEL_NAME,
                    "object": "model",
                    "created": int(datetime.now(timezone.utc).timestamp()),
                    "owned_by": "jarvis-proxy",
                }
            ],
        }
    )


@app.route("/v1/chat/completions", methods=["POST"])
def v1_chat_completions():
    payload = request.get_json(silent=True) or {}
    user_text = _extract_user_text(payload)
    response_text = bridge.run_text(user_text)
    stream = _as_bool(payload.get("stream", False))

    if stream:
        def _gen():
            first = {
                "id": f"chatcmpl-{int(datetime.now(timezone.utc).timestamp())}",
                "object": "chat.completion.chunk",
                "created": int(datetime.now(timezone.utc).timestamp()),
                "model": payload.get("model", MODEL_NAME),
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": response_text},
                        "finish_reason": None,
                    }
                ],
            }
            done = {
                "id": f"chatcmpl-{int(datetime.now(timezone.utc).timestamp())}",
                "object": "chat.completion.chunk",
                "created": int(datetime.now(timezone.utc).timestamp()),
                "model": payload.get("model", MODEL_NAME),
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }

            yield f"data: {json.dumps(first)}\n\n"
            yield f"data: {json.dumps(done)}\n\n"
            yield "data: [DONE]\n\n"

        return Response(stream_with_context(_gen()), mimetype="text/event-stream")

    return jsonify(
        {
            "id": f"chatcmpl-{int(datetime.now(timezone.utc).timestamp())}",
            "object": "chat.completion",
            "created": int(datetime.now(timezone.utc).timestamp()),
            "model": payload.get("model", MODEL_NAME),
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": response_text},
                    "finish_reason": "stop",
                }
            ],
        }
    )


@app.route("/v1/completions", methods=["POST"])
def v1_completions():
    payload = request.get_json(silent=True) or {}
    user_text = _extract_user_text(payload)
    response_text = bridge.run_text(user_text)

    return jsonify(
        {
            "id": f"cmpl-{int(datetime.now(timezone.utc).timestamp())}",
            "object": "text_completion",
            "created": int(datetime.now(timezone.utc).timestamp()),
            "model": payload.get("model", MODEL_NAME),
            "choices": [{"index": 0, "text": response_text, "finish_reason": "stop"}],
        }
    )


@app.errorhandler(404)
def not_found(_err):
    logger.warning("404 path requested: %s", request.path)
    return jsonify({"error": "not_found", "path": request.path}), 404


if __name__ == "__main__":
    host = os.getenv("PROXY_HOST", "127.0.0.1")
    port = int(os.getenv("PROXY_PORT", "11435"))
    logger.info("Starting Off Grid Jarvis proxy on %s:%s", host, port)
    app.run(host=host, port=port, debug=False)
