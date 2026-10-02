"""
Voice Engine Module
Handles all voice input/output operations with customization support
"""

import pyttsx3
import speech_recognition as sr
import logging
from typing import Optional, Dict
import threading
import time

logger = logging.getLogger(__name__)


class VoiceEngine:
    """Manages voice recognition and text-to-speech operations"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.engine = pyttsx3.init('sapi5')
        self.recognizer = sr.Recognizer()
        self.current_profile = "default"
        self.stop_speaking = False
        self.speech_lock = threading.Lock()
        self.esc_listener_thread = None
        self.keyboard_available = False
        
        # Apply initial voice settings
        self.apply_voice_profile(self.current_profile)
        
        # Get available voices for customization
        self.available_voices = self.engine.getProperty('voices')
        logger.info(f"Voice engine initialized with {len(self.available_voices)} voices")
        
        # Setup keyboard interrupt listener
        self._setup_keyboard_listener()
    
    def apply_voice_profile(self, profile_name: str = "default"):
        """Apply a voice profile configuration"""
        try:
            profiles = self.config.get('voice_profiles', {})
            if profile_name not in profiles:
                profile_name = "default"
            
            profile = profiles[profile_name]
            voices = self.engine.getProperty('voices')
            
            voice_idx = profile.get('voice_index', 0)
            if voice_idx < len(voices):
                self.engine.setProperty('voice', voices[voice_idx].id)
            
            self.engine.setProperty('rate', profile.get('rate', 170))
            self.engine.setProperty('volume', profile.get('volume', 1.0))
            
            self.current_profile = profile_name
        except Exception as e:
            logger.error(f"Error applying voice profile: {e}")
    
    def _setup_keyboard_listener(self):
        """Setup keyboard listener for Escape key interrupt"""
        try:
            import keyboard
            self.keyboard_available = True
            logger.info("Keyboard library available - ESC interrupt enabled")
        except ImportError:
            logger.warning("keyboard library not available - ESC interrupt disabled")
            self.keyboard_available = False
        except Exception as e:
            logger.warning(f"Could not setup keyboard listener: {e}")
            self.keyboard_available = False
    
    def _esc_listener(self):
        """Background thread that listens for ESC or F key during speech"""
        try:
            import keyboard
            while not self.stop_speaking and self.esc_listener_thread:
                if keyboard.is_pressed('esc') or keyboard.is_pressed('f'):
                    logger.info("Interrupt key pressed - stopping speech")
                    self._interrupt_speech()
                    break
                time.sleep(0.05)  # Check every 50ms for responsive interrupt
        except Exception as e:
            logger.error(f"Error in ESC listener thread: {e}")
    
    def _start_esc_listener(self):
        """Start the ESC listener thread"""
        if self.keyboard_available and not self.esc_listener_thread:
            self.esc_listener_thread = threading.Thread(target=self._esc_listener, daemon=True)
            self.esc_listener_thread.start()
    
    def _stop_esc_listener(self):
        """Stop the ESC listener thread"""
        if self.esc_listener_thread:
            self.esc_listener_thread = None
    
    def _interrupt_speech(self):
        """Interrupt ongoing speech immediately"""
        self.stop_speaking = True
        try:
            self.engine.stop()
            # Force end the loop if running
            try:
                self.engine.endLoop()
            except:
                pass
            logger.info("Speech interrupted by user")
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
    
    def force_stop(self):
        """Force stop speech - can be called from external threads"""
        self.stop_speaking = True
        try:
            self.engine.stop()
            try:
                self.engine.endLoop()
            except:
                pass
        except:
            pass
    
    def speak(self, text: str, print_output: bool = True):
        """Convert text to speech with interrupt support"""
        with self.speech_lock:
            try:
                self.stop_speaking = False
                
                if print_output:
                    print(f"Jarvis: {text}")
                
                # Check if already interrupted before speaking
                if self.stop_speaking:
                    return
                
                # Use threaded approach for interruptible speech
                speech_done = threading.Event()
                
                def on_end(name, completed):
                    speech_done.set()
                
                self.engine.connect('finished-utterance', on_end)
                self.engine.say(text)
                self.engine.startLoop(False)
                
                # Check for interrupt while speaking
                while not speech_done.is_set() and not self.stop_speaking:
                    self.engine.iterate()
                    # Check keyboard directly for more responsive interrupt
                    if self.keyboard_available:
                        try:
                            import keyboard
                            if keyboard.is_pressed('f') or keyboard.is_pressed('esc'):
                                self.stop_speaking = True
                                break
                        except:
                            pass
                    time.sleep(0.01)  # Small delay to prevent CPU spinning
                
                # Stop and cleanup
                try:
                    self.engine.endLoop()
                except:
                    pass
                
                # If interrupted, stop immediately
                if self.stop_speaking:
                    try:
                        self.engine.stop()
                    except:
                        pass
                    print(" [Speech interrupted]")
                
            except Exception as e:
                if not self.stop_speaking:
                    logger.error(f"Error in speak: {e}")
                print(f"Jarvis: {text}")  # Fallback to print
            finally:
                self.stop_speaking = False
                self._stop_esc_listener()
    
    def listen(self) -> Optional[str]:
        """Listen for audio input and convert to text"""
        try:
            # Check if microphone is available
            try:
                with sr.Microphone() as source:
                    pass
            except OSError as e:
                if "PyAudio" in str(e):
                    print(" [Error: PyAudio not available. Please install: pip install PyAudio]")
                    logger.error("PyAudio not available for microphone input")
                    # Sleep to prevent infinite loop
                    import time
                    time.sleep(2)
                    return None
                else:
                    print(f" [Microphone error: {e}]")
                    logger.error(f"Microphone error: {e}")
                    import time
                    time.sleep(2)
                    return None
            
            with sr.Microphone() as source:
                print("Listening...", end='', flush=True)
                
                # Adjust for ambient noise (quick calibration)
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                # Get recognition config (reduced timeouts for faster response)
                rec_config = self.config.get('recognition', {})
                timeout = rec_config.get('timeout', 3)  # Reduced from 5 to 3 seconds
                phrase_limit = rec_config.get('phrase_time_limit', 5)  # Reduced from 10 to 5 seconds
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_limit
                )
                
                print(" Got it! Recognizing...")
                
                # Recognize speech using Google
                language = rec_config.get('language', 'en-in')
                query = self.recognizer.recognize_google(audio, language=language)
                
                print(f"User said: {query}\n")
                logger.info(f"Recognized: {query}")
                
                return query.lower()
                
        except sr.WaitTimeoutError:
            print(" [Timeout - no speech detected]")
            logger.debug("Listening timeout")
            return None
        except sr.UnknownValueError:
            print(" [Could not understand audio]")
            logger.debug("Could not understand audio")
            return None
        except OSError as e:
            if "No Default Input Device Available" in str(e):
                print("\n\n⚠ ERROR: No microphone detected!")
                print("Please connect a microphone and restart Jarvis.\n")
                logger.error("Microphone not available")
                raise
            else:
                logger.error(f"Audio device error: {e}")
                return None
        except Exception as e:
            logger.error(f"Error in listen: {e}")
            print(f" [Error: {e}]")
            return None
    
    def set_voice_parameters(self, rate: Optional[int] = None, 
                           volume: Optional[float] = None,
                           voice_index: Optional[int] = None):
        """Dynamically adjust voice parameters"""
        try:
            if rate is not None:
                self.engine.setProperty('rate', rate)
            
            if volume is not None:
                self.engine.setProperty('volume', volume)
            
            if voice_index is not None:
                voices = self.engine.getProperty('voices')
                if voice_index < len(voices):
                    self.engine.setProperty('voice', voices[voice_index].id)
            
            logger.info(f"Updated voice parameters: rate={rate}, volume={volume}, voice={voice_index}")
            
        except Exception as e:
            logger.error(f"Error setting voice parameters: {e}")
    
    def list_available_voices(self):
        """Get list of available voices"""
        voices_info = []
        for idx, voice in enumerate(self.available_voices):
            voices_info.append({
                'index': idx,
                'name': voice.name,
                'id': voice.id,
                'languages': voice.languages
            })
        return voices_info
