"""
VS Code Controller Module
Handles VS Code operations like opening files, running code, stopping execution
"""

import logging
import subprocess
import os
import psutil
import time
from typing import Optional, List

logger = logging.getLogger(__name__)


class VSCodeController:
    """Manages VS Code operations"""
    
    def __init__(self):
        self.running_processes = []
        self.vscode_path = self._find_vscode()
    
    def _find_vscode(self) -> Optional[str]:
        """Find VS Code executable"""
        username = os.environ.get('USERNAME', '')
        userprofile = os.environ.get('USERPROFILE', f'C:\\Users\\{username}')
        
        possible_paths = [
            # Custom Desktop installation (user specific)
            os.path.join(userprofile, 'Desktop', 'Microsoft VS Code', 'Code.exe'),
            # User installation (most common)
            os.path.join(userprofile, 'AppData', 'Local', 'Programs', 'Microsoft VS Code', 'Code.exe'),
            # System installations
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
            # VS Code Insiders
            os.path.join(userprofile, 'AppData', 'Local', 'Programs', 'Microsoft VS Code Insiders', 'Code - Insiders.exe'),
            r"C:\Program Files\Microsoft VS Code Insiders\Code - Insiders.exe",
            # Portable installation
            os.path.join(userprofile, 'VSCode', 'Code.exe'),
            # Scoop installation
            os.path.join(userprofile, 'scoop', 'apps', 'vscode', 'current', 'Code.exe'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found VS Code at: {path}")
                return path
        
        # Try 'code' command in PATH (works if VS Code is in system PATH)
        try:
            result = subprocess.run(
                ['where', 'code'] if os.name == 'nt' else ['which', 'code'],
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                code_path = result.stdout.strip().split('\n')[0]
                logger.info(f"Found VS Code in PATH: {code_path}")
                return 'code'  # Use 'code' command directly
        except Exception as e:
            logger.debug(f"VS Code not in PATH: {e}")
        
        # Try running 'code --version' directly
        try:
            result = subprocess.run(
                ['code', '--version'], 
                capture_output=True, 
                timeout=5,
                shell=True  # Use shell to find in PATH
            )
            if result.returncode == 0:
                logger.info("Found VS Code via 'code' command")
                return 'code'
        except Exception as e:
            logger.debug(f"Could not run 'code' command: {e}")
        
        logger.warning("VS Code not found - please ensure VS Code is installed")
        return None
    
    def open_file(self, file_path: str) -> bool:
        """Open file in VS Code"""
        try:
            if not self.vscode_path:
                logger.error("VS Code not available")
                return False
            
            subprocess.Popen([self.vscode_path, file_path])
            logger.info(f"Opened {file_path} in VS Code")
            return True
            
        except Exception as e:
            logger.error(f"Error opening file in VS Code: {e}")
            return False
    
    def open_folder(self, folder_path: str) -> bool:
        """Open folder in VS Code"""
        try:
            if not self.vscode_path:
                return False
            
            subprocess.Popen([self.vscode_path, folder_path])
            logger.info(f"Opened folder {folder_path} in VS Code")
            return True
            
        except Exception as e:
            logger.error(f"Error opening folder: {e}")
            return False
    
    def run_python_file(self, file_path: str, in_vscode: bool = True) -> bool:
        """
        Run Python file in VS Code integrated terminal
        
        Args:
            file_path: Path to Python file
            in_vscode: If True, runs in VS Code terminal; else in PowerShell
        """
        try:
            import time
            
            if in_vscode and self.vscode_path:
                # Open file in VS Code
                subprocess.Popen([self.vscode_path, file_path])
                logger.info(f"Opened {file_path} in VS Code")
                time.sleep(1)  # Wait for VS Code to open
                
                # Get the directory and filename
                file_dir = os.path.dirname(os.path.abspath(file_path))
                file_name = os.path.basename(file_path)
                
                # Open VS Code with the file and execute in integrated terminal
                # Use VS Code command to open folder and run terminal command
                cmd_path = self.vscode_path if self.vscode_path != 'code' else 'code'
                
                # Create a temporary script to run in VS Code terminal
                script_content = f'cd "{file_dir}" && python "{file_name}"'
                
                # Try to use VS Code's integrated terminal via command
                try:
                    # Open integrated terminal and run the command
                    subprocess.Popen([
                        cmd_path,
                        file_dir,  # Open the folder
                        '--new-window'  # In new window
                    ])
                    time.sleep(1.5)
                    
                    logger.info(f"Opened in VS Code - Use terminal or press F5 to run")
                except Exception as e:
                    logger.warning(f"Could not open VS Code terminal: {e}")
                
                # For now, still track the process if running externally
                process = subprocess.Popen(
                    ['python', file_path],
                    cwd=file_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                
                self.running_processes.append({
                    'process': process,
                    'file': file_path,
                    'start_time': time.time()
                })
                
                logger.info(f"Opened VS Code and started execution")
                return True
            else:
                # Run in PowerShell console window
                process = subprocess.Popen(
                    ['python', file_path],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                
                self.running_processes.append({
                    'process': process,
                    'file': file_path,
                    'start_time': time.time()
                })
                
                logger.info(f"Started execution in console")
                return True
            
        except Exception as e:
            logger.error(f"Error running Python file: {e}")
            return False
    
    def stop_all_executions(self) -> int:
        """Stop all running code executions"""
        stopped = 0
        
        for proc_info in self.running_processes[:]:
            try:
                process = proc_info['process']
                if process.poll() is None:  # Still running
                    process.terminate()
                    process.wait(timeout=2)
                    stopped += 1
                    logger.info(f"Stopped execution of {proc_info['file']}")
                
                self.running_processes.remove(proc_info)
                
            except Exception as e:
                logger.error(f"Error stopping process: {e}")
        
        return stopped
    
    def get_running_count(self) -> int:
        """Get count of running processes"""
        # Clean up finished processes
        self.running_processes = [
            p for p in self.running_processes 
            if p['process'].poll() is None
        ]
        return len(self.running_processes)
    
    def create_file(self, file_path: str, content: str) -> bool:
        """Create a new file with content"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating file: {e}")
            return False
