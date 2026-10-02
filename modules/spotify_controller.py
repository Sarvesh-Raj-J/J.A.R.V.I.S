"""
Spotify Controller
------------------
This module handles Spotify web automation to play music.
Uses a persistent Chrome profile to keep you logged in.
"""

import logging
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

logger = logging.getLogger(__name__)

# Spotify Web Player URL - uses your logged-in session
SPOTIFY_URL = "https://open.spotify.com/"

class SpotifyController:
    """Handles web automation for Spotify."""
    
    def __init__(self):
        self.driver = None
        # Keep browser sessions in the user's application-data directory.
        configured_dir = os.getenv("JARVIS_SPOTIFY_PROFILE")
        default_dir = Path(os.getenv("LOCALAPPDATA", Path.home())) / "Jarvis" / "spotify_user_data"
        self.user_data_dir = configured_dir or str(default_dir)

    def _initialize_driver(self):
        """Initializes the Selenium WebDriver with persistent profile."""
        try:
            logger.info("Initializing Spotify web driver...")
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Use persistent profile to keep login session
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
            options.add_argument("--profile-directory=Default")
            
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            logger.info("Spotify web driver initialized with persistent profile.")
        except Exception as e:
            logger.error(f"Failed to initialize web driver: {e}")
            self.driver = None

    def _ensure_driver_valid(self):
        """Check if driver is valid and reinitialize if needed."""
        if self.driver is None:
            self._initialize_driver()
            return self.driver is not None
        
        try:
            # Try a simple command to check if session is valid
            _ = self.driver.current_url
            return True
        except Exception as e:
            logger.warning(f"Driver session invalid, reinitializing: {e}")
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self._initialize_driver()
            return self.driver is not None

    def play_song(self, song_name: str):
        """
        Opens Spotify web player, searches for a song, and plays it.

        Args:
            song_name (str): The name of the song to play.
        """
        if not self._ensure_driver_valid():
            return "Failed to open Spotify."

        try:
            # Go directly to Spotify (session should be preserved)
            self.driver.get(SPOTIFY_URL)
            time.sleep(3)  # Wait for the page to load

            # Check if login is needed by looking for a login button
            login_buttons = self.driver.find_elements(By.XPATH, "//button[@data-testid='login-button']")
            if login_buttons:
                logger.info("Spotify login required. Please log in manually in the browser.")
                return "I've opened Spotify for you. Please log in to continue. Your session will be saved for next time."

            # Go to the search page
            search_url = f"https://open.spotify.com/search/{song_name.replace(' ', '%20')}"
            self.driver.get(search_url)
            time.sleep(4)

            # Try to find and click the top result or first song row
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # First, try clicking on the top result section
            try:
                # Look for the top result card and hover to reveal play button
                top_result = self.driver.find_elements(By.XPATH, "//div[@data-testid='top-result-card']")
                if top_result:
                    ActionChains(self.driver).move_to_element(top_result[0]).perform()
                    time.sleep(1)
                    play_btn = top_result[0].find_elements(By.XPATH, ".//button[@data-testid='play-button']")
                    if play_btn:
                        play_btn[0].click()
                        return f"Now playing {song_name} on Spotify."
            except Exception as e:
                logger.debug(f"Top result approach failed: {e}")
            
            # Try clicking on the first track row
            try:
                track_rows = self.driver.find_elements(By.XPATH, "//div[@data-testid='tracklist-row']")
                if track_rows:
                    ActionChains(self.driver).move_to_element(track_rows[0]).perform()
                    time.sleep(0.5)
                    # Double click to play
                    ActionChains(self.driver).double_click(track_rows[0]).perform()
                    return f"Now playing {song_name} on Spotify."
            except Exception as e:
                logger.debug(f"Track row approach failed: {e}")
            
            # Fallback: Try any play button on the page
            play_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Play')]")
            if play_buttons:
                logger.info(f"Found play button for '{song_name}'. Clicking it now.")
                ActionChains(self.driver).move_to_element(play_buttons[0]).perform()
                time.sleep(0.5)
                play_buttons[0].click()
                return f"Now playing {song_name} on Spotify."
            else:
                logger.warning(f"Could not find a play button for '{song_name}'.")
                return f"Sorry, I couldn't find '{song_name}' to play on Spotify."

        except Exception as e:
            logger.error(f"An error occurred while trying to play song on Spotify: {e}")
            # Reset driver on error so next attempt reinitializes
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            return "Sorry, I ran into an error with Spotify. Please try again."

    def pause(self):
        """Pause the current playback."""
        if not self._ensure_driver_valid():
            return "Spotify is not open."
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            pause_btn = self.driver.find_elements(By.XPATH, "//button[@data-testid='control-button-pause']")
            if pause_btn:
                pause_btn[0].click()
                return "Paused Spotify."
            return "Could not find pause button. Is music playing?"
        except Exception as e:
            logger.error(f"Error pausing: {e}")
            return "Error pausing Spotify."
    
    def resume(self):
        """Resume playback."""
        if not self._ensure_driver_valid():
            return "Spotify is not open."
        try:
            play_btn = self.driver.find_elements(By.XPATH, "//button[@data-testid='control-button-play']")
            if play_btn:
                play_btn[0].click()
                return "Resumed Spotify playback."
            return "Could not find play button."
        except Exception as e:
            logger.error(f"Error resuming: {e}")
            return "Error resuming Spotify."
    
    def next_track(self):
        """Skip to next track."""
        if not self._ensure_driver_valid():
            return "Spotify is not open."
        try:
            next_btn = self.driver.find_elements(By.XPATH, "//button[@data-testid='control-button-skip-forward']")
            if next_btn:
                next_btn[0].click()
                return "Skipped to next track."
            return "Could not find next button."
        except Exception as e:
            logger.error(f"Error skipping: {e}")
            return "Error skipping track."
    
    def previous_track(self):
        """Go to previous track."""
        if not self._ensure_driver_valid():
            return "Spotify is not open."
        try:
            prev_btn = self.driver.find_elements(By.XPATH, "//button[@data-testid='control-button-skip-back']")
            if prev_btn:
                prev_btn[0].click()
                return "Playing previous track."
            return "Could not find previous button."
        except Exception as e:
            logger.error(f"Error: {e}")
            return "Error going to previous track."

    def close(self):
        """Closes the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            logger.info("Spotify web driver closed.")

if __name__ == '__main__':
    # Example usage:
    controller = SpotifyController()
    controller.play_song("Never Gonna Give You Up")
    time.sleep(20) # Play for 20 seconds
    controller.close()
