"""
AI Integration Module
Handles Ollama AI with TTS and speech recognition support
"""

import requests
import json
import logging
import os
from typing import Dict, List, Optional
import speech_recognition as sr
import pyttsx3

logger = logging.getLogger(__name__)


class AIAssistant:
    """Manages Ollama AI with TTS and speech recognition utilities"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.conversation_history: List[Dict] = []
        
        # Ollama configuration
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
        self.models_to_try = ['phi3:3.8b', 'gemma3:4b', 'gemma2:2b', 'mistral', 'neural-chat']
        
        # TTS and speech recognition utilities
        self.tts_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        
        logger.info(f"AIAssistant initialized with Ollama at {self.ollama_url}")
        logger.info("TTS and speech recognition utilities available")
    
    def query(self, prompt: str, use_context: bool = True) -> Optional[str]:
        """
        Query the Ollama AI model with a prompt
        
        Args:
            prompt: The user's query/prompt
            use_context: Whether to include conversation history
            
        Returns:
            str: AI response or fallback response
        """
        query_text = (prompt or "").strip()
        if not query_text:
            return "I didn't catch that. Could you repeat?"
        
        # Try to get response from Ollama
        ollama_response = self._query_ollama(query_text)
        if ollama_response:
            return ollama_response
        
        # Fall back to simple pattern matching
        return self._fallback_response(query_text)
    
    def _query_ollama(self, prompt: str) -> Optional[str]:
        """
        Query Ollama model for intelligent responses
        
        Args:
            prompt: The user's query
            
        Returns:
            str: Ollama response or None if unavailable
        """
        try:
            # Try available models directly - skip health check to avoid timeout delays
            for model in self.models_to_try:
                try:
                    payload = {
                        'model': model,
                        'prompt': prompt,
                        'stream': False,
                        'temperature': 0.7
                    }
                    
                    logger.debug(f"Querying Ollama with model: {model}")
                    response = requests.post(self.ollama_url, json=payload, timeout=45)
                    
                    if response.status_code == 200:
                        data = response.json()
                        result = data.get('response', '').strip()
                        if result:
                            logger.info(f"✓ Ollama ({model}) responded: {result[:80]}...")
                            return result
                        else:
                            logger.debug(f"Ollama ({model}) returned empty response")
                    else:
                        logger.debug(f"Ollama ({model}) returned status {response.status_code}")
                        
                except (requests.ConnectionError, requests.Timeout) as e:
                    logger.debug(f"Ollama ({model}) error: {str(e)[:50]}")
                    continue
                except Exception as e:
                    logger.debug(f"Ollama ({model}) exception: {str(e)[:50]}")
                    continue
            
            logger.warning("No Ollama models produced a response")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error in _query_ollama: {e}")
            return None
    
    def check_ollama_health(self) -> bool:
        """Check if Ollama is running and responsive"""
        try:
            response = requests.get(
                f"{self.ollama_url.replace('/api/generate', '')}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                logger.info(f"✓ Ollama is healthy. Available models: {len(models)}")
                if models:
                    model_names = [m.get('name', 'unknown') for m in models]
                    logger.info(f"  Models: {', '.join(model_names[:3])}")
                return True
            else:
                logger.warning(f"Ollama returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ Ollama health check failed: {e}")
            return False
    
    def speak(self, text: str) -> None:
        """Use TTS to speak text"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            logger.info(f"TTS: {text[:50]}...")
        except Exception as e:
            logger.error(f"TTS error: {e}")
    
    def listen_from_mic(self, timeout: int = 5) -> Optional[str]:
        """Listen to microphone and return transcribed text"""
        try:
            with sr.Microphone() as source:
                logger.info("Listening for speech...")
                audio = self.recognizer.listen(source, timeout=timeout)
                
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            logger.error(f"Listen error: {e}")
            return None
    
    def _build_context(self) -> str:
        """Build conversation context from history"""
        if not self.conversation_history:
            return ""
        
        context_str = "Recent conversation:\n"
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            context_str += f"{role.capitalize()}: {content}\n"
        
        return context_str
    
    def clear_context(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation context cleared")
    
    def _add_to_history(self, user_msg: str, assistant_msg: str):
        """Add exchange to conversation history"""
        self.conversation_history.append({
            'role': 'user',
            'content': user_msg
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': assistant_msg
        })
        
        # Trim history if too long (keep last 10 exchanges)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def _fallback_response(self, prompt: str) -> str:
        """Provide fallback responses when AI/Ollama is unavailable"""
        prompt_lower = prompt.lower()
        
        # Simple pattern matching for common queries
        if any(word in prompt_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! How can I help you?"
        
        elif any(word in prompt_lower for word in ['how are you', 'how do you do']):
            return "I'm functioning well, thank you for asking!"
        
        elif any(word in prompt_lower for word in ['who are you', 'what are you']):
            return "I am Jarvis, your personal desktop assistant. I can help you with various tasks like opening applications, sending emails, and answering questions."
        
        elif any(word in prompt_lower for word in ['thank', 'thanks']):
            return "You're welcome!"
        
        elif 'time' in prompt_lower:
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}"
        
        elif 'date' in prompt_lower:
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            return f"Today is {current_date}"
        
        else:
            # Simple echo response for unknown inputs
            # This acknowledges what the user said instead of asking generic questions
            words = prompt_lower.split()
            if words:
                first_word = words[0]
                # Acknowledge their input
                if len(words) == 1:
                    # Single word - echo with interest
                    return f"Interesting - {prompt}. I'm trying to reach Ollama to give you a better response."
                else:
                    # Multiple words - summarize
                    return f"I heard you say '{prompt}'. Ollama is processing your request..."
            
            return "I didn't catch that. Could you say it again?"
    
    def generate_code(self, description: str, language: str = "python") -> Optional[str]:
        """
        Generate code based on description using Ollama
        
        Args:
            description: What the code should do
            language: Programming language (default: python)
            
        Returns:
            str: Generated code or None if failed
        """
        try:
            prompt = f"""You are an expert programmer. Generate clean, well-commented {language} code for the following task:

Task: {description}

Requirements:
- Write production-ready code
- Include proper error handling
- Add helpful comments
- Follow best practices
- Make it efficient and readable

Generate only the code, no explanations:"""
            
            payload = {
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3  # Lower temperature for more consistent code
            }
            
            for model in self.models_to_try:
                try:
                    payload["model"] = model
                    response = requests.post(self.ollama_url, json=payload, timeout=60)
                    
                    if response.status_code == 200:
                        result = response.json()
                        code = result.get('response', '').strip()
                        if code:
                            logger.info(f"Generated {language} code ({len(code)} chars) with {model}")
                            return code
                except (requests.ConnectionError, requests.Timeout):
                    continue
            
            logger.warning("Code generation failed - no available models")
            return None
                
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return None
    
    def get_model_info(self) -> Dict:
        """Get information about the AI configuration"""
        return {
            'ollama_url': self.ollama_url,
            'models': self.models_to_try,
            'history_length': len(self.conversation_history),
            'tts_available': True,
            'speech_recognition_available': True
        }
