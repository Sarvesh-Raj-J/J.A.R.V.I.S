"""
App Actions Module
Provides ability to control applications and execute their functions
"""

import logging
import subprocess
import time
import pyautogui
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AppActions:
    """Execute actions within opened applications"""
    
    def __init__(self):
        self.app_handlers = {
            'calculator': self._handle_calculator,
            'calc': self._handle_calculator,
            'notepad': self._handle_notepad,
            'chrome': self._handle_browser,
            'firefox': self._handle_browser,
            'edge': self._handle_browser,
        }
    
    def execute_app_action(self, app_name: str, action: str, parameters: Optional[Dict] = None) -> bool:
        """
        Execute an action in a specific application
        
        Args:
            app_name: Name of the application
            action: Action to perform
            parameters: Additional parameters for the action
            
        Returns:
            bool: True if action was successful
        """
        try:
            app_name = app_name.lower().strip()
            
            # Find handler for this app
            handler = None
            for key in self.app_handlers:
                if key in app_name or app_name in key:
                    handler = self.app_handlers[key]
                    break
            
            if handler:
                logger.info(f"Executing {action} in {app_name}")
                return handler(action, parameters or {})
            else:
                logger.warning(f"No handler for app: {app_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing app action: {e}")
            return False
    
    def _handle_calculator(self, action: str, params: Dict) -> bool:
        """Handle calculator-specific actions"""
        try:
            if action == 'calculate':
                expression = params.get('expression', '')
                if not expression:
                    return False
                
                # Give calculator time to open
                time.sleep(0.5)
                
                # Type the expression
                pyautogui.write(expression, interval=0.1)
                
                # Press Enter
                pyautogui.press('enter')
                
                logger.info(f"Sent calculation to calculator: {expression}")
                return True
                
        except Exception as e:
            logger.error(f"Calculator action error: {e}")
            return False
    
    def _handle_notepad(self, action: str, params: Dict) -> bool:
        """Handle notepad-specific actions"""
        try:
            if action == 'write':
                text = params.get('text', '')
                if not text:
                    return False
                
                # Give notepad time to open
                time.sleep(0.5)
                
                # Type the text
                pyautogui.write(text, interval=0.05)
                
                logger.info(f"Wrote text to notepad")
                return True
                
        except Exception as e:
            logger.error(f"Notepad action error: {e}")
            return False
    
    def _handle_browser(self, action: str, params: Dict) -> bool:
        """Handle browser-specific actions"""
        try:
            if action == 'navigate':
                url = params.get('url', '')
                if not url:
                    return False
                
                # Give browser time to open
                time.sleep(1)
                
                # Type URL in address bar
                pyautogui.hotkey('ctrl', 'l')  # Focus address bar
                time.sleep(0.2)
                pyautogui.write(url, interval=0.05)
                pyautogui.press('enter')
                
                logger.info(f"Navigated browser to: {url}")
                return True
            
            elif action == 'search':
                query = params.get('query', '')
                if not query:
                    return False
                
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'l')
                time.sleep(0.2)
                pyautogui.write(query, interval=0.05)
                pyautogui.press('enter')
                
                logger.info(f"Searched in browser: {query}")
                return True
                
        except Exception as e:
            logger.error(f"Browser action error: {e}")
            return False
