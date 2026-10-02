"""
Application Controller Module
Handles opening applications, files, and system control
"""

import os
import subprocess
import platform
import logging
from typing import Dict, Optional, List
import glob

logger = logging.getLogger(__name__)


class ApplicationController:
    """Manages application launching and file operations"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.app_map = {}
        self.custom_paths = config.get('application_paths', {}).get('custom_mappings', {})
        self._build_app_map()
    
    def _build_app_map(self):
        """Scan system for installed applications"""
        try:
            logger.info("Building application map...")
            
            if platform.system() == "Windows":
                self._scan_windows_apps()
                self._add_common_windows_apps()
            elif platform.system() == "Darwin":  # macOS
                self._scan_macos_apps()
            else:  # Linux
                self._scan_linux_apps()
            
            # Add custom mappings
            self.app_map.update(self.custom_paths)
            
            logger.info(f"Indexed {len(self.app_map)} applications")
            
        except Exception as e:
            logger.error(f"Error building app map: {e}")
    
    def _add_common_windows_apps(self):
        """Add common Windows applications with known paths"""
        userprofile = os.environ.get('USERPROFILE', '')
        
        # VS Code - check multiple possible locations
        vscode_paths = [
            os.path.join(userprofile, 'Desktop', 'Microsoft VS Code', 'Code.exe'),
            os.path.join(userprofile, 'AppData', 'Local', 'Programs', 'Microsoft VS Code', 'Code.exe'),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ]
        
        for vscode_path in vscode_paths:
            if os.path.exists(vscode_path):
                # Add multiple aliases for VS Code
                self.app_map['vscode'] = vscode_path
                self.app_map['vs code'] = vscode_path
                self.app_map['visual studio code'] = vscode_path
                self.app_map['code'] = vscode_path
                logger.info(f"Added VS Code: {vscode_path}")
                break
        
        # Other common apps
        common_apps = {
            'chrome': [
                os.path.join(userprofile, 'AppData', 'Local', 'Google', 'Chrome', 'Application', 'chrome.exe'),
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],
            'firefox': [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ],
            'notepad': [r"C:\Windows\System32\notepad.exe"],
            'calculator': [r"C:\Windows\System32\calc.exe"],
            'explorer': [r"C:\Windows\explorer.exe"],
        }
        
        for app_name, paths in common_apps.items():
            for path in paths:
                if os.path.exists(path):
                    self.app_map[app_name] = path
                    break
    
    def _scan_windows_apps(self):
        """Scan Windows Start Menu for applications"""
        locations = [
            os.path.join(os.environ.get("ProgramData", ""), 
                        r"Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.environ.get("APPDATA", ""), 
                        r"Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.environ.get("USERPROFILE", ""), 
                        r"Desktop")
        ]
        
        for location in locations:
            if not os.path.exists(location):
                continue
                
            for root, dirs, files in os.walk(location):
                for file in files:
                    if file.endswith(".lnk") or file.endswith(".exe"):
                        app_name = file.lower().replace(".lnk", "").replace(".exe", "")
                        full_path = os.path.join(root, file)
                        self.app_map[app_name] = full_path
        
        # Add common system paths (FAST - only top level + common locations)
        system_paths = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
        ]
        
        for sys_path in system_paths:
            if not os.path.exists(sys_path):
                continue
            try:
                for item in os.listdir(sys_path):
                    full_path = os.path.join(sys_path, item)
                    if not os.path.isdir(full_path):
                        continue
                    
                    # Only check top level and bin/ subdirectory (FAST)
                    check_paths = [
                        full_path,
                        os.path.join(full_path, "bin"),
                    ]
                    
                    for check_path in check_paths:
                        if not os.path.exists(check_path):
                            continue
                        try:
                            for file in os.listdir(check_path):
                                if file.endswith(".exe"):
                                    app_name = file.lower().replace(".exe", "")
                                    exe_path = os.path.join(check_path, file)
                                    if app_name not in self.app_map:
                                        self.app_map[app_name] = exe_path
                                        break  # Only take first .exe per folder
                        except (PermissionError, OSError):
                            continue
            except (PermissionError, OSError) as e:
                logger.warning(f"Could not access {sys_path}: {e}")
                continue
    
    def _scan_macos_apps(self):
        """Scan macOS Applications folder"""
        app_locations = [
            "/Applications",
            os.path.expanduser("~/Applications")
        ]
        
        for location in app_locations:
            if not os.path.exists(location):
                continue
            
            for item in os.listdir(location):
                if item.endswith(".app"):
                    app_name = item.lower().replace(".app", "")
                    full_path = os.path.join(location, item)
                    self.app_map[app_name] = full_path
    
    def _scan_linux_apps(self):
        """Scan Linux .desktop files"""
        app_locations = [
            "/usr/share/applications",
            os.path.expanduser("~/.local/share/applications")
        ]
        
        for location in app_locations:
            if not os.path.exists(location):
                continue
            
            for item in os.listdir(location):
                if item.endswith(".desktop"):
                    app_name = item.lower().replace(".desktop", "")
                    full_path = os.path.join(location, item)
                    self.app_map[app_name] = full_path
    
    def open_application(self, app_name: str) -> bool:
        """Open an application by name"""
        try:
            app_name = app_name.lower().strip()
            
            # Direct match
            if app_name in self.app_map:
                logger.info(f"Opening application: {app_name}")
                self._launch_app(self.app_map[app_name])
                return True
            
            # Fuzzy match - but require minimum length and meaningful match
            best_match = None
            best_score = 0
            
            for key, path in self.app_map.items():
                # Skip very short keys (like 'od', 'bc', etc.) to avoid false matches
                if len(key) < 3:
                    continue
                
                # Calculate match score
                score = 0
                
                # Exact substring match (higher score)
                if app_name == key:
                    score = 100
                elif app_name.startswith(key) or key.startswith(app_name):
                    # Prefix match - good
                    score = 80
                elif app_name in key:
                    # app_name is substring of key - moderate
                    # But require it to be a significant portion
                    if len(app_name) >= len(key) * 0.5:
                        score = 60
                elif key in app_name:
                    # key is substring of app_name - be careful here
                    # Only match if key is substantial (>50% of app_name)
                    if len(key) >= len(app_name) * 0.5:
                        score = 50
                
                if score > best_score:
                    best_score = score
                    best_match = (key, path)
            
            if best_match and best_score >= 50:
                logger.info(f"Opening application (fuzzy match, score={best_score}): {best_match[0]}")
                self._launch_app(best_match[1])
                return True
            
            logger.warning(f"Application not found: {app_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error opening application {app_name}: {e}")
            return False
    
    def _launch_app(self, path: str):
        """Launch application based on platform"""
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", path])
            else:  # Linux
                subprocess.Popen([path])
                
        except Exception as e:
            logger.error(f"Error launching app at {path}: {e}")
            raise
    
    def open_file(self, file_path: str) -> bool:
        """Open a file with default application"""
        try:
            if not os.path.exists(file_path):
                # Try to find file
                file_path = self._find_file(file_path)
                
            if os.path.exists(file_path):
                logger.info(f"Opening file: {file_path}")
                
                if platform.system() == "Windows":
                    os.startfile(file_path)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", file_path])
                else:
                    subprocess.Popen(["xdg-open", file_path])
                
                return True
            else:
                logger.warning(f"File not found: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e}")
            return False
    
    def _find_file(self, filename: str) -> Optional[str]:
        """Search for a file in common locations"""
        search_locations = [
            os.path.expanduser("~"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads")
        ]
        
        for location in search_locations:
            try:
                for root, dirs, files in os.walk(location):
                    for file in files:
                        if filename.lower() in file.lower():
                            return os.path.join(root, file)
            except:
                continue
        
        return None
    
    def list_installed_apps(self) -> List[str]:
        """Get list of all indexed applications"""
        return sorted(list(self.app_map.keys()))
    
    def check_app_installed(self, app_name: str) -> bool:
        """Check if an application is installed"""
        app_name = app_name.lower().strip()
        
        # Direct match
        if app_name in self.app_map:
            return True
        
        # Fuzzy match
        for key in self.app_map.keys():
            if app_name in key or key in app_name:
                return True
        
        return False
