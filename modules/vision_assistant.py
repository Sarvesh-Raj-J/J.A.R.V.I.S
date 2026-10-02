"""
Vision Assistant Module
Captures one webcam frame and gets a fast scene description from Ollama VLM.
"""

import base64
import logging
import os
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)

try:
    import cv2  # type: ignore
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class VisionAssistant:
    """Handles quick single-image scene descriptions using a local VLM."""

    def __init__(self, config: Dict):
        self.config = config or {}
        vision_cfg = self.config.get("vision", {})

        self.enabled = vision_cfg.get("enabled", True)
        self.model = vision_cfg.get("model", "moondream")
        self.api_url = os.getenv(
            "OLLAMA_VISION_URL",
            os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"),
        )
        self.camera_index = int(vision_cfg.get("camera_index", 0))
        self.frame_width = int(vision_cfg.get("frame_width", 640))
        self.frame_height = int(vision_cfg.get("frame_height", 480))
        self.timeout = int(vision_cfg.get("timeout", 45))
        self.default_prompt = vision_cfg.get(
            "prompt",
            "Describe this scene in 2 short sentences. Focus on important objects and actions.",
        )

        logger.info("VisionAssistant initialized with model '%s'", self.model)

    def describe_scene(self, prompt: Optional[str] = None) -> str:
        """Capture one image and return a short scene description."""
        if not self.enabled:
            return "Vision mode is disabled in config."

        if not CV2_AVAILABLE:
            return "OpenCV is not installed. Please install opencv-python."

        frame_b64 = self._capture_frame_base64()
        if not frame_b64:
            return "I could not access the camera."

        query_prompt = (prompt or "").strip() or self.default_prompt

        payload = {
            "model": self.model,
            "prompt": query_prompt,
            "images": [frame_b64],
            "stream": False,
            "temperature": 0.2,
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=self.timeout)
            if response.status_code != 200:
                logger.warning("Vision request failed with status %s", response.status_code)
                return "Vision model is not ready. Please run ollama pull moondream and try again."

            data = response.json()
            text = str(data.get("response", "")).strip()
            if text:
                return text

            return "I captured the image, but the model returned an empty response."
        except requests.RequestException as exc:
            logger.warning("Vision request error: %s", exc)
            return "I could not reach Ollama. Please ensure Ollama is running."
        except Exception as exc:
            logger.error("Unexpected vision error: %s", exc)
            return "I hit an unexpected error while describing the scene."

    def _capture_frame_base64(self) -> Optional[str]:
        """Capture one webcam frame and return base64-encoded JPEG."""
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            return None

        try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)

            # Warm up camera to improve first-frame reliability.
            frame = None
            for _ in range(4):
                ok, current = cap.read()
                if ok:
                    frame = current

            if frame is None:
                return None

            ok, encoded = cv2.imencode(
                ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            )
            if not ok:
                return None

            return base64.b64encode(encoded.tobytes()).decode("utf-8")
        finally:
            cap.release()
