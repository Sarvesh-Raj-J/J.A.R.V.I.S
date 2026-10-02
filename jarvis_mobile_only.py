"""
Jarvis Mobile Server - Lightweight version
Runs mobile server without the desktop UI
Perfect for headless operation or when you only need mobile control
"""

import json
import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import modules
from modules.voice_engine import VoiceEngine
from modules.app_controller import ApplicationController
from modules.email_manager import EmailManager
from modules.ai_assistant import AIAssistant
from modules.utilities import Utilities
from modules.command_handler import CommandHandler
from modules.home_automation import HomeAutomation
from mobile_server import run_mobile_server, set_handlers, set_home_automation


def load_config(config_path="config.json"):
    """Load configuration from file"""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Return default config
            return {
                "wake_phrases": ["hey jarvis", "jarvis"],
                "voice_settings": {"rate": 170, "volume": 1.0, "voice_index": 0},
                "ollama": {
                    "enabled": True,
                    "model": "llama2",
                    "api_url": "http://localhost:11434/api/generate"
                },
                "vision": {
                    "enabled": True,
                    "model": "moondream",
                    "camera_index": 0,
                    "frame_width": 640,
                    "frame_height": 480,
                    "timeout": 45,
                    "prompt": "Describe this scene in 2 short sentences. Focus on important objects and actions."
                }
            }
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║          ░░█ ▄▀█ █▀█ █░█ █ █▀   Mobile Server                ║
    ║          █▄█ █▀█ █▀▄ ▀▄▀ █ ▄█   Lightweight Edition          ║
    ║                                                              ║
    ║   Control Jarvis from your phone without the desktop UI      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("[*] Loading configuration...")
    config = load_config()
    
    print("[*] Initializing modules...")
    
    # Initialize voice engine (for TTS responses)
    voice_engine = VoiceEngine(config)
    print("    ✓ Voice engine ready")
    
    # Initialize app controller
    app_controller = ApplicationController(config)
    print("    ✓ App controller ready")
    
    # Initialize email manager
    email_manager = EmailManager(config)
    print("    ✓ Email manager ready")
    
    # Initialize AI assistant
    ai_assistant = AIAssistant(config)
    print("    ✓ AI assistant ready")
    
    # Initialize home automation for TV control
    try:
        home_automation = HomeAutomation()
        set_home_automation(home_automation)
        print("    ✓ Home automation ready")
    except Exception as e:
        logger.warning(f"Home automation not available: {e}")
        home_automation = None
    
    # Initialize command handler
    command_handler = CommandHandler(
        voice_engine=voice_engine,
        system_controller=None,
        app_controller=app_controller,
        ai_assistant=ai_assistant,
        email_manager=email_manager
    )
    print("    ✓ Command handler ready")
    
    # Set handlers for mobile server
    set_handlers(command_handler, voice_engine)
    
    print("\n[*] All modules initialized!")
    print("[*] Starting mobile server...")
    print("\n" + "="*60)
    print("  📱 Connect your Jarvis mobile app to this server")
    print("  📍 Make sure your phone is on the same WiFi network")
    print("="*60 + "\n")
    
    # Run the mobile server (blocking)
    run_mobile_server(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Shutting down Jarvis Mobile Server...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
