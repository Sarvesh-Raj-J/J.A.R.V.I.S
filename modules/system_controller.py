"""
System Controller Module
Handles system settings like brightness, volume, focus timer, etc.
"""

import logging
import subprocess
import time
import threading
import os
import sys
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import screen_brightness_control as sbc
    BRIGHTNESS_AVAILABLE = True
except Exception:
    BRIGHTNESS_AVAILABLE = False
    # Brightness control not available (requires compatible monitor/laptop)


class SystemController:
    """Manages system-level settings and controls"""
    
    def __init__(self):
        self.focus_timer_active = False
        self.focus_end_time = None
        self.cv_brightness_process = None
        self.cv_volume_process = None
        self.cv_exit_event = threading.Event()
    
    def set_brightness(self, level: int) -> bool:
        """
        Set screen brightness
        
        Args:
            level: Brightness level (0-100)
            
        Returns:
            bool: True if successful
        """
        try:
            if not BRIGHTNESS_AVAILABLE:
                logger.error("Brightness control not available")
                return False
            
            # Clamp level between 0 and 100
            level = max(0, min(100, level))
            
            sbc.set_brightness(level)
            logger.info(f"Brightness set to {level}%")
            return True
            
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
            return False
    
    def get_brightness(self) -> Optional[int]:
        """Get current screen brightness level"""
        try:
            if not BRIGHTNESS_AVAILABLE:
                return None
            
            brightness = sbc.get_brightness()
            if isinstance(brightness, list):
                brightness = brightness[0]  # Get first display
            
            return brightness
            
        except Exception as e:
            logger.error(f"Error getting brightness: {e}")
            return None
    
    def increase_brightness(self, amount: int = 10) -> bool:
        """Increase brightness by specified amount"""
        try:
            current = self.get_brightness()
            if current is None:
                return False
            
            new_level = min(100, current + amount)
            return self.set_brightness(new_level)
            
        except Exception as e:
            logger.error(f"Error increasing brightness: {e}")
            return False
    
    def decrease_brightness(self, amount: int = 10) -> bool:
        """Decrease brightness by specified amount"""
        try:
            current = self.get_brightness()
            if current is None:
                return False
            
            new_level = max(0, current - amount)
            return self.set_brightness(new_level)
            
        except Exception as e:
            logger.error(f"Error decreasing brightness: {e}")
            return False
    
    def set_volume(self, level: int) -> bool:
        """
        Set system volume (Windows)
        
        Args:
            level: Volume level (0-100)
            
        Returns:
            bool: True if successful
        """
        try:
            level = max(0, min(100, level))
            
            # Use PowerShell to set volume
            ps_command = f"""
            Add-Type -TypeDefinition @"
            using System;
            using System.Runtime.InteropServices;
            public class Audio {{
                [DllImport("user32.dll")] 
                public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, uint dwExtraInfo);
                public static void SetVolume(int level) {{
                    // Mute first
                    keybd_event(0xAD, 0, 0, 0); 
                    keybd_event(0xAD, 0, 2, 0);
                    System.Threading.Thread.Sleep(100);
                    // Unmute
                    keybd_event(0xAD, 0, 0, 0); 
                    keybd_event(0xAD, 0, 2, 0);
                    System.Threading.Thread.Sleep(100);
                    // Set volume
                    for(int i = 0; i < level/2; i++) {{
                        keybd_event(0xAF, 0, 0, 0); 
                        keybd_event(0xAF, 0, 2, 0);
                        System.Threading.Thread.Sleep(50);
                    }}
                }}
            }}
            "@
            [Audio]::SetVolume({level})
            """
            
            result = subprocess.run(["powershell", "-Command", ps_command], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Volume set to {level}%")
                return True
            else:
                logger.error(f"PowerShell volume control failed: {result.stderr}")
                return False
            
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False
    
    def start_focus_timer(self, minutes: int) -> bool:
        """
        Start a focus/work timer
        
        Args:
            minutes: Duration in minutes
            
        Returns:
            bool: True if successful
        """
        try:
            self.focus_timer_active = True
            self.focus_end_time = time.time() + (minutes * 60)
            logger.info(f"Focus timer started for {minutes} minutes")
            return True
            
        except Exception as e:
            logger.error(f"Error starting focus timer: {e}")
            return False
    
    def get_focus_timer_status(self) -> Optional[int]:
        """Get remaining time on focus timer in seconds"""
        try:
            if not self.focus_timer_active or not self.focus_end_time:
                return None
            
            remaining = int(self.focus_end_time - time.time())
            
            if remaining <= 0:
                self.focus_timer_active = False
                self.focus_end_time = None
                return 0
            
            return remaining
            
        except Exception as e:
            logger.error(f"Error getting timer status: {e}")
            return None
    
    def stop_focus_timer(self) -> bool:
        """Stop the focus timer"""
        try:
            self.focus_timer_active = False
            self.focus_end_time = None
            logger.info("Focus timer stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping timer: {e}")
            return False
    
    def open_display_settings(self) -> bool:
        """Open Windows display settings"""
        try:
            subprocess.Popen(['start', 'ms-settings:display'], shell=True)
            logger.info("Opened display settings")
            return True
            
        except Exception as e:
            logger.error(f"Error opening display settings: {e}")
            return False
    
    def open_focus_assist(self) -> bool:
        """Open Windows Focus Assist settings"""
        try:
            subprocess.Popen(['start', 'ms-settings:quiethours'], shell=True)
            logger.info("Opened focus assist settings")
            return True
            
        except Exception as e:
            logger.error(f"Error opening focus assist: {e}")
            return False
    
    def lock_screen(self) -> bool:
        """Lock the Windows screen"""
        try:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
            logger.info("Screen locked")
            return True
            
        except Exception as e:
            logger.error(f"Error locking screen: {e}")
            return False
    
    def shutdown_pc(self, delay_seconds: int = 5) -> bool:
        """Shutdown the PC with optional delay"""
        try:
            subprocess.Popen(['shutdown', '/s', '/t', str(delay_seconds)])
            logger.info(f"PC shutdown initiated with {delay_seconds}s delay")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down PC: {e}")
            return False
    
    def restart_pc(self, delay_seconds: int = 5) -> bool:
        """Restart the PC with optional delay"""
        try:
            subprocess.Popen(['shutdown', '/r', '/t', str(delay_seconds)])
            logger.info(f"PC restart initiated with {delay_seconds}s delay")
            return True
            
        except Exception as e:
            logger.error(f"Error restarting PC: {e}")
            return False
    
    def sleep_pc(self) -> bool:
        """Put the PC to sleep"""
        try:
            subprocess.Popen(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
            logger.info("PC sleep initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error putting PC to sleep: {e}")
            return False
    
    def cancel_shutdown(self) -> bool:
        """Cancel a pending shutdown or restart"""
        try:
            subprocess.run(['shutdown', '/a'])
            logger.info("Shutdown/restart cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling shutdown: {e}")
            return False
    
    def start_cv_brightness_control(self) -> bool:
        """Start CV-based brightness control in a separate window"""
        try:
            if self.cv_brightness_process and self.cv_brightness_process.poll() is None:
                logger.info("CV brightness control already running")
                return True
            
            # Use the same Python executable that's running the main Jarvis app
            python_executable = sys.executable
            # Construct the absolute path to brightness_control.py
            # Assumes brightness_control.py is in the parent directory of Jarvis_Laptop
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            script_path = os.path.join(base_dir, 'brightness_control.py')

            if not os.path.exists(script_path):
                logger.error(f"Brightness control script not found at: {script_path}")
                return False
            
            # Run in a separate window so it doesn't block Jarvis
            # CREATE_NEW_CONSOLE creates a new console window for the process
            if os.name == 'nt':  # Windows
                self.cv_brightness_process = subprocess.Popen(
                    [python_executable, script_path],
                    cwd=os.path.dirname(script_path),
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:  # Linux/Mac
                self.cv_brightness_process = subprocess.Popen(
                    [python_executable, script_path],
                    cwd=os.path.dirname(script_path),
                    start_new_session=True
                )
            
            logger.info("CV brightness control started in separate window")
            return True
            
        except Exception as e:
            logger.error(f"Error starting CV brightness control: {e}")
            return False
    
    def start_cv_volume_control(self) -> bool:
        """Start CV-based volume control in a separate window"""
        try:
            if self.cv_volume_process and self.cv_volume_process.poll() is None:
                logger.info("CV volume control already running")
                return True
            
            # Use the same Python executable
            python_executable = sys.executable
            
            # Path to the CV volume control script
            script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     'volume_control.py')
            script_path = os.path.abspath(script_path)
            
            if not os.path.exists(script_path):
                logger.error(f"CV volume script not found: {script_path}")
                return False
            
            # Run in a separate window so it doesn't block Jarvis
            if os.name == 'nt':  # Windows
                self.cv_volume_process = subprocess.Popen(
                    [python_executable, script_path],
                    cwd=os.path.dirname(script_path),
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:  # Linux/Mac
                self.cv_volume_process = subprocess.Popen(
                    [python_executable, script_path],
                    cwd=os.path.dirname(script_path),
                    start_new_session=True
                )
            
            logger.info("CV volume control started in separate window")
            return True
            
        except Exception as e:
            logger.error(f"Error starting CV volume control: {e}")
            return False
    
    def stop_cv_brightness_control(self) -> bool:
        """Stop CV-based brightness control"""
        try:
            if self.cv_brightness_process and self.cv_brightness_process.poll() is None:
                self.cv_brightness_process.terminate()
                self.cv_brightness_process.wait(timeout=5)
                logger.info("CV brightness control stopped")
            
            self.cv_brightness_process = None
            return True
            
        except Exception as e:
            logger.error(f"Error stopping CV brightness control: {e}")
            return False
    
    def stop_cv_volume_control(self) -> bool:
        """Stop CV-based volume control"""
        try:
            if self.cv_volume_process and self.cv_volume_process.poll() is None:
                self.cv_volume_process.terminate()
                self.cv_volume_process.wait(timeout=5)
                logger.info("CV volume control stopped")
            
            self.cv_volume_process = None
            return True
            
        except Exception as e:
            logger.error(f"Error stopping CV volume control: {e}")
            return False
    
    def is_cv_brightness_active(self) -> bool:
        """Check if CV brightness control is active"""
        return (self.cv_brightness_process is not None and 
                self.cv_brightness_process.poll() is None)
    
    def is_cv_volume_active(self) -> bool:
        """Check if CV volume control is active"""
        return (self.cv_volume_process is not None and 
                self.cv_volume_process.poll() is None)
