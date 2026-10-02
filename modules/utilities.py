"""
Utility Module
Helper functions for internet checking, file operations, etc.
"""

import requests
import logging
import webbrowser
from typing import Optional

logger = logging.getLogger(__name__)


class Utilities:
    """Collection of utility functions"""
    
    @staticmethod
    def check_internet(timeout: int = 3) -> bool:
        """
        Check if internet connection is available
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            bool: True if internet is available
        """
        try:
            response = requests.get('https://www.google.com', timeout=timeout)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            logger.warning("No internet connection")
            return False
        except Exception as e:
            logger.error(f"Error checking internet: {e}")
            return False
    
    @staticmethod
    def open_website(url: str) -> bool:
        """
        Open a website in the default browser
        
        Args:
            url: Website URL to open
            
        Returns:
            bool: True if successful
        """
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            
            logger.info(f"Opening website: {url}")
            webbrowser.open(url)
            return True
            
        except Exception as e:
            logger.error(f"Error opening website: {e}")
            return False
    
    @staticmethod
    def open_website_with_check(url: str, site_name: str = "website") -> tuple[bool, str]:
        """
        Open website after checking internet connectivity
        
        Args:
            url: Website URL
            site_name: Human-readable site name for messages
            
        Returns:
            tuple: (success, message)
        """
        if not Utilities.check_internet():
            msg = "I cannot connect to the internet. Please check your connection."
            logger.warning(msg)
            return False, msg
        
        success = Utilities.open_website(url)
        if success:
            msg = f"Opening {site_name}"
            return True, msg
        else:
            msg = f"Failed to open {site_name}"
            return False, msg
    
    @staticmethod
    def search_web(query: str, engine: str = "google") -> bool:
        """
        Search the web using specified search engine
        
        Args:
            query: Search query
            engine: Search engine (google, bing, duckduckgo)
            
        Returns:
            bool: True if successful
        """
        try:
            engines = {
                'google': 'https://www.google.com/search?q=',
                'bing': 'https://www.bing.com/search?q=',
                'duckduckgo': 'https://duckduckgo.com/?q='
            }
            
            base_url = engines.get(engine.lower(), engines['google'])
            search_url = base_url + query.replace(' ', '+')
            
            logger.info(f"Searching {engine}: {query}")
            return Utilities.open_website(search_url)
            
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return False
    
    @staticmethod
    def get_greeting() -> str:
        """Get time-appropriate greeting"""
        from datetime import datetime
        
        hour = datetime.now().hour
        
        if hour >= 0 and hour < 12:
            return "Good Morning!"
        elif hour >= 12 and hour < 18:
            return "Good Afternoon!"
        else:
            return "Good Evening!"
    
    @staticmethod
    def get_current_time() -> str:
        """Get current time in readable format"""
        from datetime import datetime
        return datetime.now().strftime("%I:%M %p")
    
    @staticmethod
    def get_current_date() -> str:
        """Get current date in readable format"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")
