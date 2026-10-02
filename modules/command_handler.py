"""
Command Handler Module
Processes and routes voice commands to appropriate modules
"""
import logging
from typing import Dict, Optional
import re
from modules.spotify_controller import SpotifyController

logger = logging.getLogger(__name__)


class CommandHandler:
    """Handles user commands and dispatches them to appropriate modules."""
    
    def __init__(self, voice_engine, system_controller, app_controller, ai_assistant, email_manager):
        self.voice_engine = voice_engine
        self.system_controller = system_controller
        self.app_controller = app_controller
        self.ai_assistant = ai_assistant
        self.email_manager = email_manager
        self.spotify_controller = SpotifyController()
        self.last_generated_code: Optional[str] = None
        
        # Import system controller
        try:
            from modules.system_controller import SystemController
            self.system_controller = SystemController()
        except Exception as e:
            logger.warning(f"System controller not available: {e}")
            self.system_controller = None
        
        # Import utilities
        try:
            from modules.utilities import Utilities
            self.utilities = Utilities()
        except Exception as e:
            logger.warning(f"Utilities not available: {e}")
            self.utilities = None
        
        # Import VS Code controller
        try:
            from modules.vscode_controller import VSCodeController
            self.vscode_controller = VSCodeController()
        except Exception as e:
            logger.warning(f"VS Code controller not available: {e}")
            self.vscode_controller = None
        
        # Import app actions if available
        try:
            from modules.app_actions import AppActions
            self.app_actions = AppActions()
        except:
            self.app_actions = None

        # Import vision assistant if available
        try:
            from modules.vision_assistant import VisionAssistant
            self.vision_assistant = VisionAssistant(getattr(self.ai_assistant, 'config', {}) or {})
        except Exception as e:
            logger.warning(f"Vision assistant not available: {e}")
            self.vision_assistant = None
        
        # Command patterns
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> Dict:
        """Build regex patterns for command matching"""
        return {
            'open_app': re.compile(r'open\s+(.+)'),
            'close_app': re.compile(r'close\s+(.+)'),
            'open_file': re.compile(r'open file\s+(.+)'),
            'arduino_new_sketch': re.compile(r'(?:(?:open|create|make|start)\s+(?:a\s+)?(?:new\s+)?(?:sketch|project)|(?:new\s+)?(?:sketch|project))\s+(?:in|on|with|inside)\s+(?:arduino(?:\s+ide)?)'),
            'notepad_new_text_file': re.compile(r'(?:(?:open|create|make|start)\s+(?:a\s+)?(?:new\s+)?(?:text\s+file|file)|(?:new\s+)?(?:text\s+file|file))\s+(?:in|on|with|inside)\s+notepad'),
            'vscode_new_file': re.compile(r'(?:(?:open|create|make|start)\s+(?:a\s+)?(?:new\s+)?(?:file|text\s+file)|(?:new\s+)?(?:file|text\s+file))\s+(?:in|on|with|inside)\s+(?:vs\s*code|vscode|visual\s+studio\s+code)'),
            'search_web': re.compile(r'search\s+(?:for\s+)?(.+)'),
            'google': re.compile(r'google\s+(.+)'),
            'youtube': re.compile(r'youtube\s+(.+)'),
            'wikipedia': re.compile(r'wikipedia\s+(.+)'),
            'time': re.compile(r'(?:what\s+)?(?:is\s+)?(?:the\s+)?time'),
            'date': re.compile(r'(?:what\s+)?(?:is\s+)?(?:the\s+)?date'),
            'email': re.compile(r'(?:send\s+)?(?:an\s+)?email|gmail'),
            'change_voice': re.compile(r'change voice\s+(?:to\s+)?(.+)'),
            'set_voice_speed': re.compile(r'(?:set\s+)?voice speed\s+(?:to\s+)?(\d+)'),
            'calculate': re.compile(r'(?:calculate|what is|what\'s|compute|solve)\s+(.+)'),
            'brightness': re.compile(r'(?:set\s+)?brightness\s+(?:to\s+)?(\d+)'),
            'focus_timer': re.compile(r'(?:set\s+)?focus timer\s+(?:for\s+)?(\d+)'),
            'shutdown_jarvis': re.compile(r'(?:shutdown|exit|quit|close)\s+jarvis|jarvis\s+(?:shutdown|exit|quit)'),
            'shutdown_pc': re.compile(r'(?:shutdown|turn off)\s+(?:my\s+)?(?:pc|computer|system)'),
            'restart_pc': re.compile(r'restart\s+(?:my\s+)?(?:pc|computer|system)'),
            'sleep_pc': re.compile(r'(?:sleep|hibernate)\s+(?:my\s+)?(?:pc|computer|system)'),
        }
    
    def handle_play_command(self, command: str):
        """Handles 'play' commands for Spotify."""
        song_name = command.replace("play", "").strip()
        if not song_name or song_name == "spotify":
            self.voice_engine.speak("What song or artist would you like me to play on Spotify?")
            return
        
        response = self.spotify_controller.play_song(song_name)
        self.voice_engine.speak(response)
    
    def handle_spotify_control(self, command: str):
        """Handle Spotify playback controls (pause, resume, next, previous)."""
        command = command.lower()
        
        if any(word in command for word in ['pause', 'stop music', 'stop spotify']):
            response = self.spotify_controller.pause()
            self.voice_engine.speak(response)
            return True
        
        if any(word in command for word in ['resume', 'continue', 'unpause']):
            response = self.spotify_controller.resume()
            self.voice_engine.speak(response)
            return True
        
        if any(word in command for word in ['next', 'skip', 'next song', 'next track']):
            response = self.spotify_controller.next_track()
            self.voice_engine.speak(response)
            return True
        
        if any(word in command for word in ['previous', 'back', 'previous song', 'last song']):
            response = self.spotify_controller.previous_track()
            self.voice_engine.speak(response)
            return True
        
        return False
    
    def process_command(self, command: str) -> bool:
        """
        Process a voice command and execute appropriate action
        
        Args:
            command: The voice command string
            
        Returns:
            bool: True if command was handled, False otherwise
        """
        try:
            command = command.lower().strip()
            logger.info(f"Processing command: {command}")
            
            # Check for CV control stop commands FIRST (priority when CV control is active)
            if self.system_controller:
                stop_phrases = [
                    'ok jarvis', 'okay jarvis', 'fine jarvis', 'stop jarvis',
                    'ok', 'okay', 'fine', 'stop', 'that\'s enough', 'enough',
                    'thank you', 'thanks', 'good', 'done'
                ]
                
                # Check if command matches a stop phrase
                if any(phrase in command for phrase in stop_phrases):
                    # Stop brightness control if active
                    if self.system_controller.is_cv_brightness_active():
                        self.system_controller.stop_cv_brightness_control()
                        self.voice_engine.speak("Brightness control stopped")
                        return True
                    
                    # Stop volume control if active
                    if self.system_controller.is_cv_volume_active():
                        self.system_controller.stop_cv_volume_control()
                        self.voice_engine.speak("Volume control stopped")
                        return True
            
            # Spotify controls (pause, next, previous, resume)
            if any(word in command for word in ['pause spotify', 'pause music', 'stop music', 
                                                  'next song', 'next track', 'skip song', 'skip track',
                                                  'previous song', 'previous track', 'last song',
                                                  'resume spotify', 'resume music', 'continue music']):
                return self.handle_spotify_control(command)
            
            # Play command (Spotify)
            if command.startswith('play'):
                return self.handle_play_command(command)

            # Web services (check BEFORE generic 'open' to prevent conflicts)
            elif 'youtube' in command:
                match = self.patterns['youtube'].search(command)
                if match:
                    return self._handle_youtube_search(match.group(1))
            
            elif 'wikipedia' in command:
                match = self.patterns['wikipedia'].search(command)
                if match:
                    return self._handle_wikipedia(match.group(1))
            
            elif 'google' in command and 'search' not in command:
                match = self.patterns['google'].search(command)
                if match:
                    return self._handle_web_search(match.group(1))
            
            # Web searches
            elif 'search' in command:
                match = self.patterns['search_web'].search(command)
                if match:
                    return self._handle_web_search(match.group(1))
            
            # Check for file opening
            elif 'open file' in command:
                match = self.patterns['open_file'].search(command)
                if match:
                    return self._handle_open_file(match.group(1))

            # Arduino IDE new sketch commands
            elif any(phrase in command for phrase in [
                'new sketch in arduino', 'new sketch in arduino ide',
                'open new sketch in arduino', 'open new sketch in arduino ide',
                'create new sketch in arduino', 'create new sketch in arduino ide',
                'make new sketch in arduino', 'start new sketch in arduino',
                'arduino new sketch', 'arduino ide new sketch'
            ]) or self.patterns['arduino_new_sketch'].search(command):
                return self._handle_new_arduino_sketch()

            # Notepad new text file commands
            elif any(phrase in command for phrase in [
                'new text file in notepad', 'open new text file in notepad',
                'create new text file in notepad', 'make new text file in notepad',
                'start new text file in notepad', 'new file in notepad',
                'open new file in notepad', 'create new file in notepad',
                'notepad new text file', 'notepad new file'
            ]) or self.patterns['notepad_new_text_file'].search(command):
                return self._handle_new_notepad_text_file()

            # VS Code new file commands
            elif any(phrase in command for phrase in [
                'new file in vscode', 'new file in vs code', 'new file in visual studio code',
                'open new file in vscode', 'open new file in vs code',
                'create new file in vscode', 'create new file in vs code',
                'new text file in vscode', 'new text file in vs code',
                'open new text file in vscode', 'open new text file in vs code',
                'vscode new file', 'vs code new file'
            ]) or self.patterns['vscode_new_file'].search(command):
                return self._handle_new_vscode_file()
            
            # Generic open command (last resort for apps)
            elif 'open ' in command or command.startswith('open'):
                match = self.patterns['open_app'].search(command)
                if match:
                    return self._handle_open_app(match.group(1))
            
            # Email
            elif self.patterns['email'].search(command):
                return self._handle_email()
            
            # System controls (CHECK TIMER BEFORE TIME!)
            elif 'focus timer' in command or 'timer' in command:
                return self._handle_focus_timer(command)
            
            # CV Control Commands (check BEFORE regular brightness/volume)
            elif any(phrase in command for phrase in ['control brightness', 'control my brightness', 'control screen brightness', 'control my screen brightness']):
                return self._handle_cv_brightness_control(command)
            
            elif any(phrase in command for phrase in ['control volume', 'control my volume', 'control sound']):
                return self._handle_cv_volume_control(command)
            
            elif 'brightness' in command:
                return self._handle_brightness(command)
            
            # Time and date (AFTER timer check)
            elif self.patterns['time'].search(command):
                return self._handle_time()
            
            elif self.patterns['date'].search(command):
                return self._handle_date()
            
            elif any(phrase in command for phrase in ['lock screen', 'lock my screen', 'lock computer', 'lock my computer', 'lock pc']):
                if self.system_controller and self.system_controller.lock_screen():
                    # Don't speak as screen will be locked
                    return True
                return False
            
            elif 'display settings' in command:
                if self.system_controller and self.system_controller.open_display_settings():
                    self.voice_engine.speak("Opening display settings")
                    return True
                return False

            # Vision commands
            elif any(phrase in command for phrase in [
                'describe scene', 'describe the scene', 'describe my scene',
                'what do you see', 'what can you see', 'look around',
                'analyze scene', 'scan scene', 'describe camera view'
            ]):
                return self._handle_describe_scene(command)
            
            # VS Code commands - check for code execution patterns
            elif ('run' in command or 'execute' in command) and ('.py' in command or 'dot py' in command or 'python' in command or 'code' in command):
                return self._handle_run_code(command)
            
            elif 'stop code' in command or 'stop execution' in command or 'terminate' in command:
                return self._handle_stop_code()
            
            elif 'generate code' in command or 'create code' in command or 'write code' in command:
                return self._handle_generate_code(command)

            elif any(phrase in command for phrase in [
                'paste script', 'paste the script', 'paste generated script',
                'paste code', 'paste generated code'
            ]):
                return self._handle_paste_generated_script(command)
            
            # VS Code open commands - catch all variations
            elif any(phrase in command for phrase in ['open vscode', 'open vs code', 'open visual studio code', 'open in vscode', 'open in vs code', 'launch vscode', 'launch vs code', 'start vscode', 'start vs code']):
                return self._handle_open_vscode(command)
            
            # Voice customization
            elif 'change voice' in command:
                match = self.patterns['change_voice'].search(command)
                if match:
                    return self._handle_voice_change(match.group(1))
            
            elif 'voice speed' in command:
                match = self.patterns['set_voice_speed'].search(command)
                if match:
                    return self._handle_voice_speed(int(match.group(1)))
            
            elif 'list voices' in command:
                return self._handle_list_voices()
            
            # Help and capabilities
            elif any(phrase in command for phrase in [
                'what can you do', 'what are your capabilities', 'what are the tasks',
                'help me', 'show help', 'list commands', 'what commands',
                'your abilities', 'what do you do', 'how can you help',
                'what are you capable', 'show me what you can do', 'your features'
            ]):
                return self._handle_help()
            
            # Shutdown and power commands
            elif self.patterns['shutdown_jarvis'].search(command):
                return self._handle_shutdown_jarvis()
            
            elif self.patterns['shutdown_pc'].search(command):
                return self._handle_shutdown_pc()
            
            elif self.patterns['restart_pc'].search(command):
                return self._handle_restart_pc()
            
            elif self.patterns['sleep_pc'].search(command):
                return self._handle_sleep_pc()
            
            elif 'cancel shutdown' in command or 'abort shutdown' in command:
                return self._handle_cancel_shutdown()
            
            # Calculation commands (before AI fallback)
            elif any(word in command for word in ['calculate', 'what is', "what's", 'compute', 'solve']):
                # Make sure it's actually a math question
                match = self.patterns['calculate'].search(command)
                if match:
                    expr = match.group(1).strip()
                    # Check if it contains numbers or math operators
                    if any(char.isdigit() or char in '+-*/()' for char in expr):
                        return self._handle_calculation(expr)

            # Plain math expressions like "1+1" or "(12/3) + 5"
            elif re.fullmatch(r'[\d\s\+\-\*\/\(\)\.xX%]+', command) and any(ch.isdigit() for ch in command):
                return self._handle_calculation(command.replace('x', '*').replace('X', '*').replace('%', '/100'))

            # Voice-style math expressions like "1 plus 1" without "calculate"
            elif any(word in command for word in ['plus', 'minus', 'times', 'multiplied by', 'divided', 'over', 'squared', 'cubed']) and any(ch.isdigit() for ch in command):
                return self._handle_calculation(command)
            
            # AI conversation (fallback for everything else)
            else:
                return self._handle_ai_conversation(command)
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.voice_engine.speak("I encountered an error processing that command.")
            return False
    
    def _handle_open_app(self, app_name: str) -> bool:
        """Handle application opening"""
        # Check if app is installed
        if not self.app_controller.check_app_installed(app_name):
            self.voice_engine.speak(f"I couldn't find {app_name} installed on this computer.")
            return False
        
        self.voice_engine.speak(f"Opening {app_name}")
        success = self.app_controller.open_application(app_name)
        
        if not success:
            self.voice_engine.speak(f"I had trouble opening {app_name}")
        
        return success
    
    def _handle_open_file(self, filename: str) -> bool:
        """Handle file opening"""
        self.voice_engine.speak(f"Looking for {filename}")
        success = self.app_controller.open_file(filename)
        
        if success:
            self.voice_engine.speak(f"Opening {filename}")
        else:
            self.voice_engine.speak(f"I couldn't find a file named {filename}")
        
        return success

    def _handle_new_arduino_sketch(self) -> bool:
        """Open Arduino IDE and create a new sketch."""
        arduino_aliases = ['arduino ide', 'arduino', 'arduino ide.exe']
        launched = False

        for app_name in arduino_aliases:
            if self.app_controller.check_app_installed(app_name):
                launched = self.app_controller.open_application(app_name)
                if launched:
                    break

        if not launched:
            self.voice_engine.speak("I couldn't find Arduino IDE installed on this computer.")
            return False

        try:
            import time
            import pyautogui

            # Off Grid requests can arrive while another app has focus.
            # Try a few focus+shortcut cycles to improve reliability.
            for attempt in range(3):
                time.sleep(1.2 if attempt == 0 else 0.5)
                try:
                    pyautogui.hotkey('alt', 'tab')
                    time.sleep(0.9)
                except Exception:
                    pass
                pyautogui.hotkey('ctrl', 'n')

            self.voice_engine.speak("Opening a new sketch in Arduino IDE with Control plus N")
            return True
        except Exception as e:
            logger.warning(f"Could not send new sketch shortcut to Arduino IDE: {e}")
            self.voice_engine.speak("Arduino IDE is open. Please use Control plus N to create a new sketch.")
            return True

    def _handle_new_notepad_text_file(self) -> bool:
        """Open Notepad with a new blank text file."""
        if not self.app_controller.check_app_installed('notepad'):
            self.voice_engine.speak("I couldn't find Notepad installed on this computer.")
            return False

        success = self.app_controller.open_application('notepad')
        if success:
            self.voice_engine.speak("Opening a new text file in Notepad")
            return True

        self.voice_engine.speak("I had trouble opening Notepad")
        return False

    def _handle_new_vscode_file(self) -> bool:
        """Open VS Code and create a new file using Ctrl+N after a delay."""
        launched = False

        # Prefer app controller aliases first.
        for app_name in ['vscode', 'vs code', 'visual studio code', 'code']:
            if self.app_controller.check_app_installed(app_name):
                launched = self.app_controller.open_application(app_name)
                if launched:
                    break

        # Fall back to VS Code controller if direct app open did not work.
        if not launched and self.vscode_controller:
            try:
                self.vscode_controller.open_folder('.')
                launched = True
            except Exception as e:
                logger.warning(f"VS Code controller fallback open failed: {e}")

        if not launched:
            self.voice_engine.speak("I couldn't open VS Code on this computer.")
            return False

        try:
            import time
            import pyautogui

            # Match Arduino behavior: wait for IDE to fully load first.
            for attempt in range(3):
                time.sleep(5.0 if attempt == 0 else 0.5)
                try:
                    pyautogui.hotkey('alt', 'tab')
                    time.sleep(0.2)
                except Exception:
                    pass
                pyautogui.hotkey('ctrl', 'n')

            self.voice_engine.speak("Opening a new file in VS Code with Control plus N")
            return True
        except Exception as e:
            logger.warning(f"Could not send new file shortcut to VS Code: {e}")
            self.voice_engine.speak("VS Code is open. Please use Control plus N to create a new file.")
            return True
    
    def _handle_whatsapp_web(self) -> bool:
        """Handle WhatsApp Web opening with internet check"""
        self.voice_engine.speak("Checking internet connection...")
        success, message = self.utilities.open_website_with_check(
            'https://web.whatsapp.com',
            'WhatsApp Web'
        )
        self.voice_engine.speak(message)
        return success
    
    def _handle_web_search(self, query: str) -> bool:
        """Handle web search"""
        if not self.utilities.check_internet():
            self.voice_engine.speak("I cannot connect to the internet.")
            return False
        
        self.voice_engine.speak(f"Searching for {query}")
        return self.utilities.search_web(query)
    
    def _handle_youtube_search(self, query: str) -> bool:
        """Handle YouTube search"""
        if not self.utilities.check_internet():
            self.voice_engine.speak("I cannot connect to the internet.")
            return False
        
        self.voice_engine.speak(f"Searching YouTube for {query}")
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        return self.utilities.open_website(url)
    
    def _handle_wikipedia(self, query: str) -> bool:
        """Handle Wikipedia search"""
        try:
            import wikipedia
            
            if not self.utilities.check_internet():
                self.voice_engine.speak("I cannot connect to the internet.")
                return False
            
            self.voice_engine.speak("Searching Wikipedia...")
            results = wikipedia.summary(query, sentences=2)
            self.voice_engine.speak("According to Wikipedia")
            self.voice_engine.speak(results)
            return True
            
        except wikipedia.exceptions.DisambiguationError as e:
            self.voice_engine.speak(f"There are multiple results for {query}. Please be more specific.")
            return False
        except wikipedia.exceptions.PageError:
            self.voice_engine.speak(f"I couldn't find any Wikipedia article about {query}")
            return False
        except Exception as e:
            logger.error(f"Wikipedia error: {e}")
            self.voice_engine.speak("I had trouble searching Wikipedia.")
            return False
    
    def _handle_email(self) -> bool:
        """Handle email composition and sending"""
        if not self.email_manager.validate_credentials():
            self.voice_engine.speak("Email credentials are not configured. Please update the config file.")
            return False
        
        email_details = self.email_manager.compose_email_interactive(self.voice_engine)
        
        if email_details:
            success = self.email_manager.send_email(
                email_details['to'],
                email_details['subject'],
                email_details['content']
            )
            
            if success:
                self.voice_engine.speak("Email sent successfully!")
            else:
                self.voice_engine.speak("Failed to send email. Please check your configuration.")
            
            return success
        
        return False
    
    def _handle_time(self) -> bool:
        """Handle time query"""
        current_time = self.utilities.get_current_time()
        self.voice_engine.speak(f"The current time is {current_time}")
        return True
    
    def _handle_date(self) -> bool:
        """Handle date query"""
        current_date = self.utilities.get_current_date()
        self.voice_engine.speak(f"Today is {current_date}")
        return True
    
    def _handle_voice_change(self, profile_name: str) -> bool:
        """Handle voice profile change"""
        self.voice_engine.apply_voice_profile(profile_name)
        self.voice_engine.speak(f"Voice changed to {profile_name} profile")
        return True
    
    def _handle_voice_speed(self, speed: int) -> bool:
        """Handle voice speed change"""
        self.voice_engine.set_voice_parameters(rate=speed)
        self.voice_engine.speak(f"Voice speed set to {speed}")
        return True
    
    def _handle_help(self) -> bool:
        """List all capabilities and commands"""
        self.voice_engine.speak("Here are the things I can do for you, sir.")
        
        capabilities = [
            "Open applications. Just say 'open' followed by the app name, like 'open Chrome' or 'open VS Code'.",
            "Search the web. Say 'search for' followed by your query, or 'Google' or 'YouTube' something.",
            "Control your music. Say 'play' followed by a song name to play on Spotify.",
            "Send emails. Say 'send an email' and I'll guide you through it.",
            "Tell you the time and date. Ask 'what time is it' or 'what's the date'.",
            "Do calculations. Say 'calculate' or 'what is' followed by a math expression.",
            "Control screen brightness. Say 'set brightness to 50' or 'increase brightness'.",
            "Control volume with hand gestures. Say 'control my volume' or 'control my brightness'.",
            "Describe what the camera sees. Say 'describe scene' or 'what do you see'.",
            "Set focus timers. Say 'set focus timer for 25 minutes'.",
            "Lock your screen. Say 'lock screen' or 'lock my computer'.",
            "Run Python code. Say 'run' followed by the filename.",
            "Generate code. Say 'generate code' and describe what you need.",
            "Control your PC. Say 'shutdown PC', 'restart PC', or 'sleep PC'.",
            "Search Wikipedia. Say 'Wikipedia' followed by a topic.",
            "Change my voice. Say 'change voice' or 'list voices'.",
            "And have conversations using AI. Just ask me anything!",
        ]
        
        # Speak a summary, not all items (too long)
        self.voice_engine.speak("I can open apps, search the web, play music, send emails, "
                               "tell time, do math, control brightness and volume, "
                               "describe camera scenes, "
                               "set timers, lock your screen, run code, control your PC, "
                               "search Wikipedia, and have AI conversations.")
        
        self.voice_engine.speak("Just say 'Hey Jarvis' followed by your command. "
                               "For example, 'Hey Jarvis, open Chrome' or 'Hey Jarvis, what's the weather'.")
        
        return True
    
    def _handle_list_voices(self) -> bool:
        """List available voices"""
        voices = self.voice_engine.list_available_voices()
        self.voice_engine.speak(f"I have {len(voices)} voices available")
        
        for voice in voices[:3]:  # Limit to first 3
            self.voice_engine.speak(f"Voice {voice['index']}: {voice['name']}")
        
        return True
    
    def _handle_calculation(self, expression: str) -> bool:
        """Handle mathematical calculations"""
        try:
            # Clean up the expression
            expression = expression.strip()
            original_expression = expression
            
            # Replace words with operators
            replacements = {
                'plus': '+',
                'minus': '-',
                'times': '*',
                'multiplied by': '*',
                'divided by': '/',
                'divided': '/',
                'over': '/',
                'to the power of': '**',
                'squared': '**2',
                'cubed': '**3',
            }
            
            for word, symbol in replacements.items():
                expression = expression.replace(word, symbol)
            
            # Remove common filler words
            expression = expression.replace('by', '').replace('the', '').strip()
            
            # Sanitize expression (only allow numbers, operators, spaces, parentheses)
            import re
            if not re.match(r'^[\d\s\+\-\*\/\(\)\.\*\*]+$', expression):
                self.voice_engine.speak("I can only calculate mathematical expressions with numbers and basic operators.")
                return False
            
            # Evaluate the expression safely
            result = eval(expression, {"__builtins__": {}}, {})
            
            # Format result
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 4)
            
            logger.info(f"Calculation: {expression} = {result}")
            self.voice_engine.speak(f"The answer is {result}")
            
            # Optional: Open calculator app and perform the calculation (disabled by default)
            # Uncomment below to enable calculator app integration
            """
            if self.app_actions and self.app_controller.check_app_installed('calculator'):
                try:
                    # Open calculator
                    self.app_controller.open_application('calculator')
                    
                    # Send calculation to calculator
                    import time
                    time.sleep(0.8)  # Wait for calculator to open
                    
                    # Use app_actions to type in calculator
                    self.app_actions.execute_app_action('calculator', 'calculate', {'expression': expression})
                    
                    logger.info("Also displayed result in Calculator app")
                except Exception as e:
                    logger.debug(f"Could not use calculator app: {e}")
            """
            
            return True
            
        except ZeroDivisionError:
            self.voice_engine.speak("Cannot divide by zero")
            return False
        except SyntaxError:
            self.voice_engine.speak("I couldn't understand that mathematical expression")
            return False
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            self.voice_engine.speak("I had trouble calculating that")
            return False
    
    def _handle_ai_conversation(self, query: str) -> bool:
        """Handle general conversation with AI - always attempts to provide a helpful response"""
        response = self.ai_assistant.query(query)
        
        if response:
            self.voice_engine.speak(response)
            return True

        # Keep the conversation moving even if AI returns nothing.
        if query.strip():
            self.voice_engine.speak(f"I heard you say {query}. I'm still trying to reach the AI model.")
        else:
            self.voice_engine.speak("I didn't catch that. Please try again.")
        return True
    
    def _handle_brightness(self, command: str) -> bool:
        """Handle brightness control commands"""
        if not self.system_controller:
            self.voice_engine.speak("System control is not available.")
            return False
        
        try:
            # Check for specific brightness level
            match = self.patterns['brightness'].search(command)
            if match:
                level = int(match.group(1))
                if self.system_controller.set_brightness(level):
                    self.voice_engine.speak(f"Brightness set to {level} percent")
                    return True
                else:
                    self.voice_engine.speak("Could not change brightness")
                    return False
            
            # Check for increase/decrease
            if 'increase' in command or 'raise' in command or 'brighter' in command or 'up' in command:
                if self.system_controller.increase_brightness(10):
                    new_level = self.system_controller.get_brightness()
                    self.voice_engine.speak(f"Brightness increased to {new_level} percent")
                    return True
            elif 'decrease' in command or 'lower' in command or 'dimmer' in command or 'down' in command or 'reduce' in command:
                if self.system_controller.decrease_brightness(10):
                    new_level = self.system_controller.get_brightness()
                    self.voice_engine.speak(f"Brightness decreased to {new_level} percent")
                    return True
            else:
                # Get current brightness
                current = self.system_controller.get_brightness()
                if current is not None:
                    self.voice_engine.speak(f"Current brightness is {current} percent")
                    return True
            
            self.voice_engine.speak("Could not adjust brightness")
            return False
            
        except Exception as e:
            logger.error(f"Brightness control error: {e}")
            self.voice_engine.speak("Error controlling brightness")
            return False
    
    def _handle_focus_timer(self, command: str) -> bool:
        """Handle focus timer commands"""
        if not self.system_controller:
            self.voice_engine.speak("System control is not available.")
            return False
    
    def _handle_cv_brightness_control(self, command: str) -> bool:
        """Handle CV-based brightness control commands"""
        if not self.system_controller:
            self.voice_engine.speak("System control is not available.")
            return False
        
        try:
            # Check if already running
            if self.system_controller.is_cv_brightness_active():
                self.voice_engine.speak("Brightness control is already active. Say 'ok jarvis', 'fine jarvis', or press ESC to stop it.")
                return True
            
            # Start CV brightness control
            self.voice_engine.speak("Starting brightness control. Move your hand left and right to adjust brightness. Say 'ok jarvis' or 'fine jarvis' to stop.")
            
            if self.system_controller.start_cv_brightness_control():
                # Start monitoring for stop commands
                self._monitor_cv_stop_commands('brightness')
                return True
            else:
                self.voice_engine.speak("Could not start brightness control")
                return False
                
        except Exception as e:
            logger.error(f"CV brightness control error: {e}")
            self.voice_engine.speak("Error starting brightness control")
            return False
    
    def _handle_cv_volume_control(self, command: str) -> bool:
        """Handle CV-based volume control commands"""
        if not self.system_controller:
            self.voice_engine.speak("System control is not available.")
            return False
        
        try:
            # Check if already running
            if self.system_controller.is_cv_volume_active():
                self.voice_engine.speak("Volume control is already active. Say 'ok jarvis', 'fine jarvis', or press ESC to stop it.")
                return True
            
            # Start CV volume control
            self.voice_engine.speak("Starting volume control. Move your hand up and down to adjust volume. Say 'ok jarvis' or 'fine jarvis' to stop.")
            
            if self.system_controller.start_cv_volume_control():
                # Start monitoring for stop commands
                self._monitor_cv_stop_commands('volume')
                return True
            else:
                self.voice_engine.speak("Could not start volume control")
                return False
                
        except Exception as e:
            logger.error(f"CV volume control error: {e}")
            self.voice_engine.speak("Error starting volume control")
            return False
    
    def _monitor_cv_stop_commands(self, control_type: str):
        """Monitor for stop commands while CV control is active"""
        import threading
        
        def monitor():
            while True:
                # Check if process is still running
                if control_type == 'brightness' and not self.system_controller.is_cv_brightness_active():
                    break
                elif control_type == 'volume' and not self.system_controller.is_cv_volume_active():
                    break
                
                # Listen for stop commands
                query = self.voice_engine.listen()
                if query:
                    query = query.lower().strip()
                    
                    # Check for stop phrases
                    stop_phrases = [
                        'ok jarvis', 'okay jarvis', 'fine jarvis', 'stop jarvis',
                        'ok', 'okay', 'fine', 'stop', 'that\'s enough', 'enough',
                        'thank you', 'thanks', 'good', 'done'
                    ]
                    
                    if any(phrase in query for phrase in stop_phrases):
                        # Stop the appropriate control
                        if control_type == 'brightness':
                            self.system_controller.stop_cv_brightness_control()
                            self.voice_engine.speak("Brightness control stopped")
                        elif control_type == 'volume':
                            self.system_controller.stop_cv_volume_control()
                            self.voice_engine.speak("Volume control stopped")
                        break
                
                import time
                time.sleep(0.5)  # Small delay to prevent excessive CPU usage
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def _handle_focus_timer_original(self, command: str) -> bool:
        """Handle focus timer commands"""
        if not self.system_controller:
            self.voice_engine.speak("System control is not available.")
            return False
        
        try:
            # Check for stop/cancel
            if 'stop' in command or 'cancel' in command:
                if self.system_controller.stop_focus_timer():
                    self.voice_engine.speak("Focus timer stopped")
                    return True
            
            # Check for status
            if 'status' in command or 'how long' in command or 'remaining' in command:
                remaining = self.system_controller.get_focus_timer_status()
                if remaining is not None and remaining > 0:
                    minutes = remaining // 60
                    seconds = remaining % 60
                    if minutes > 0:
                        self.voice_engine.speak(f"{minutes} minutes and {seconds} seconds remaining")
                    else:
                        self.voice_engine.speak(f"{seconds} seconds remaining")
                    return True
                else:
                    self.voice_engine.speak("No active focus timer")
                    return True
            
            # Set timer
            match = self.patterns['focus_timer'].search(command)
            if match:
                minutes = int(match.group(1))
                if self.system_controller.start_focus_timer(minutes):
                    self.voice_engine.speak(f"Focus timer set for {minutes} minutes")
                    return True
            
            self.voice_engine.speak("Please specify timer duration in minutes")
            return False
            
        except Exception as e:
            logger.error(f"Focus timer error: {e}")
            self.voice_engine.speak("Error with focus timer")
            return False

    def _handle_describe_scene(self, command: str) -> bool:
        """Capture one webcam frame and describe the scene quickly."""
        if not self.vision_assistant:
            self.voice_engine.speak("Vision assistant is not available.")
            return False

        try:
            prompt = command
            for phrase in [
                'describe the scene', 'describe my scene', 'describe scene',
                'what do you see', 'what can you see', 'look around',
                'analyze scene', 'scan scene', 'describe camera view'
            ]:
                prompt = prompt.replace(phrase, '')

            prompt = prompt.strip(' ,.')

            self.voice_engine.speak("Checking camera and describing the scene.")
            description = self.vision_assistant.describe_scene(prompt=prompt)
            self.voice_engine.speak(description)
            return True
        except Exception as e:
            logger.error(f"Describe scene error: {e}")
            self.voice_engine.speak("I had trouble describing the camera scene.")
            return False
    
    def _handle_run_code(self, command: str) -> bool:
        """Handle code execution"""
        if not self.vscode_controller:
            self.voice_engine.speak("VS Code controller not available")
            return False
        
        try:
            # Extract filename if mentioned
            # Handle patterns: "run code hand.py", "run hand.py", "execute hand dot py"
            import re
            
            # Replace voice-to-text patterns
            command = command.replace(' dot ', '.')
            command = command.replace(' underscore ', '_')
            command = command.replace('underscore', '_')
            # Handle common voice recognition mistakes
            command = command.replace('.com', '.py')  # "dot com" → ".py"
            command = command.replace(' com ', '.py ')  # "com" → ".py"
            if command.endswith(' com'):
                command = command[:-4] + '.py'
            
            words = command.split()
            python_file = None
            
            # Look for .py extension or construct filename
            for i, word in enumerate(words):
                if '.py' in word:
                    python_file = word
                    break
                # Skip common words
                elif word not in ['run', 'execute', 'code', 'file', 'python', 'script', 'the']:
                    # Check if next word might be "py" or "dot py"
                    if i + 1 < len(words) and words[i + 1] in ['py', 'python']:
                        python_file = f"{word}.py"
                        break
                    # If it looks like a filename (after run/execute keywords)
                    elif i > 0 and words[i-1] in ['run', 'execute', 'code']:
                        if not word.endswith('.py'):
                            python_file = f"{word}.py"
                        else:
                            python_file = word
                        break
            
            if python_file:
                # Search for file in multiple locations
                import os
                import glob
                
                search_paths = [
                    python_file,  # Current directory
                    os.path.join('..', python_file),  # Parent directory (HOME_AUTOMATION)
                    os.path.join('..', '..', python_file),  # Grandparent
                    os.path.join(os.path.expanduser('~'), 'Desktop', 'HOME_AUTOMATION', python_file),  # Absolute path
                ]
                
                found_path = None
                for path in search_paths:
                    if os.path.exists(path):
                        found_path = os.path.abspath(path)
                        break
                
                # If not found in specific paths, search recursively
                if not found_path:
                    # Search in parent directory and subdirectories
                    parent_dir = os.path.abspath('..')
                    matches = glob.glob(os.path.join(parent_dir, '**', python_file), recursive=True)
                    if matches:
                        found_path = matches[0]  # Take first match
                
                if found_path:
                    self.voice_engine.speak(f"Executing {os.path.basename(python_file)}")
                    self.vscode_controller.run_python_file(found_path)
                    return True
                else:
                    # Smart search: find files containing the keyword
                    base_name = os.path.splitext(python_file)[0]  # Remove .py extension
                    parent_dir = os.path.abspath('..')
                    
                    # Search for files containing the keyword
                    all_py_files = glob.glob(os.path.join(parent_dir, '**', '*.py'), recursive=True)
                    matches = [f for f in all_py_files if base_name.lower() in os.path.basename(f).lower()]
                    
                    if len(matches) == 1:
                        # Only one match - auto-execute it
                        found_path = matches[0]
                        file_name = os.path.basename(found_path)
                        self.voice_engine.speak(f"Found {file_name}. Executing")
                        self.vscode_controller.run_python_file(found_path)
                        return True
                    elif len(matches) > 1:
                        # Multiple matches - list options
                        file_names = [os.path.basename(f) for f in matches]
                        options = ", ".join(file_names)
                        self.voice_engine.speak(f"Found {len(matches)} files with {base_name}: {options}. Please specify the exact filename")
                        return False
                    else:
                        self.voice_engine.speak(f"File {python_file} not found in project directories")
                        return False
            else:
                self.voice_engine.speak("Please specify the Python file to run")
                return False
                
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            self.voice_engine.speak("Error executing code")
            return False
    
    def _handle_stop_code(self) -> bool:
        """Handle stopping code execution"""
        if not self.vscode_controller:
            self.voice_engine.speak("VS Code controller not available")
            return False
        
        try:
            stopped = self.vscode_controller.stop_all_executions()
            if stopped > 0:
                self.voice_engine.speak(f"Stopped {stopped} running processes")
            else:
                self.voice_engine.speak("No processes running")
            return True
            
        except Exception as e:
            logger.error(f"Stop execution error: {e}")
            self.voice_engine.speak("Error stopping execution")
            return False
    
    def _handle_generate_code(self, command: str) -> bool:
        """Handle code generation"""
        try:
            # Extract description
            description = command.replace('generate code', '').replace('create code', '').replace('write code', '').strip()
            
            if len(description) < 5:
                self.voice_engine.speak("Please describe what code you need")
                return False
            
            self.voice_engine.speak("Generating code. This may take a moment.")
            
            # Generate code using AI
            code = self.ai_assistant.generate_code(description)
            
            if code:
                self.last_generated_code = code

                # Save to file
                import os
                from datetime import datetime
                filename = f"generated_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
                
                if self.vscode_controller:
                    self.vscode_controller.create_file(filename, code)
                    self.vscode_controller.open_file(filename)
                    self.voice_engine.speak(f"Code generated and saved to {filename}. Say paste script in Arduino IDE to paste it directly.")
                else:
                    # Just save without opening
                    with open(filename, 'w') as f:
                        f.write(code)
                    self.voice_engine.speak(f"Code generated and saved to {filename}. Say paste script in Arduino IDE to paste it directly.")
                
                return True
            else:
                self.voice_engine.speak("Could not generate code. AI may not be available.")
                return False
                
        except Exception as e:
            logger.error(f"Code generation error: {e}")
            self.voice_engine.speak("Error generating code")
            return False

    def _handle_paste_generated_script(self, command: str) -> bool:
        """Paste the last generated code into a target app window."""
        if not self.last_generated_code:
            self.voice_engine.speak("I don't have a generated script yet. Ask me to generate code first.")
            return False

        target = 'arduino'
        if any(phrase in command for phrase in ['vs code', 'vscode', 'visual studio code']):
            target = 'vscode'
        elif 'notepad' in command:
            target = 'notepad'

        try:
            import time
            import pyautogui

            launched = False
            if target == 'arduino':
                for app_name in ['arduino ide', 'arduino', 'arduino ide.exe']:
                    if self.app_controller.check_app_installed(app_name):
                        launched = self.app_controller.open_application(app_name)
                        if launched:
                            break
                if not launched:
                    self.voice_engine.speak("I couldn't find Arduino IDE installed on this computer.")
                    return False

                time.sleep(5.0)
                pyautogui.hotkey('ctrl', 'n')

            elif target == 'vscode':
                for app_name in ['vscode', 'vs code', 'visual studio code', 'code']:
                    if self.app_controller.check_app_installed(app_name):
                        launched = self.app_controller.open_application(app_name)
                        if launched:
                            break
                if not launched and self.vscode_controller:
                    self.vscode_controller.open_folder('.')
                    launched = True

                if not launched:
                    self.voice_engine.speak("I couldn't open VS Code on this computer.")
                    return False

                time.sleep(5.0)
                pyautogui.hotkey('ctrl', 'n')

            else:
                if not self.app_controller.check_app_installed('notepad'):
                    self.voice_engine.speak("I couldn't find Notepad installed on this computer.")
                    return False
                launched = self.app_controller.open_application('notepad')
                if not launched:
                    self.voice_engine.speak("I had trouble opening Notepad.")
                    return False
                time.sleep(1.5)

            # Focus the destination editor and paste generated script content.
            time.sleep(0.8)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(self.last_generated_code, interval=0.001)

            app_name = 'Arduino IDE' if target == 'arduino' else ('VS Code' if target == 'vscode' else 'Notepad')
            self.voice_engine.speak(f"Pasted the generated script into {app_name}")
            return True
        except Exception as e:
            logger.error(f"Paste generated script error: {e}")
            self.voice_engine.speak("I could not paste the generated script automatically.")
            return False
    
    def _handle_open_vscode(self, command: str) -> bool:
        """Handle opening VS Code"""
        if not self.vscode_controller:
            self.voice_engine.speak("VS Code controller not available")
            return False
        
        try:
            # Check for file/folder in command
            words = command.split()
            target = None
            
            for i, word in enumerate(words):
                if word in ['file', 'folder']:
                    if i + 1 < len(words):
                        target = words[i + 1]
                        break
            
            if target:
                import os
                if os.path.exists(target):
                    if os.path.isfile(target):
                        self.vscode_controller.open_file(target)
                        self.voice_engine.speak(f"Opening {target} in VS Code")
                    else:
                        self.vscode_controller.open_folder(target)
                        self.voice_engine.speak(f"Opening folder {target} in VS Code")
                    return True
                else:
                    self.voice_engine.speak(f"{target} not found")
                    return False
            else:
                # Just open VS Code
                self.vscode_controller.open_folder('.')
                self.voice_engine.speak("Opening VS Code")
                return True
                
        except Exception as e:
            logger.error(f"VS Code open error: {e}")
            self.voice_engine.speak("Error opening VS Code")
            return False
    
    def _handle_shutdown_jarvis(self) -> bool:
        """Handle Jarvis shutdown"""
        try:
            self.voice_engine.speak("Goodbye! Shutting down Jarvis.")
            logger.info("Jarvis shutdown requested by user")
            # Return special value to signal main loop to exit
            return 'EXIT'
            
        except Exception as e:
            logger.error(f"Error in shutdown: {e}")
            return False
    
    def _handle_shutdown_pc(self) -> bool:
        """Handle PC shutdown"""
        try:
            if self.system_controller:
                self.voice_engine.speak("Shutting down your PC in 5 seconds. Say 'cancel shutdown' to abort.")
                if self.system_controller.shutdown_pc(5):
                    return True
            else:
                self.voice_engine.speak("System controller not available.")
            return False
            
        except Exception as e:
            logger.error(f"Error in PC shutdown: {e}")
            return False
    
    def _handle_restart_pc(self) -> bool:
        """Handle PC restart"""
        try:
            if self.system_controller:
                self.voice_engine.speak("Restarting your PC in 5 seconds. Say 'cancel shutdown' to abort.")
                if self.system_controller.restart_pc(5):
                    return True
            else:
                self.voice_engine.speak("System controller not available.")
            return False
            
        except Exception as e:
            logger.error(f"Error in PC restart: {e}")
            return False
    
    def _handle_sleep_pc(self) -> bool:
        """Handle PC sleep"""
        try:
            if self.system_controller:
                self.voice_engine.speak("Putting your PC to sleep. Goodbye!")
                if self.system_controller.sleep_pc():
                    return True
            else:
                self.voice_engine.speak("System controller not available.")
            return False
            
        except Exception as e:
            logger.error(f"Error putting PC to sleep: {e}")
            return False
    
    def _handle_cancel_shutdown(self) -> bool:
        """Handle cancelling shutdown/restart"""
        try:
            if self.system_controller:
                if self.system_controller.cancel_shutdown():
                    self.voice_engine.speak("Shutdown cancelled.")
                    return True
                else:
                    self.voice_engine.speak("No shutdown in progress.")
            else:
                self.voice_engine.speak("System controller not available.")
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling shutdown: {e}")
            return False
