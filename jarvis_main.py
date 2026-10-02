"""
Jarvis - Comprehensive Voice-Controlled Automation System
Main application file with modular architecture
"""

import os
import logging
import time
import threading
from typing import Dict, Optional

# Import keyboard for ESC monitoring
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# Import custom modules
from modules.voice_engine import VoiceEngine
from modules.app_controller import ApplicationController
from modules.email_manager import EmailManager
from modules.ai_assistant import AIAssistant
from modules.utilities import Utilities
from modules.command_handler import CommandHandler
from modules.configuration import load_config


class Jarvis:
    """Main Jarvis application class"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize Jarvis with configuration
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.is_active = False
        self.running = True
        self.esc_pressed = False
        
        # Setup ESC key listener
        if KEYBOARD_AVAILABLE:
            keyboard.on_press_key('esc', self._on_esc_press)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize modules
        logger.info("Initializing Jarvis modules...")
        self.voice_engine = VoiceEngine(self.config)
        self.app_controller = ApplicationController(self.config)
        self.email_manager = EmailManager(self.config)
        self.ai_assistant = AIAssistant(self.config)
        self.utilities = Utilities()
        
        # Initialize command handler with all modules
        self.command_handler = CommandHandler(
            voice_engine=self.voice_engine,
            system_controller=None,  # Will be initialized inside CommandHandler
            app_controller=self.app_controller,
            ai_assistant=self.ai_assistant,
            email_manager=self.email_manager
        )
        
        # Start mobile server for app connectivity
        self._start_mobile_server()
        
        logger.info("Jarvis initialized successfully")
    
    def _start_mobile_server(self):
        """Start the mobile server for app connectivity"""
        try:
            from mobile_server import start_mobile_server_thread
            self.mobile_server_thread = start_mobile_server_thread(
                cmd_handler=self.command_handler,
                voice_eng=self.voice_engine,
                port=5000
            )
            logger.info("Mobile server started on port 5000")
        except Exception as e:
            logger.warning(f"Could not start mobile server: {e}")
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        return load_config(self.config_path)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        
        if log_config.get('enabled', True):
            log_file = log_config.get('log_file', 'jarvis.log')
            log_level = getattr(logging, log_config.get('log_level', 'INFO'))
            
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
        
        global logger
        logger = logging.getLogger(__name__)
    
    def greet_user(self):
        """Greet the user based on time of day"""
        greeting = self.utilities.get_greeting()
        self.voice_engine.speak(greeting)
        self.voice_engine.speak("I am Jarvis. How can I help you today?")
        logger.info("Greeted user")
    
    def check_wake_phrase(self, query: str) -> bool:
        """
        Check if query contains wake phrase
        
        Args:
            query: The voice query to check
            
        Returns:
            bool: True if wake phrase detected
        """
        if not query:
            return False
        
        wake_phrases = self.config.get('wake_phrases', ['hey jarvis', 'jarvis'])
        
        for phrase in wake_phrases:
            if phrase in query.lower():
                return True
        
        return False
    
    def _on_esc_press(self, event):
        """Handle ESC key press"""
        self.esc_pressed = True
        self.running = False
        print("\n[ESC pressed - Exiting...]")
        logger.info("ESC key pressed - shutting down")
    
    def check_sleep_command(self, query: str) -> bool:
        """
        Check if query contains sleep command
        
        Args:
            query: The voice query to check
            
        Returns:
            bool: True if sleep command detected
        """
        if not query:
            return False
        
        sleep_commands = self.config.get('sleep_commands', ['sleep', 'go to sleep'])
        
        for command in sleep_commands:
            if command in query.lower():
                return True
        
        return False
    
    def run(self):
        """Main Jarvis loop"""
        print("\n" + "="*60)
        print("JARVIS - Voice-Controlled Automation System")
        print("="*60)
        print("\nQuick Commands:")
        print("  - 'Hey Jarvis' to wake up")
        print("  - 'Stop' or 'Cancel' to deactivate")
        print("  - 'Exit' or 'Bye' to quit")
        print("  - Press ESC key anytime for instant exit")
        print("  - Press Ctrl+C for forced shutdown")
        print("\nNew Features:")
        print("  - 'Increase/Decrease brightness'")
        print("  - 'Set brightness to 50'")
        print("  - 'Control my brightness' (hand gesture control)")
        print("  - 'Control my volume' (hand gesture control)")
        print("  - 'Set focus timer for 25' (minutes)")
        print("  - 'Lock screen'")
        print("  - 'Display settings'")
        print("\nSay 'Hey Jarvis' to get started!")
        print("="*60 + "\n")
        
        # Test microphone
        print("Testing microphone...")
        try:
            import speech_recognition as sr
            test_rec = sr.Recognizer()
            with sr.Microphone() as source:
                print("[OK] Microphone detected\n")
        except OSError as e:
            print("[ERROR] Microphone not detected!")
            print("\nPlease ensure:")
            print("  1. A microphone is connected")
            print("  2. Microphone is set as default in Windows Settings")
            print("  3. Python has microphone permissions\n")
            logger.error(f"Microphone error: {e}")
            return
        except Exception as e:
            print(f"[ERROR] Error testing microphone: {e}\n")
            logger.error(f"Microphone test error: {e}")
        
        # Greet user
        self.greet_user()
        
        try:
            while self.running and not self.esc_pressed:
                # Check for ESC key
                if self.esc_pressed:
                    break
                
                # Listen for input
                query = self.voice_engine.listen()
                
                if not query:
                    continue
                
                # Check for PC shutdown/restart/sleep commands (work anytime, even when inactive)
                if any(phrase in query for phrase in ['shutdown my', 'turn off my', 'restart my', 'sleep my', 'shutdown pc', 'turn off pc', 'restart pc', 'sleep pc', 'shutdown computer', 'turn off computer', 'restart computer', 'sleep computer']):
                    result = self.command_handler.process_command(query)
                    if result == 'EXIT':
                        self.running = False
                        break
                    continue
                
                # Quick exit commands for Jarvis (work anytime)
                if any(phrase in query for phrase in ['exit jarvis', 'quit jarvis', 'shutdown jarvis', 'close jarvis', 'goodbye jarvis', 'bye jarvis']):
                    self.voice_engine.speak("Goodbye!")
                    logger.info("Jarvis shutting down")
                    self.running = False
                    break
                
                # Check for wake phrase
                if not self.is_active:
                    if self.check_wake_phrase(query):
                        self.is_active = True
                        self.voice_engine.speak("Yes?")
                        logger.info("Jarvis activated")
                    continue
                
                # If active, process commands
                if self.is_active:
                    # Check for sleep/stop commands
                    if self.check_sleep_command(query) or 'stop' in query or 'cancel' in query or 'never mind' in query:
                        self.voice_engine.speak("Okay.")
                        self.is_active = False
                        logger.info("Jarvis deactivated")
                        continue
                    
                    # Process command
                    result = self.command_handler.process_command(query)
                    
                    # Check for exit command
                    if result == 'EXIT':
                        self.running = False
                        break
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            logger.info("Jarvis interrupted by user")
        
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            print(f"\nError: {e}")
        
        finally:
            logger.info("Jarvis terminated")
            print("\nJarvis shut down.\n")


def main():
    """Main entry point"""
    # Check if setup is needed
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        from setup_wizard import run_wizard
        run_wizard()
        return
    
    # Run Jarvis
    jarvis = Jarvis()
    jarvis.run()


if __name__ == "__main__":
    main()
