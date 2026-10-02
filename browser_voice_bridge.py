"""Browser voice bridge for Jarvis (no paid phone number required).

Flow:
1) Open /call from your phone browser (local IP or ngrok URL).
2) Browser captures speech using Web Speech API.
3) Text is sent to /api/ask.
4) Jarvis reply is spoken back by browser TTS.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

logger = logging.getLogger("browser_voice_bridge")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

CALL_PAGE_HTML = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Jarvis Phone Call</title>
    <style>
        :root {
            --bg: #08131a;
            --panel: #0e1d27;
            --line: #1d3b4d;
            --accent: #35d7ff;
            --accent2: #00ffb3;
            --text: #d9f6ff;
            --muted: #83a9b8;
            --warn: #ffd166;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            font-family: Segoe UI, Tahoma, sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at 15% 20%, #103145 0%, transparent 40%),
                radial-gradient(circle at 85% 80%, #0f2a3a 0%, transparent 35%),
                linear-gradient(160deg, #050c11 0%, #0a1a24 55%, #061019 100%);
            display: grid;
            place-items: center;
            padding: 16px;
        }
        .card {
            width: min(680px, 100%);
            border: 1px solid var(--line);
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(18,40,54,.95), rgba(9,24,33,.92));
            box-shadow: 0 0 40px rgba(0, 220, 255, .12);
            padding: 18px;
        }
        h1 {
            margin: 0 0 8px;
            font-size: 1.5rem;
            letter-spacing: .04em;
        }
        .sub {
            color: var(--muted);
            margin-bottom: 14px;
            font-size: .95rem;
        }
        .row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }
        button {
            border: 1px solid var(--line);
            border-radius: 999px;
            padding: 10px 14px;
            color: var(--text);
            background: #143244;
            font-weight: 600;
        }
        button.primary { border-color: #2dbce0; background: #0f4d66; }
        button.stop { border-color: #4b5e67; background: #26383f; }
        .status {
            margin: 8px 0 14px;
            color: var(--warn);
            font-size: .95rem;
        }
        .log {
            border: 1px solid var(--line);
            border-radius: 12px;
            background: rgba(5, 14, 20, .85);
            max-height: 48vh;
            overflow: auto;
            padding: 12px;
            font-size: .95rem;
            line-height: 1.45;
        }
        .u { color: var(--accent2); margin-top: 10px; }
        .j { color: var(--accent); margin-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Jarvis Phone Call</h1>
        <div class="sub">Tap Start Listening, speak your command, and hear the reply.</div>
        <div class="row">
            <button id="startBtn" class="primary">Start Listening</button>
            <button id="stopBtn" class="stop">Stop</button>
        </div>
        <div id="status" class="status">Idle</div>
        <div id="log" class="log"></div>
    </div>

    <script>
        const logEl = document.getElementById('log');
        const statusEl = document.getElementById('status');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');

        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        let listening = false;

        function append(kind, text) {
            const p = document.createElement('div');
            p.className = kind;
            p.textContent = (kind === 'u' ? 'You: ' : 'Jarvis: ') + text;
            logEl.appendChild(p);
            logEl.scrollTop = logEl.scrollHeight;
        }

        function speak(text) {
            if (!('speechSynthesis' in window)) return;
            const utter = new SpeechSynthesisUtterance(text);
            utter.rate = 1;
            utter.pitch = 1;
            speechSynthesis.cancel();
            speechSynthesis.speak(utter);
        }

        async function askJarvis(text) {
            try {
                const res = await fetch('/api/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                const data = await res.json();
                const reply = data.reply || 'Command received.';
                append('j', reply);
                speak(reply);
            } catch (e) {
                append('j', 'Network error while contacting Jarvis.');
            }
        }

        function startListening() {
            if (!SR) {
                statusEl.textContent = 'Speech recognition not supported. Use Chrome/Edge on Android.';
                return;
            }
            if (!recognition) {
                recognition = new SR();
                recognition.lang = 'en-IN';
                recognition.interimResults = false;
                recognition.continuous = false;

                recognition.onstart = () => {
                    listening = true;
                    statusEl.textContent = 'Listening...';
                };

                recognition.onresult = (event) => {
                    const text = (event.results?.[0]?.[0]?.transcript || '').trim();
                    if (!text) return;
                    append('u', text);
                    statusEl.textContent = 'Processing...';
                    askJarvis(text).finally(() => {
                        if (listening) statusEl.textContent = 'Tap Start Listening for next command';
                    });
                };

                recognition.onerror = (event) => {
                    statusEl.textContent = 'Speech error: ' + event.error;
                };

                recognition.onend = () => {
                    listening = false;
                };
            }
            recognition.start();
        }

        function stopListening() {
            listening = false;
            if (recognition) recognition.stop();
            speechSynthesis.cancel();
            statusEl.textContent = 'Stopped';
        }

        startBtn.addEventListener('click', startListening);
        stopBtn.addEventListener('click', stopListening);
    </script>
</body>
</html>
"""


