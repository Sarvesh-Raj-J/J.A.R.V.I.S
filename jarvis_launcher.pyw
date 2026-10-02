"""
J.A.R.V.I.S Launcher with Animated Arc Reactor Splash Screen
Creates a spinning Arc Reactor animation before launching Jarvis
"""

import tkinter as tk
import math
import time
import threading
import subprocess
import sys
import os
import ctypes

# Set Windows App ID for taskbar icon
try:
    myappid = 'jarvis.ai.assistant.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass


class ArcReactorSplash:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S")
        
        # Set window icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "jarvis_icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        # Get screen dimensions for centering
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Window size
        self.width = 400
        self.height = 450
        
        # Center the window
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#000000')
        
        # Make window slightly transparent
        self.root.attributes('-alpha', 0.95)
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=self.width, 
            height=self.height,
            bg='#000000',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Animation variables
        self.rotation = 0
        self.pulse = 0
        self.loading_progress = 0
        self.cx = self.width // 2
        self.cy = 180
        self.radius = 120
        
        # Status text
        self.status_text = self.canvas.create_text(
            self.cx, 350,
            text="INITIALIZING...",
            font=("Consolas", 12, "bold"),
            fill="#00d4ff"
        )
        
        # JARVIS text
        self.canvas.create_text(
            self.cx, 400,
            text="J.A.R.V.I.S",
            font=("Consolas", 24, "bold"),
            fill="#00f0ff"
        )
        
        # Loading bar background
        self.canvas.create_rectangle(
            50, 370, 350, 380,
            fill="#0a1a20",
            outline="#005566"
        )
        
        # Loading bar
        self.loading_bar = self.canvas.create_rectangle(
            50, 370, 50, 380,
            fill="#00d4ff",
            outline=""
        )
        
        # Create reactor elements
        self.create_reactor()
        
        # Start animation
        self.running = True
        self.animate()
        
        # Start Jarvis after animation
        self.root.after(3000, self.launch_jarvis)
        
        self.root.mainloop()
    
    def create_reactor(self):
        """Create the arc reactor visual elements"""
        r = self.radius
        
        # Outer glow circle
        self.outer_glow = self.canvas.create_oval(
            self.cx - r - 10, self.cy - r - 10,
            self.cx + r + 10, self.cy + r + 10,
            outline="#003344", width=20
        )
        
        # Main outer ring
        self.outer_ring = self.canvas.create_oval(
            self.cx - r, self.cy - r,
            self.cx + r, self.cy + r,
            outline="#00a8b5", width=4
        )
        
        # Secondary rings
        self.ring2 = self.canvas.create_oval(
            self.cx - r * 0.85, self.cy - r * 0.85,
            self.cx + r * 0.85, self.cy + r * 0.85,
            outline="#005566", width=2
        )
        
        self.ring3 = self.canvas.create_oval(
            self.cx - r * 0.7, self.cy - r * 0.7,
            self.cx + r * 0.7, self.cy + r * 0.7,
            outline="#00d4ff", width=2
        )
        
        # Rotating arc segments (outer)
        self.arcs = []
        for i in range(8):
            arc = self.canvas.create_arc(
                self.cx - r * 0.92, self.cy - r * 0.92,
                self.cx + r * 0.92, self.cy + r * 0.92,
                start=i * 45 + 5, extent=30,
                outline="#00f0ff", width=3, style='arc'
            )
            self.arcs.append(arc)
        
        # Inner rotating segments
        self.inner_arcs = []
        for i in range(6):
            arc = self.canvas.create_arc(
                self.cx - r * 0.55, self.cy - r * 0.55,
                self.cx + r * 0.55, self.cy + r * 0.55,
                start=i * 60, extent=40,
                outline="#00a8b5", width=2, style='arc'
            )
            self.inner_arcs.append(arc)
        
        # Triangular markers
        self.markers = []
        for i in range(12):
            angle = math.radians(i * 30)
            x1 = self.cx + r * 0.75 * math.cos(angle)
            y1 = self.cy + r * 0.75 * math.sin(angle)
            x2 = self.cx + r * 0.82 * math.cos(angle - 0.08)
            y2 = self.cy + r * 0.82 * math.sin(angle - 0.08)
            x3 = self.cx + r * 0.82 * math.cos(angle + 0.08)
            y3 = self.cy + r * 0.82 * math.sin(angle + 0.08)
            
            marker = self.canvas.create_polygon(
                x1, y1, x2, y2, x3, y3,
                fill="#00d4ff", outline=""
            )
            self.markers.append({'id': marker, 'base_angle': i * 30})
        
        # Core circles
        self.core_outer = self.canvas.create_oval(
            self.cx - r * 0.35, self.cy - r * 0.35,
            self.cx + r * 0.35, self.cy + r * 0.35,
            outline="#00f0ff", fill="#0a1520", width=3
        )
        
        self.core_mid = self.canvas.create_oval(
            self.cx - r * 0.25, self.cy - r * 0.25,
            self.cx + r * 0.25, self.cy + r * 0.25,
            outline="#00d4ff", fill="#051015", width=2
        )
        
        self.core_inner = self.canvas.create_oval(
            self.cx - r * 0.15, self.cy - r * 0.15,
            self.cx + r * 0.15, self.cy + r * 0.15,
            outline="#00ffff", fill="#00a8b5", width=2
        )
        
        # Center bright dot
        self.center = self.canvas.create_oval(
            self.cx - r * 0.06, self.cy - r * 0.06,
            self.cx + r * 0.06, self.cy + r * 0.06,
            fill="#ffffff", outline=""
        )
        
        # Inner triangle (like Iron Man's reactor)
        tri_r = r * 0.28
        self.triangle = self.canvas.create_polygon(
            self.cx, self.cy - tri_r,
            self.cx - tri_r * 0.866, self.cy + tri_r * 0.5,
            self.cx + tri_r * 0.866, self.cy + tri_r * 0.5,
            fill="", outline="#00f0ff", width=2
        )
    
    def animate(self):
        """Animate the arc reactor"""
        if not self.running:
            return
        
        self.rotation += 2
        self.pulse += 0.15
        self.loading_progress = min(self.loading_progress + 1, 100)
        
        r = self.radius
        
        # Rotate outer arcs
        for i, arc in enumerate(self.arcs):
            start = (i * 45 + 5 + self.rotation) % 360
            self.canvas.itemconfig(arc, start=start)
        
        # Counter-rotate inner arcs
        for i, arc in enumerate(self.inner_arcs):
            start = (i * 60 - self.rotation * 1.5) % 360
            self.canvas.itemconfig(arc, start=start)
        
        # Pulse markers
        pulse_scale = 1 + abs(math.sin(self.pulse)) * 0.1
        for marker in self.markers:
            angle = math.radians(marker['base_angle'] + self.rotation * 0.5)
            base_r = r * 0.75 * pulse_scale
            x1 = self.cx + base_r * math.cos(angle)
            y1 = self.cy + base_r * math.sin(angle)
            x2 = self.cx + r * 0.82 * math.cos(angle - 0.08)
            y2 = self.cy + r * 0.82 * math.sin(angle - 0.08)
            x3 = self.cx + r * 0.82 * math.cos(angle + 0.08)
            y3 = self.cy + r * 0.82 * math.sin(angle + 0.08)
            self.canvas.coords(marker['id'], x1, y1, x2, y2, x3, y3)
        
        # Rotate triangle
        tri_r = r * 0.28
        tri_rotation = math.radians(-self.rotation * 0.3)
        points = []
        for i in range(3):
            angle = tri_rotation + i * (2 * math.pi / 3) - math.pi / 2
            x = self.cx + tri_r * math.cos(angle)
            y = self.cy + tri_r * math.sin(angle)
            points.extend([x, y])
        self.canvas.coords(self.triangle, *points)
        
        # Pulse core
        core_pulse = 1 + abs(math.sin(self.pulse * 2)) * 0.15
        core_r = r * 0.15 * core_pulse
        self.canvas.coords(
            self.core_inner,
            self.cx - core_r, self.cy - core_r,
            self.cx + core_r, self.cy + core_r
        )
        
        # Pulse center brightness
        if int(self.pulse * 10) % 2 == 0:
            self.canvas.itemconfig(self.center, fill="#ffffff")
        else:
            self.canvas.itemconfig(self.center, fill="#00ffff")
        
        # Update loading bar
        bar_width = 50 + (300 * self.loading_progress / 100)
        self.canvas.coords(self.loading_bar, 50, 370, bar_width, 380)
        
        # Update status text
        statuses = [
            "INITIALIZING CORE SYSTEMS...",
            "LOADING VOICE ENGINE...",
            "CALIBRATING SENSORS...",
            "CONNECTING MODULES...",
            "SYSTEM READY"
        ]
        status_idx = min(self.loading_progress // 25, 4)
        self.canvas.itemconfig(self.status_text, text=statuses[status_idx])
        
        self.root.after(30, self.animate)
    
    def launch_jarvis(self):
        """Launch the main Jarvis application"""
        self.running = False
        self.root.destroy()
        
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        jarvis_path = os.path.join(script_dir, "jarvis_futuristic_ui.py")
        
        # Get the venv pythonw path (no console)
        venv_pythonw = os.path.join(os.path.dirname(script_dir), "venv", "Scripts", "pythonw.exe")
        venv_python = os.path.join(os.path.dirname(script_dir), "venv", "Scripts", "python.exe")
        
        # Use pythonw to avoid console, with CREATE_NO_WINDOW flag
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        if os.path.exists(venv_pythonw):
            subprocess.Popen(
                [venv_pythonw, jarvis_path], 
                cwd=script_dir,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        elif os.path.exists(venv_python):
            subprocess.Popen(
                [venv_python, jarvis_path], 
                cwd=script_dir,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            subprocess.Popen(
                [sys.executable, jarvis_path], 
                cwd=script_dir,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )


if __name__ == "__main__":
    ArcReactorSplash()
