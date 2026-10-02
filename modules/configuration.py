"""Configuration loading and local secret handling for Jarvis."""

from __future__ import annotations

import copy
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

DEFAULT_CONFIG: Dict[str, Any] = {
    "wake_phrases": ["hey jarvis", "jarvis"],
    "sleep_commands": ["sleep", "go to sleep", "standby"],
    "voice_settings": {"rate": 170, "volume": 1.0, "voice_index": 0},
    "voice_profiles": {"default": {"rate": 170, "volume": 1.0, "voice_index": 0}},
    "email": {
        "sender_email": "",
        "sender_password": "",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
    },
    "ollama": {
        "enabled": True,
        "model": "llama2",
        "api_url": "http://localhost:11434/api/generate",
        "context_aware": True,
        "max_context_messages": 10,
    },
    "logging": {"enabled": True, "log_file": "jarvis.log", "log_level": "INFO"},
}


def load_config(config_path: str | os.PathLike[str] | None = None) -> Dict[str, Any]:
    """Load local configuration and overlay supported environment variables."""
    path = Path(config_path or os.getenv("JARVIS_CONFIG", "config.json"))
    config = copy.deepcopy(DEFAULT_CONFIG)

    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as config_file:
                loaded = json.load(config_file)
            if not isinstance(loaded, dict):
                raise ValueError("configuration root must be a JSON object")
            _merge(config, loaded)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(f"Unable to load configuration from {path}: {exc}") from exc
    else:
        logger.info("No local config found at %s; using defaults", path)

    email = config.setdefault("email", {})
    email["sender_email"] = os.getenv("JARVIS_EMAIL", email.get("sender_email", ""))
    email["sender_password"] = os.getenv(
        "JARVIS_EMAIL_PASSWORD", email.get("sender_password", "")
    )
    ollama = config.setdefault("ollama", {})
    ollama["api_url"] = os.getenv("OLLAMA_URL", ollama.get("api_url"))
    return config


def _merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _merge(target[key], value)
        else:
            target[key] = value