class CapturingVoiceEngine:
    """Minimal voice engine adapter that captures spoken text from CommandHandler."""

    def __init__(self) -> None:
        self.last_response = ""

    def speak(self, text: str, *args: Any, **kwargs: Any) -> None:
        self.last_response = str(text)

    def listen(self, *args: Any, **kwargs: Any) -> str:
        return ""

    def force_stop(self) -> None:
        return


class JarvisCallBridge:
    """Creates and uses the existing Jarvis command pipeline for phone calls."""

    def __init__(self, config_path: str = "config.json") -> None:
        self.voice = CapturingVoiceEngine()
        self.config = self._load_config(config_path)
        self.handler = self._build_command_handler()

    def _load_config(self, config_path: str) -> dict:
        cfg_file = Path(config_path)
        if not cfg_file.exists():
            logger.warning("Config not found at %s. Using defaults.", cfg_file)
            return {}
        with cfg_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _build_command_handler(self):
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
            logger.info("Jarvis command handler initialized.")
            return handler
        except Exception as exc:
            logger.exception("Failed to initialize full Jarvis pipeline: %s", exc)
            return None

    def respond(self, text: str) -> str:
        query = (text or "").strip()
        if not query:
            return "I did not catch that. Please say that again."

        if self.handler is None:
            return f"I heard: {query}. Jarvis command system is not initialized yet."

        self.voice.last_response = ""

        try:
            self.handler.process_command(query)
            if self.voice.last_response:
                return self.voice.last_response

            # Fallback path for generic conversational text.
            ai = getattr(self.handler, "ai_assistant", None)
            if ai is not None:
                ai_reply = ai.query(query)
                if ai_reply:
                    return str(ai_reply)

            return "Command received."
        except Exception as exc:
            logger.exception("Error processing phone command: %s", exc)
            return "I hit an internal error while processing that request."


app = Flask(__name__)
bridge = JarvisCallBridge(config_path=os.getenv("JARVIS_CONFIG", "config.json"))


@app.route("/health", methods=["GET"])
def health() -> dict:
    return {"status": "ok"}


@app.route("/call", methods=["GET"])
def call_page() -> str:
    return CALL_PAGE_HTML


@app.route("/api/ask", methods=["POST"])
def api_ask():
    expected_token = os.getenv("JARVIS_BRIDGE_TOKEN")
    provided_token = request.headers.get("Authorization", "").replace("Bearer ", "", 1).strip()
    if not expected_token or provided_token != expected_token:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()
    logger.info("Phone speech text: %s", text)

    if not text:
        return jsonify({"reply": "I did not catch that. Please try again."}), 400

    reply = bridge.respond(text)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    host = os.getenv("BRIDGE_HOST", "127.0.0.1")
    port = int(os.getenv("BRIDGE_PORT", "5050"))
    logger.info("Starting browser voice bridge on %s:%s", host, port)
    app.run(host=host, port=port, debug=False)
