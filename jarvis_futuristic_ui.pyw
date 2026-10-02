"""
J.A.R.V.I.S - Advanced Holographic Interface
Cinematic Iron Man inspired AI assistant interface
Designed for maximum visual impact and professional aesthetics
"""

import os
import runpy

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    runpy.run_path(os.path.join(script_dir, "jarvis_futuristic_ui.py"), run_name="__main__")
    raise SystemExit

import tkinter as tk
from tkinter import font as tkfont
import threading
import queue
import time
import math
import random
from datetime import datetime
import json
import os
import sys
import ctypes

# Set Windows App ID for taskbar icon
try:
    myappid = 'jarvis.ai.assistant.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# Optional imports for enhanced features
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# CV Control imports
try:
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    from PIL import Image, ImageTk
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False
    print("CV controls not available - install opencv-python, mediapipe, pillow")

# Brightness control
try:
    import screen_brightness_control as sbc
    BRIGHTNESS_AVAILABLE = True
except ImportError:
    BRIGHTNESS_AVAILABLE = False

# Volume control using pycaw - import later to avoid COM conflicts
VOLUME_AVAILABLE = True  # Will be checked at runtime


class ColorScheme:
    """Professional color palette"""
    # Primary colors
    BACKGROUND = '#000000'
    PANEL_BG = '#0a0a0a'
    
    # Accent colors
    CYAN_BRIGHT = '#00f0ff'
    CYAN_MID = '#00a8b5'
    CYAN_DARK = '#005566'
    CYAN_GLOW = '#00ffff'
    
    # Secondary accents
    BLUE_BRIGHT = '#4da6ff'
    BLUE_MID = '#0066cc'
    
    # Status colors
    ACTIVE_GREEN = '#00ff88'
    WARNING_ORANGE = '#ff9500'
    ERROR_RED = '#ff3355'
    
    # Text colors
    TEXT_PRIMARY = '#ffffff'
    TEXT_SECONDARY = '#88ccdd'
    TEXT_DIM = '#446677'
    
    # UI elements
    BORDER = '#1a3a4a'
    BORDER_BRIGHT = '#00d4ff'
    GRID = '#0a1a20'


class WaveformVisualizer:
    """Sophisticated audio waveform visualization"""
    
    def __init__(self, canvas, x, y, width, height):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.points = 100
        self.wave_data = [0] * self.points
        self.target_data = [0] * self.points
        self.line_id = None
        self.glow_id = None
        self.phase = 0
        self.is_active = False
        
        self._create_waveform()
    
    def _create_waveform(self):
        """Create initial waveform line"""
        points = self._calculate_points([0] * self.points)
        
        # Glow effect (thicker, more transparent)
        self.glow_id = self.canvas.create_line(
            *points, fill=ColorScheme.CYAN_DARK, 
            width=6, smooth=True, capstyle='round'
        )
        
        # Main line
        self.line_id = self.canvas.create_line(
            *points, fill=ColorScheme.CYAN_BRIGHT, 
            width=2, smooth=True, capstyle='round'
        )
    
    def _calculate_points(self, data):
        """Calculate line points from wave data"""
        points = []
        step = self.width / (self.points - 1)
        center_y = self.y + self.height / 2
        
        for i, value in enumerate(data):
            x = self.x + i * step
            y = center_y - value * (self.height / 2) * 0.8
            points.extend([x, y])
        
        return points
    
    def update(self, speaking=False, listening=False):
        """Update waveform animation"""
        self.phase += 0.15
        
        if speaking:
            # Dynamic speaking pattern
            for i in range(self.points):
                freq1 = math.sin(self.phase * 2 + i * 0.3) * 0.4
                freq2 = math.sin(self.phase * 3.7 + i * 0.2) * 0.25
                freq3 = math.sin(self.phase * 5.3 + i * 0.15) * 0.15
                noise = random.uniform(-0.1, 0.1)
                self.target_data[i] = freq1 + freq2 + freq3 + noise
        elif listening:
            # Subtle listening pattern
            for i in range(self.points):
                wave = math.sin(self.phase + i * 0.1) * 0.15
                self.target_data[i] = wave + random.uniform(-0.05, 0.05)
        else:
            # Idle flat line with subtle pulse
            pulse = math.sin(self.phase * 0.5) * 0.03
            for i in range(self.points):
                self.target_data[i] = pulse
        
        # Smooth transition
        for i in range(self.points):
            self.wave_data[i] += (self.target_data[i] - self.wave_data[i]) * 0.3
        
        # Update line
        points = self._calculate_points(self.wave_data)
        self.canvas.coords(self.glow_id, *points)
        self.canvas.coords(self.line_id, *points)
    
    def reposition(self, new_x, new_y, new_width=None):
        """Reposition the waveform"""
        self.x = new_x
        self.y = new_y
        if new_width:
            self.width = new_width
        # Redraw will happen on next update()


class ArcReactor:
    """Central Arc Reactor visualization"""
    
    def __init__(self, canvas, x, y, radius):
        self.canvas = canvas
        self.cx = x
        self.cy = y
        self.radius = radius
        self.rotation = 0
        self.pulse = 0
        self.elements = {}
        self.is_active = False
        self.audio_level = 0
        
        self._create_reactor()
    
    def _create_reactor(self):
        """Create the arc reactor elements"""
        r = self.radius
        
        # Outer ring segments
        self.elements['outer_rings'] = []
        for i in range(3):
            ring_r = r * (0.95 - i * 0.08)
            ring = self.canvas.create_oval(
                self.cx - ring_r, self.cy - ring_r,
                self.cx + ring_r, self.cy + ring_r,
                outline=ColorScheme.CYAN_DARK if i > 0 else ColorScheme.CYAN_MID,
                width=2 if i == 0 else 1
            )
            self.elements['outer_rings'].append(ring)
        
        # Rotating arc segments
        self.elements['arcs'] = []
        for i in range(8):
            start = i * 45 + 10
            arc = self.canvas.create_arc(
                self.cx - r * 0.85, self.cy - r * 0.85,
                self.cx + r * 0.85, self.cy + r * 0.85,
                start=start, extent=25,
                outline=ColorScheme.CYAN_BRIGHT, width=3, style='arc'
            )
            self.elements['arcs'].append(arc)
        
        # Inner rotating segments
        self.elements['inner_arcs'] = []
        for i in range(6):
            start = i * 60 + 15
            arc = self.canvas.create_arc(
                self.cx - r * 0.6, self.cy - r * 0.6,
                self.cx + r * 0.6, self.cy + r * 0.6,
                start=start, extent=30,
                outline=ColorScheme.CYAN_MID, width=2, style='arc'
            )
            self.elements['inner_arcs'].append(arc)
        
        # Triangular markers
        self.elements['markers'] = []
        for i in range(12):
            angle = math.radians(i * 30)
            x1 = self.cx + r * 0.72 * math.cos(angle)
            y1 = self.cy + r * 0.72 * math.sin(angle)
            x2 = self.cx + r * 0.78 * math.cos(angle - 0.05)
            y2 = self.cy + r * 0.78 * math.sin(angle - 0.05)
            x3 = self.cx + r * 0.78 * math.cos(angle + 0.05)
            y3 = self.cy + r * 0.78 * math.sin(angle + 0.05)
            
            marker = self.canvas.create_polygon(
                x1, y1, x2, y2, x3, y3,
                fill=ColorScheme.CYAN_DARK, outline=''
            )
            self.elements['markers'].append({'id': marker, 'base_angle': i * 30})
        
        # Core circles
        self.elements['core_outer'] = self.canvas.create_oval(
            self.cx - r * 0.35, self.cy - r * 0.35,
            self.cx + r * 0.35, self.cy + r * 0.35,
            outline=ColorScheme.CYAN_BRIGHT, width=3
        )
        
        self.elements['core_mid'] = self.canvas.create_oval(
            self.cx - r * 0.25, self.cy - r * 0.25,
            self.cx + r * 0.25, self.cy + r * 0.25,
            outline=ColorScheme.CYAN_MID, fill=ColorScheme.PANEL_BG, width=2
        )
        
        self.elements['core_inner'] = self.canvas.create_oval(
            self.cx - r * 0.15, self.cy - r * 0.15,
            self.cx + r * 0.15, self.cy + r * 0.15,
            outline=ColorScheme.CYAN_GLOW, fill=ColorScheme.CYAN_DARK, width=2
        )
        
        # Center dot
        self.elements['center'] = self.canvas.create_oval(
            self.cx - r * 0.05, self.cy - r * 0.05,
            self.cx + r * 0.05, self.cy + r * 0.05,
            fill=ColorScheme.CYAN_GLOW, outline=''
        )
    
    def update(self, audio_level=0, active=False):
        """Update reactor animation"""
        self.audio_level = audio_level
        self.is_active = active
        self.rotation += 0.8 if active else 0.3
        self.pulse += 0.1
        
        r = self.radius
        
        # Rotate outer arcs
        for i, arc in enumerate(self.elements['arcs']):
            start = (i * 45 + 10 + self.rotation) % 360
            self.canvas.itemconfig(arc, start=start)
        
        # Counter-rotate inner arcs
        for i, arc in enumerate(self.elements['inner_arcs']):
            start = (i * 60 + 15 - self.rotation * 1.5) % 360
            self.canvas.itemconfig(arc, start=start)
        
        # Pulse markers based on audio
        pulse_scale = 1 + audio_level * 0.3 + abs(math.sin(self.pulse)) * 0.1
        for marker in self.elements['markers']:
            angle = math.radians(marker['base_angle'] + self.rotation * 0.5)
            base_r = r * 0.72 * pulse_scale
            x1 = self.cx + base_r * math.cos(angle)
            y1 = self.cy + base_r * math.sin(angle)
            x2 = self.cx + r * 0.78 * math.cos(angle - 0.05)
            y2 = self.cy + r * 0.78 * math.sin(angle - 0.05)
            x3 = self.cx + r * 0.78 * math.cos(angle + 0.05)
            y3 = self.cy + r * 0.78 * math.sin(angle + 0.05)
            self.canvas.coords(marker['id'], x1, y1, x2, y2, x3, y3)
            
            # Color based on audio
            if audio_level > 0.3:
                self.canvas.itemconfig(marker['id'], fill=ColorScheme.CYAN_BRIGHT)
            else:
                self.canvas.itemconfig(marker['id'], fill=ColorScheme.CYAN_DARK)
        
        # Pulse core based on audio
        core_pulse = 1 + audio_level * 0.5
        inner_r = r * 0.15 * core_pulse
        self.canvas.coords(
            self.elements['core_inner'],
            self.cx - inner_r, self.cy - inner_r,
            self.cx + inner_r, self.cy + inner_r
        )
        
        # Update core color based on state
        if audio_level > 0.3:
            self.canvas.itemconfig(self.elements['core_inner'], fill=ColorScheme.CYAN_GLOW)
            self.canvas.itemconfig(self.elements['center'], fill='#ffffff')
        elif active:
            self.canvas.itemconfig(self.elements['core_inner'], fill=ColorScheme.CYAN_BRIGHT)
            self.canvas.itemconfig(self.elements['center'], fill=ColorScheme.CYAN_GLOW)
        else:
            self.canvas.itemconfig(self.elements['core_inner'], fill=ColorScheme.CYAN_DARK)
            self.canvas.itemconfig(self.elements['center'], fill=ColorScheme.CYAN_MID)
    
    def reposition(self, new_cx, new_cy):
        """Reposition the arc reactor to new center"""
        dx = new_cx - self.cx
        dy = new_cy - self.cy
        self.cx = new_cx
        self.cy = new_cy
        
        # Move all elements
        for key, item in self.elements.items():
            if key == 'markers':
                for marker in item:
                    self.canvas.move(marker['id'], dx, dy)
            elif key in ['arcs', 'inner_arcs', 'outer_rings']:
                for arc in item:
                    self.canvas.move(arc, dx, dy)
            else:
                self.canvas.move(item, dx, dy)


class HexagonalGrid:
    """Background hexagonal grid pattern"""
    
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.hexagons = []
        
        self._create_grid()
    
    def _create_grid(self):
        """Create hexagonal grid pattern"""
        hex_size = 40
        rows = int(self.height / (hex_size * 1.5)) + 2
        cols = int(self.width / (hex_size * 1.732)) + 2
        
        for row in range(rows):
            for col in range(cols):
                x = col * hex_size * 1.732
                y = row * hex_size * 1.5
                if row % 2 == 1:
                    x += hex_size * 0.866
                
                if random.random() > 0.7:  # Only draw some hexagons
                    self._draw_hexagon(x, y, hex_size * 0.4)
    
    def _draw_hexagon(self, cx, cy, size):
        """Draw a single hexagon"""
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            points.extend([x, y])
        
        hex_id = self.canvas.create_polygon(
            *points,
            outline=ColorScheme.GRID, fill='', width=1
        )
        self.canvas.tag_lower(hex_id)
        self.hexagons.append(hex_id)
    
    def resize(self, new_width, new_height):
        """Resize the grid"""
        # Delete old hexagons
        for hex_id in self.hexagons:
            self.canvas.delete(hex_id)
        self.hexagons = []
        
        # Update dimensions and recreate
        self.width = new_width
        self.height = new_height
        self._create_grid()


class DataDisplay:
    """Floating data display panel"""
    
    def __init__(self, canvas, x, y, width, height, title, align='left'):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.align = align
        self.data_items = []
        self.elements = {}
        
        self._create_panel()
    
    def _create_panel(self):
        """Create the panel structure"""
        # Corner accents
        corner_size = 15
        accent_color = ColorScheme.CYAN_BRIGHT
        
        # Top-left corner
        self.elements['corner_tl'] = self.canvas.create_line(
            self.x, self.y + corner_size,
            self.x, self.y,
            self.x + corner_size, self.y,
            fill=accent_color, width=2
        )
        
        # Top-right corner
        self.elements['corner_tr'] = self.canvas.create_line(
            self.x + self.width - corner_size, self.y,
            self.x + self.width, self.y,
            self.x + self.width, self.y + corner_size,
            fill=accent_color, width=2
        )
        
        # Bottom-left corner
        self.elements['corner_bl'] = self.canvas.create_line(
            self.x, self.y + self.height - corner_size,
            self.x, self.y + self.height,
            self.x + corner_size, self.y + self.height,
            fill=ColorScheme.CYAN_DARK, width=1
        )
        
        # Bottom-right corner
        self.elements['corner_br'] = self.canvas.create_line(
            self.x + self.width - corner_size, self.y + self.height,
            self.x + self.width, self.y + self.height,
            self.x + self.width, self.y + self.height - corner_size,
            fill=ColorScheme.CYAN_DARK, width=1
        )
        
        # Title bar line
        self.elements['title_line'] = self.canvas.create_line(
            self.x, self.y + 25,
            self.x + self.width, self.y + 25,
            fill=ColorScheme.BORDER, width=1
        )
        
        # Title text
        title_x = self.x + 10 if self.align == 'left' else self.x + self.width - 10
        anchor = 'w' if self.align == 'left' else 'e'
        self.elements['title'] = self.canvas.create_text(
            title_x, self.y + 12,
            text=self.title,
            fill=ColorScheme.CYAN_BRIGHT,
            font=('Segoe UI', 9, 'bold'),
            anchor=anchor
        )
        
        # Status indicator
        ind_x = self.x + self.width - 15 if self.align == 'left' else self.x + 15
        self.elements['indicator'] = self.canvas.create_oval(
            ind_x - 4, self.y + 8,
            ind_x + 4, self.y + 16,
            fill=ColorScheme.ACTIVE_GREEN, outline=''
        )
    
    def add_data_row(self, label, value, color=None):
        """Add a data row to the panel"""
        y_offset = 35 + len(self.data_items) * 22
        
        if y_offset > self.height - 10:
            return None
        
        color = color or ColorScheme.TEXT_SECONDARY
        
        label_x = self.x + 10 if self.align == 'left' else self.x + self.width - 10
        value_x = self.x + self.width - 10 if self.align == 'left' else self.x + 10
        label_anchor = 'w' if self.align == 'left' else 'e'
        value_anchor = 'e' if self.align == 'left' else 'w'
        
        label_id = self.canvas.create_text(
            label_x, self.y + y_offset,
            text=label,
            fill=ColorScheme.TEXT_DIM,
            font=('Segoe UI', 8),
            anchor=label_anchor
        )
        
        value_id = self.canvas.create_text(
            value_x, self.y + y_offset,
            text=value,
            fill=color,
            font=('Consolas', 9),
            anchor=value_anchor
        )
        
        self.data_items.append({'label': label_id, 'value': value_id})
        return len(self.data_items) - 1
    
    def update_value(self, index, value, color=None):
        """Update a data value"""
        if index < len(self.data_items):
            self.canvas.itemconfig(self.data_items[index]['value'], text=value)
            if color:
                self.canvas.itemconfig(self.data_items[index]['value'], fill=color)
    
    def reposition(self, new_x, new_y):
        """Reposition the panel"""
        dx = new_x - self.x
        dy = new_y - self.y
        self.x = new_x
        self.y = new_y
        
        # Move all elements
        for key, elem in self.elements.items():
            self.canvas.move(elem, dx, dy)
        
        # Move data items
        for item in self.data_items:
            self.canvas.move(item['label'], dx, dy)
            self.canvas.move(item['value'], dx, dy)


class ConversationPanel:
    """Scrolling conversation display"""
    
    def __init__(self, parent, x, y, width, height):
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.messages = []
        
        self._create_panel()
    
    def _create_panel(self):
        """Create the conversation panel"""
        # Frame with custom styling
        self.frame = tk.Frame(
            self.parent,
            bg=ColorScheme.PANEL_BG,
            highlightbackground=ColorScheme.BORDER,
            highlightthickness=1
        )
        self.frame.place(x=self.x, y=self.y, width=self.width, height=self.height)
        
        # Header
        header = tk.Frame(self.frame, bg=ColorScheme.PANEL_BG, height=30)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Title with icon
        title_label = tk.Label(
            header,
            text="◈  COMMUNICATION LOG",
            bg=ColorScheme.PANEL_BG,
            fg=ColorScheme.CYAN_BRIGHT,
            font=('Segoe UI', 9, 'bold'),
            anchor='w'
        )
        title_label.pack(side='left', padx=10, pady=5)
        
        # Separator
        sep = tk.Frame(self.frame, bg=ColorScheme.BORDER, height=1)
        sep.pack(fill='x')
        
        # Text widget for messages
        self.text = tk.Text(
            self.frame,
            bg=ColorScheme.BACKGROUND,
            fg=ColorScheme.TEXT_PRIMARY,
            font=('Consolas', 10),
            wrap='word',
            state='disabled',
            cursor='arrow',
            relief='flat',
            padx=15,
            pady=10,
            spacing1=5,
            spacing3=5,
            selectbackground=ColorScheme.CYAN_DARK
        )
        self.text.pack(fill='both', expand=True)
        
        # Configure tags
        self.text.tag_configure('timestamp', foreground=ColorScheme.TEXT_DIM, font=('Consolas', 8))
        self.text.tag_configure('jarvis_label', foreground=ColorScheme.CYAN_BRIGHT, font=('Segoe UI', 9, 'bold'))
        self.text.tag_configure('jarvis', foreground=ColorScheme.TEXT_PRIMARY, font=('Consolas', 10))
        self.text.tag_configure('user_label', foreground=ColorScheme.ACTIVE_GREEN, font=('Segoe UI', 9, 'bold'))
        self.text.tag_configure('user', foreground=ColorScheme.TEXT_SECONDARY, font=('Consolas', 10))
        self.text.tag_configure('system', foreground=ColorScheme.TEXT_DIM, font=('Consolas', 9, 'italic'))
        self.text.tag_configure('error', foreground=ColorScheme.ERROR_RED, font=('Consolas', 10))
    
    def add_message(self, text, msg_type='system'):
        """Add a message to the conversation"""
        self.text.config(state='normal')
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if msg_type == 'jarvis':
            self.text.insert('end', f"{timestamp}  ", 'timestamp')
            self.text.insert('end', "JARVIS: ", 'jarvis_label')
            self.text.insert('end', f"{text}\n\n", 'jarvis')
        elif msg_type == 'user':
            self.text.insert('end', f"{timestamp}  ", 'timestamp')
            self.text.insert('end', "USER: ", 'user_label')
            self.text.insert('end', f"{text}\n\n", 'user')
        elif msg_type == 'error':
            self.text.insert('end', f"{timestamp}  ", 'timestamp')
            self.text.insert('end', f"⚠ {text}\n\n", 'error')
        else:
            self.text.insert('end', f"{timestamp}  ", 'timestamp')
            self.text.insert('end', f"{text}\n", 'system')
        
        self.text.see('end')
        self.text.config(state='disabled')
        self.messages.append({'text': text, 'type': msg_type, 'time': timestamp})
    
    def reposition(self, new_x, new_y):
        """Reposition the conversation panel"""
        self.x = new_x
        self.y = new_y
        self.frame.place(x=self.x, y=self.y, width=self.width, height=self.height)


class StatusBar:
    """Bottom status bar with system metrics"""
    
    def __init__(self, canvas, y, width):
        self.canvas = canvas
        self.y = y
        self.width = width
        self.elements = {}
        
        self._create_bar()
    
    def _create_bar(self):
        """Create status bar elements"""
        # Background
        self.elements['bg'] = self.canvas.create_rectangle(
            0, self.y, self.width, self.y + 35,
            fill=ColorScheme.PANEL_BG, outline=''
        )
        
        # Top border
        self.elements['border'] = self.canvas.create_line(
            0, self.y, self.width, self.y,
            fill=ColorScheme.BORDER, width=1
        )
        
        # Status sections
        section_width = self.width / 5
        
        # CPU
        self.elements['cpu_label'] = self.canvas.create_text(
            section_width * 0.5, self.y + 12,
            text="CPU", fill=ColorScheme.TEXT_DIM,
            font=('Segoe UI', 8)
        )
        self.elements['cpu_value'] = self.canvas.create_text(
            section_width * 0.5, self.y + 25,
            text="---%", fill=ColorScheme.CYAN_BRIGHT,
            font=('Consolas', 10, 'bold')
        )
        
        # Memory
        self.elements['mem_label'] = self.canvas.create_text(
            section_width * 1.5, self.y + 12,
            text="MEMORY", fill=ColorScheme.TEXT_DIM,
            font=('Segoe UI', 8)
        )
        self.elements['mem_value'] = self.canvas.create_text(
            section_width * 1.5, self.y + 25,
            text="---%", fill=ColorScheme.CYAN_BRIGHT,
            font=('Consolas', 10, 'bold')
        )
        
        # Network
        self.elements['net_label'] = self.canvas.create_text(
            section_width * 2.5, self.y + 12,
            text="NETWORK", fill=ColorScheme.TEXT_DIM,
            font=('Segoe UI', 8)
        )
        self.elements['net_value'] = self.canvas.create_text(
            section_width * 2.5, self.y + 25,
            text="ONLINE", fill=ColorScheme.ACTIVE_GREEN,
            font=('Consolas', 10, 'bold')
        )
        
        # Status
        self.elements['status_label'] = self.canvas.create_text(
            section_width * 3.5, self.y + 12,
            text="STATUS", fill=ColorScheme.TEXT_DIM,
            font=('Segoe UI', 8)
        )
        self.elements['status_value'] = self.canvas.create_text(
            section_width * 3.5, self.y + 25,
            text="STANDBY", fill=ColorScheme.WARNING_ORANGE,
            font=('Consolas', 10, 'bold')
        )
        
        # Time
        self.elements['time'] = self.canvas.create_text(
            section_width * 4.5, self.y + 18,
            text="", fill=ColorScheme.TEXT_PRIMARY,
            font=('Consolas', 14)
        )
    
    def update(self, cpu=None, memory=None, status=None):
        """Update status bar values"""
        if cpu is not None:
            color = ColorScheme.ACTIVE_GREEN if cpu < 50 else (
                ColorScheme.WARNING_ORANGE if cpu < 80 else ColorScheme.ERROR_RED
            )
            self.canvas.itemconfig(self.elements['cpu_value'], text=f"{cpu:.0f}%", fill=color)
        
        if memory is not None:
            color = ColorScheme.ACTIVE_GREEN if memory < 60 else (
                ColorScheme.WARNING_ORANGE if memory < 85 else ColorScheme.ERROR_RED
            )
            self.canvas.itemconfig(self.elements['mem_value'], text=f"{memory:.0f}%", fill=color)
        
        if status is not None:
            colors = {
                'STANDBY': ColorScheme.WARNING_ORANGE,
                'ACTIVE': ColorScheme.ACTIVE_GREEN,
                'LISTENING': ColorScheme.CYAN_GLOW,
                'SPEAKING': ColorScheme.CYAN_BRIGHT,
                'ERROR': ColorScheme.ERROR_RED
            }
            self.canvas.itemconfig(
                self.elements['status_value'], 
                text=status, 
                fill=colors.get(status, ColorScheme.TEXT_PRIMARY)
            )
        
        # Update time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.canvas.itemconfig(self.elements['time'], text=current_time)
    
    def reposition(self, new_y, new_width):
        """Reposition the status bar"""
        dy = new_y - self.y
        self.y = new_y
        self.width = new_width
        
        # Move and resize all elements
        for key, elem in self.elements.items():
            self.canvas.move(elem, 0, dy)
        
        # Update background and border widths
        self.canvas.coords(self.elements['bg'], 0, self.y, self.width, self.y + 35)
        self.canvas.coords(self.elements['border'], 0, self.y, self.width, self.y)
        
        # Reposition section items
        section_width = self.width / 5
        self.canvas.coords(self.elements['cpu_label'], section_width * 0.5, self.y + 12)
        self.canvas.coords(self.elements['cpu_value'], section_width * 0.5, self.y + 25)
        self.canvas.coords(self.elements['mem_label'], section_width * 1.5, self.y + 12)
        self.canvas.coords(self.elements['mem_value'], section_width * 1.5, self.y + 25)
        self.canvas.coords(self.elements['net_label'], section_width * 2.5, self.y + 12)
        self.canvas.coords(self.elements['net_value'], section_width * 2.5, self.y + 25)
        self.canvas.coords(self.elements['status_label'], section_width * 3.5, self.y + 12)
        self.canvas.coords(self.elements['status_value'], section_width * 3.5, self.y + 25)
        self.canvas.coords(self.elements['time'], section_width * 4.5, self.y + 18)


class CVControlOverlay:
    """Embedded CV control overlay for brightness/volume gestures"""
    
    def __init__(self, parent, on_close_callback=None):
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.running = False
        self.control_type = None  # 'brightness' or 'volume'
        self.cap = None
        self.landmarker = None
        self.detection_result = None
        self.frame_count = 0
        self.current_value = 50
        
        # Create overlay frame
        self.overlay = None
        self.video_label = None
        self.info_label = None
        self.value_label = None
        self.close_btn = None
        
    def _result_callback(self, result, output_image, timestamp_ms):
        """MediaPipe callback for hand detection results"""
        self.detection_result = result
    
    def _setup_mediapipe(self):
        """Setup MediaPipe hand landmarker"""
        if not CV_AVAILABLE:
            return False
            
        try:
            # Find model path
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            model_path = os.path.join(base_dir, 'hand_landmarker.task')
            
            if not os.path.exists(model_path):
                print(f"Hand landmarker model not found at: {model_path}")
                return False
            
            BaseOptions = mp_python.BaseOptions
            HandLandmarker = vision.HandLandmarker
            HandLandmarkerOptions = vision.HandLandmarkerOptions
            VisionRunningMode = vision.RunningMode
            
            options = HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=model_path),
                running_mode=VisionRunningMode.LIVE_STREAM,
                result_callback=self._result_callback,
                num_hands=1,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            
            self.landmarker = HandLandmarker.create_from_options(options)
            return True
            
        except Exception as e:
            print(f"Failed to setup MediaPipe: {e}")
            return False
    
    def start(self, control_type='brightness'):
        """Start the CV control overlay"""
        if not CV_AVAILABLE:
            print("CV libraries not available")
            return False
        
        self.control_type = control_type
        self.running = True
        self.frame_count = 0
        
        # Get current value
        if control_type == 'brightness' and BRIGHTNESS_AVAILABLE:
            try:
                self.current_value = sbc.get_brightness()[0]
            except:
                self.current_value = 50
        else:
            self.current_value = 50
        
        # Setup MediaPipe
        if not self._setup_mediapipe():
            return False
        
        # Open camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Failed to open camera")
            return False
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Create overlay UI
        self._create_overlay()
        
        # Start video update loop
        self._update_video()
        
        return True
    
    def _create_overlay(self):
        """Create the overlay UI"""
        # Main overlay frame - positioned in center-right
        self.overlay = tk.Frame(
            self.parent,
            bg=ColorScheme.PANEL_BG,
            highlightbackground=ColorScheme.CYAN_BRIGHT,
            highlightthickness=2
        )
        
        # Position: center-right of screen
        overlay_width = 420
        overlay_height = 380
        x_pos = self.parent.winfo_width() - overlay_width - 50
        y_pos = (self.parent.winfo_height() - overlay_height) // 2
        
        self.overlay.place(x=x_pos, y=y_pos, width=overlay_width, height=overlay_height)
        
        # Header
        header = tk.Frame(self.overlay, bg=ColorScheme.PANEL_BG, height=40)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        control_name = "BRIGHTNESS CONTROL" if self.control_type == 'brightness' else "VOLUME CONTROL"
        title = tk.Label(
            header,
            text=f"◈  {control_name}",
            bg=ColorScheme.PANEL_BG,
            fg=ColorScheme.CYAN_BRIGHT,
            font=('Segoe UI', 11, 'bold')
        )
        title.pack(side='left', padx=15, pady=8)
        
        # Close button
        self.close_btn = tk.Label(
            header,
            text="✕",
            bg=ColorScheme.PANEL_BG,
            fg=ColorScheme.ERROR_RED,
            font=('Segoe UI', 14, 'bold'),
            cursor='hand2'
        )
        self.close_btn.pack(side='right', padx=15)
        self.close_btn.bind('<Button-1>', lambda e: self.stop())
        self.close_btn.bind('<Enter>', lambda e: self.close_btn.config(fg='#ff6677'))
        self.close_btn.bind('<Leave>', lambda e: self.close_btn.config(fg=ColorScheme.ERROR_RED))
        
        # Separator
        sep = tk.Frame(self.overlay, bg=ColorScheme.BORDER, height=1)
        sep.pack(fill='x')
        
        # Video frame with border
        video_frame = tk.Frame(
            self.overlay,
            bg=ColorScheme.BACKGROUND,
            highlightbackground=ColorScheme.CYAN_DARK,
            highlightthickness=1
        )
        video_frame.pack(padx=15, pady=10)
        
        # Video label
        self.video_label = tk.Label(
            video_frame,
            bg=ColorScheme.BACKGROUND
        )
        self.video_label.pack()
        
        # Info section
        info_frame = tk.Frame(self.overlay, bg=ColorScheme.PANEL_BG)
        info_frame.pack(fill='x', padx=15)
        
        # Current value display
        self.value_label = tk.Label(
            info_frame,
            text=f"{self.current_value}%",
            bg=ColorScheme.PANEL_BG,
            fg=ColorScheme.CYAN_GLOW,
            font=('Consolas', 28, 'bold')
        )
        self.value_label.pack(pady=5)
        
        # Instructions
        if self.control_type == 'brightness':
            instruction = "Move hand LEFT ← → RIGHT to adjust brightness"
        else:
            instruction = "Move hand DOWN ↓ ↑ UP to adjust volume"
        
        self.info_label = tk.Label(
            info_frame,
            text=instruction,
            bg=ColorScheme.PANEL_BG,
            fg=ColorScheme.TEXT_DIM,
            font=('Segoe UI', 9)
        )
        self.info_label.pack()
        
        # Close hint
        hint_label = tk.Label(
            info_frame,
            text='Say "OK Jarvis" or press ESC to close',
            bg=ColorScheme.PANEL_BG,
            fg=ColorScheme.ACTIVE_GREEN,
            font=('Segoe UI', 8, 'italic')
        )
        hint_label.pack(pady=(5, 0))
    
    def _update_video(self):
        """Update video frame"""
        if not self.running or self.cap is None:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            self.parent.after(33, self._update_video)
            return
        
        # Flip for mirror view
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect hands
        try:
            self.landmarker.detect_async(mp_image, self.frame_count)
            self.frame_count += 1
        except Exception as e:
            pass
        
        # Process detection result
        if self.detection_result and self.detection_result.hand_landmarks:
            hand_landmarks = self.detection_result.hand_landmarks[0]
            
            if self.control_type == 'brightness':
                # Use X position for brightness
                x_pos = hand_landmarks[9].x  # Middle finger knuckle
                x_pos = max(0.0, min(1.0, x_pos))
                self.current_value = int(x_pos * 100)
                
                # Set brightness
                if BRIGHTNESS_AVAILABLE:
                    try:
                        sbc.set_brightness(self.current_value)
                    except:
                        pass
                
                # Draw indicator
                indicator_x = int(x_pos * w)
                cv2.line(frame, (indicator_x, 0), (indicator_x, h), (0, 255, 255), 2)
                
            else:  # volume
                # Use Y position for volume (inverted - up is louder)
                y_pos = 1.0 - hand_landmarks[9].y
                y_pos = max(0.0, min(1.0, y_pos))
                self.current_value = int(y_pos * 100)
                
                # Set volume (using system command)
                self._set_volume(self.current_value)
                
                # Draw indicator
                indicator_y = int((1.0 - y_pos) * h)
                cv2.line(frame, (0, indicator_y), (w, indicator_y), (0, 255, 255), 2)
            
            # Draw hand landmark
            cx = int(hand_landmarks[9].x * w)
            cy = int(hand_landmarks[9].y * h)
            cv2.circle(frame, (cx, cy), 15, (0, 255, 255), -1)
            cv2.circle(frame, (cx, cy), 20, (0, 200, 200), 2)
            
            # Update value display
            self.value_label.config(text=f"{self.current_value}%", fg=ColorScheme.CYAN_GLOW)
            
            # Draw value on frame
            cv2.putText(frame, f"{self.current_value}%", (w - 100, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 200), 2)
        else:
            # No hand detected
            cv2.putText(frame, "Show hand to control", (w//2 - 120, h//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
            self.value_label.config(text=f"{self.current_value}%", fg=ColorScheme.TEXT_DIM)
        
        # Add decorative overlay elements
        cv2.rectangle(frame, (5, 5), (w-5, h-5), (0, 180, 200), 1)
        cv2.rectangle(frame, (10, 10), (w-10, h-10), (0, 100, 120), 1)
        
        # Resize frame for display
        display_width = 380
        display_height = int(display_width * h / w)
        frame_resized = cv2.resize(frame, (display_width, display_height))
        
        # Convert to PhotoImage
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Update label
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)
        
        # Schedule next update
        self.parent.after(33, self._update_video)
    
    def _set_volume(self, level):
        """Set system volume using pycaw"""
        try:
            # Import lazily to avoid COM conflicts with pyttsx3
            from pycaw.pycaw import AudioUtilities
            
            # Get the speakers and volume endpoint
            speakers = AudioUtilities.GetSpeakers()
            volume = speakers.EndpointVolume
            
            # Set volume (pycaw uses 0.0 to 1.0 range)
            volume_level = max(0.0, min(1.0, level / 100.0))
            volume.SetMasterVolumeLevelScalar(volume_level, None)
        except Exception as e:
            print(f"Volume control error: {e}")
    
    def stop(self):
        """Stop the CV control"""
        self.running = False
        
        # Release camera
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        # Close landmarker
        if self.landmarker is not None:
            try:
                self.landmarker.close()
            except:
                pass
            self.landmarker = None
        
        # Destroy overlay
        if self.overlay is not None:
            self.overlay.destroy()
            self.overlay = None
        
        # Callback
        if self.on_close_callback:
            self.on_close_callback()
    
    def is_active(self):
        """Check if CV control is active"""
        return self.running


class JarvisInterface:
    """Main Jarvis Interface - Cinematic Iron Man Style"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S")
        
        # Set taskbar icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "jarvis_icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        # Start in fullscreen mode
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=ColorScheme.BACKGROUND)
        self.root.minsize(1200, 700)
        
        # Bind Escape to exit fullscreen (toggle)
        self.root.bind('<F11>', self._toggle_fullscreen)
        
        # State
        self.is_active = False
        self.is_listening = False
        self.is_speaking = False
        self.running = True
        self.audio_level = 0
        
        # CV Control overlay
        self.cv_control = None
        
        # Queues
        self.message_queue = queue.Queue()
        
        # Jarvis backend
        self.jarvis = None
        self.jarvis_thread = None
        self.interrupt_flag = False  # Flag to interrupt Jarvis
        
        # Setup
        self._setup_fonts()
        self._setup_ui()
        self._start_animation()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind('<Escape>', self._on_escape)
        self.root.bind('<space>', lambda e: self._toggle_active())
        self.root.bind('<f>', self._on_interrupt)
        self.root.bind('<F>', self._on_interrupt)
    
    def _on_interrupt(self, event=None):
        """Handle F key - interrupt Jarvis mid-conversation"""
        self.interrupt_flag = True
        if self.jarvis and self.jarvis.voice_engine:
            try:
                # Use force_stop for immediate interruption
                self.jarvis.voice_engine.force_stop()
            except:
                pass
        self.add_message("Interrupted.", 'system')
        self.set_speaking(False)
        self.set_listening(False)
    
    def _on_escape(self, event=None):
        """Handle escape key - close CV control or exit"""
        if self.cv_control and self.cv_control.is_active():
            self.cv_control.stop()
            self.add_message("Hand gesture control closed.", 'system')
        else:
            self._on_close()
    
    def _toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode with F11"""
        is_fullscreen = self.root.attributes('-fullscreen')
        if is_fullscreen:
            # Exit fullscreen but maximize window
            self.root.attributes('-fullscreen', False)
            self.root.state('zoomed')  # Maximize window
        else:
            # Enter true fullscreen
            self.root.attributes('-fullscreen', True)
        return "break"
    
    def _setup_fonts(self):
        """Setup custom fonts"""
        self.fonts = {
            'title': tkfont.Font(family='Segoe UI Light', size=32, weight='normal'),
            'subtitle': tkfont.Font(family='Segoe UI', size=10),
            'button': tkfont.Font(family='Segoe UI', size=11, weight='bold'),
            'data': tkfont.Font(family='Consolas', size=10),
            'small': tkfont.Font(family='Segoe UI', size=8)
        }
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Main canvas
        self.canvas = tk.Canvas(
            self.root,
            bg=ColorScheme.BACKGROUND,
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Get dimensions
        self.root.update()
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        
        # Create background grid
        self.hex_grid = HexagonalGrid(self.canvas, self.width, self.height)
        
        # Create center arc reactor
        center_x = self.width // 2
        center_y = self.height // 2 - 30
        self.arc_reactor = ArcReactor(self.canvas, center_x, center_y, 150)
        
        # Create waveform below reactor
        wave_width = 500
        self.waveform = WaveformVisualizer(
            self.canvas,
            center_x - wave_width // 2,
            center_y + 180,
            wave_width, 80
        )
        
        # Header
        self._create_header()
        
        # Side panels
        self._create_side_panels()
        
        # Conversation panel
        self.conversation = ConversationPanel(
            self.root, 50, self.height - 280, 400, 230
        )
        
        # Status bar
        self.status_bar = StatusBar(self.canvas, self.height - 40, self.width)
        
        # Control button
        self._create_control_button()
        
        # Bind resize
        self.root.bind('<Configure>', self._on_resize)
    
    def _create_header(self):
        """Create header area"""
        # Main title
        self.canvas.create_text(
            self.width // 2, 40,
            text="J.A.R.V.I.S",
            fill=ColorScheme.CYAN_BRIGHT,
            font=self.fonts['title']
        )
        
        # Subtitle
        self.canvas.create_text(
            self.width // 2, 75,
            text="JUST A RATHER VERY INTELLIGENT SYSTEM",
            fill=ColorScheme.TEXT_DIM,
            font=self.fonts['subtitle']
        )
        
        # Decorative lines
        line_width = 200
        self.canvas.create_line(
            self.width // 2 - line_width, 95,
            self.width // 2 - 50, 95,
            fill=ColorScheme.BORDER, width=1
        )
        self.canvas.create_line(
            self.width // 2 + 50, 95,
            self.width // 2 + line_width, 95,
            fill=ColorScheme.BORDER, width=1
        )
        
        # Version indicator
        self.canvas.create_text(
            self.width - 20, 20,
            text="v3.0.0",
            fill=ColorScheme.TEXT_DIM,
            font=self.fonts['small'],
            anchor='e'
        )
    
    def _create_side_panels(self):
        """Create side data panels"""
        # Left panel - System Status
        self.left_panel = DataDisplay(
            self.canvas, 50, 120, 280, 200, "SYSTEM STATUS", 'left'
        )
        self.sys_cpu = self.left_panel.add_data_row("Processor", "Initializing...", ColorScheme.CYAN_BRIGHT)
        self.sys_mem = self.left_panel.add_data_row("Memory", "Initializing...", ColorScheme.CYAN_BRIGHT)
        self.sys_voice = self.left_panel.add_data_row("Voice Engine", "Ready", ColorScheme.ACTIVE_GREEN)
        self.sys_ai = self.left_panel.add_data_row("AI Core", "Online", ColorScheme.ACTIVE_GREEN)
        self.sys_cmd = self.left_panel.add_data_row("Command Handler", "Active", ColorScheme.ACTIVE_GREEN)
        
        # Right panel - Session Info
        self.right_panel = DataDisplay(
            self.canvas, self.width - 330, 120, 280, 200, "SESSION INFO", 'right'
        )
        self.session_start = self.right_panel.add_data_row("Started", datetime.now().strftime("%H:%M:%S"), ColorScheme.TEXT_SECONDARY)
        self.session_cmds = self.right_panel.add_data_row("Commands", "0", ColorScheme.CYAN_BRIGHT)
        self.session_uptime = self.right_panel.add_data_row("Uptime", "00:00:00", ColorScheme.TEXT_SECONDARY)
        self.session_mode = self.right_panel.add_data_row("Mode", "Standby", ColorScheme.WARNING_ORANGE)
        
        self.start_time = datetime.now()
        self.command_count = 0
    
    def _create_control_button(self):
        """Create main control button"""
        btn_width = 200
        btn_height = 45
        btn_x = self.width // 2 - btn_width // 2
        btn_y = self.height - 100
        
        # Button background
        self.btn_bg = self.canvas.create_rectangle(
            btn_x, btn_y,
            btn_x + btn_width, btn_y + btn_height,
            fill=ColorScheme.PANEL_BG,
            outline=ColorScheme.CYAN_MID,
            width=2
        )
        
        # Button text
        self.btn_text = self.canvas.create_text(
            self.width // 2, btn_y + btn_height // 2,
            text="◉  ACTIVATE",
            fill=ColorScheme.CYAN_BRIGHT,
            font=self.fonts['button']
        )
        
        # Corner accents
        corner = 10
        self.canvas.create_line(
            btn_x, btn_y + corner, btn_x, btn_y, btn_x + corner, btn_y,
            fill=ColorScheme.CYAN_BRIGHT, width=2
        )
        self.canvas.create_line(
            btn_x + btn_width - corner, btn_y, btn_x + btn_width, btn_y, btn_x + btn_width, btn_y + corner,
            fill=ColorScheme.CYAN_BRIGHT, width=2
        )
        
        # Bind events
        self.canvas.tag_bind(self.btn_bg, '<Button-1>', lambda e: self._toggle_active())
        self.canvas.tag_bind(self.btn_text, '<Button-1>', lambda e: self._toggle_active())
        self.canvas.tag_bind(self.btn_bg, '<Enter>', self._on_btn_enter)
        self.canvas.tag_bind(self.btn_bg, '<Leave>', self._on_btn_leave)
    
    def _on_btn_enter(self, event):
        """Button hover enter"""
        self.canvas.itemconfig(self.btn_bg, fill=ColorScheme.CYAN_DARK)
    
    def _on_btn_leave(self, event):
        """Button hover leave"""
        if self.is_active:
            self.canvas.itemconfig(self.btn_bg, fill='#1a3322')
        else:
            self.canvas.itemconfig(self.btn_bg, fill=ColorScheme.PANEL_BG)
    
    def _toggle_active(self):
        """Toggle Jarvis activation"""
        self.is_active = not self.is_active
        
        if self.is_active:
            self.canvas.itemconfig(self.btn_bg, fill='#1a3322', outline=ColorScheme.ACTIVE_GREEN)
            self.canvas.itemconfig(self.btn_text, text="◼  DEACTIVATE", fill=ColorScheme.ACTIVE_GREEN)
            self.status_bar.update(status='ACTIVE')
            self.right_panel.update_value(self.session_mode, "Active", ColorScheme.ACTIVE_GREEN)
            self.add_message("System activated. Voice recognition online.", 'system')
            self.add_message("How may I assist you today, sir?", 'jarvis')
            
            # Start Jarvis backend
            if self.jarvis is None:
                self._start_jarvis()
        else:
            self.canvas.itemconfig(self.btn_bg, fill=ColorScheme.PANEL_BG, outline=ColorScheme.CYAN_MID)
            self.canvas.itemconfig(self.btn_text, text="◉  ACTIVATE", fill=ColorScheme.CYAN_BRIGHT)
            self.status_bar.update(status='STANDBY')
            self.right_panel.update_value(self.session_mode, "Standby", ColorScheme.WARNING_ORANGE)
            self.add_message("Entering standby mode.", 'jarvis')
    
    def _start_jarvis(self):
        """Start Jarvis in background thread"""
        def run_jarvis():
            try:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from jarvis_main import Jarvis
                
                self.jarvis = Jarvis()
                
                # Hook voice engine
                original_speak = self.jarvis.voice_engine.speak
                original_listen = self.jarvis.voice_engine.listen
                
                def hooked_speak(text, print_output=True):
                    self.interrupt_flag = False  # Reset interrupt flag
                    self.set_speaking(True)
                    self.add_message(text, 'jarvis')
                    original_speak(text, print_output=False)
                    self.set_speaking(False)
                
                def hooked_listen():
                    self.interrupt_flag = False  # Reset interrupt flag
                    if not self.is_active:
                        time.sleep(0.1)
                        return None
                    if self.interrupt_flag:
                        self.interrupt_flag = False
                        return None
                    self.set_listening(True)
                    result = original_listen()
                    self.set_listening(False)
                    if self.interrupt_flag:
                        self.interrupt_flag = False
                        return None
                    if result:
                        self.add_message(result, 'user')
                        self.command_count += 1
                        self.right_panel.update_value(self.session_cmds, str(self.command_count))
                    return result
                    return result
                
                self.jarvis.voice_engine.speak = hooked_speak
                self.jarvis.voice_engine.listen = hooked_listen
                
                # Hook system controller CV methods to use embedded UI
                original_start_cv_brightness = self.jarvis.command_handler.system_controller.start_cv_brightness_control
                original_start_cv_volume = self.jarvis.command_handler.system_controller.start_cv_volume_control
                
                def hooked_cv_brightness():
                    # Use UI's embedded CV control instead
                    self.root.after(0, self.start_cv_brightness_control)
                    return True
                
                def hooked_cv_volume():
                    # Use UI's embedded CV control instead
                    self.root.after(0, self.start_cv_volume_control)
                    return True
                
                self.jarvis.command_handler.system_controller.start_cv_brightness_control = hooked_cv_brightness
                self.jarvis.command_handler.system_controller.start_cv_volume_control = hooked_cv_volume
                
                # Greet
                self.add_message("All systems initialized.", 'system')
                self.jarvis.greet_user()
                
                # Set jarvis as active since we're using the UI (no wake phrase needed)
                self.jarvis.is_active = True
                
                # Main loop
                while self.running and self.jarvis.running:
                    if not self.is_active:
                        time.sleep(0.1)
                        continue
                    
                    query = self.jarvis.voice_engine.listen()
                    
                    if not query:
                        continue
                    
                    # Check if CV control is active and user says "ok jarvis" to close it
                    if self.cv_control and self.cv_control.is_active():
                        query_lower = query.lower()
                        if any(phrase in query_lower for phrase in ['ok jarvis', 'okay jarvis', 'fine jarvis', 'stop', 'close', 'done']):
                            self.root.after(0, self.stop_cv_control)
                            self.jarvis.voice_engine.speak("Gesture control closed.")
                            continue
                    
                    # Check for sleep command
                    if self.jarvis.check_sleep_command(query):
                        self.jarvis.voice_engine.speak("Going to sleep. Say 'Hey Jarvis' to wake me.")
                        self.jarvis.is_active = False
                        # Wait for wake phrase
                        while self.running and not self.jarvis.is_active:
                            if not self.is_active:
                                time.sleep(0.1)
                                continue
                            wake_query = self.jarvis.voice_engine.listen()
                            if wake_query and self.jarvis.check_wake_phrase(wake_query):
                                self.jarvis.is_active = True
                                self.jarvis.voice_engine.speak("Yes, I'm here. How can I help?")
                        continue
                    
                    # Process the command directly (no wake phrase needed in UI mode)
                    result = self.jarvis.command_handler.process_command(query)
                    
                    if result == 'EXIT':
                        self.running = False
                        break
                
            except Exception as e:
                self.add_message(f"Error: {str(e)}", 'error')
                import traceback
                traceback.print_exc()
        
        self.jarvis_thread = threading.Thread(target=run_jarvis, daemon=True)
        self.jarvis_thread.start()
    
    def set_speaking(self, speaking):
        """Set speaking state"""
        self.is_speaking = speaking
        if speaking:
            self.status_bar.update(status='SPEAKING')
        elif self.is_active:
            self.status_bar.update(status='ACTIVE')
    
    def set_listening(self, listening):
        """Set listening state"""
        self.is_listening = listening
        if listening:
            self.status_bar.update(status='LISTENING')
        elif self.is_active:
            self.status_bar.update(status='ACTIVE')
    
    def add_message(self, text, msg_type='system'):
        """Thread-safe message adding"""
        self.message_queue.put((text, msg_type))
    
    def start_cv_brightness_control(self):
        """Start embedded CV brightness control"""
        if not CV_AVAILABLE:
            self.add_message("CV libraries not installed. Cannot start gesture control.", 'error')
            return False
        
        if self.cv_control and self.cv_control.is_active():
            self.add_message("Gesture control is already active.", 'system')
            return True
        
        self.add_message("Starting brightness gesture control...", 'system')
        self.cv_control = CVControlOverlay(self.root, self._on_cv_control_closed)
        
        if self.cv_control.start('brightness'):
            self.add_message("Move your hand LEFT/RIGHT to adjust brightness. Say 'OK Jarvis' or press ESC to close.", 'jarvis')
            return True
        else:
            self.add_message("Failed to start gesture control.", 'error')
            return False
    
    def start_cv_volume_control(self):
        """Start embedded CV volume control"""
        if not CV_AVAILABLE:
            self.add_message("CV libraries not installed. Cannot start gesture control.", 'error')
            return False
        
        if self.cv_control and self.cv_control.is_active():
            self.add_message("Gesture control is already active.", 'system')
            return True
        
        self.add_message("Starting volume gesture control...", 'system')
        self.cv_control = CVControlOverlay(self.root, self._on_cv_control_closed)
        
        if self.cv_control.start('volume'):
            self.add_message("Move your hand UP/DOWN to adjust volume. Say 'OK Jarvis' or press ESC to close.", 'jarvis')
            return True
        else:
            self.add_message("Failed to start gesture control.", 'error')
            return False
    
    def stop_cv_control(self):
        """Stop the CV control overlay"""
        if self.cv_control and self.cv_control.is_active():
            self.cv_control.stop()
            self.add_message("Gesture control closed.", 'system')
    
    def _on_cv_control_closed(self):
        """Callback when CV control is closed"""
        self.cv_control = None
        self.add_message("Gesture control deactivated.", 'system')
    
    def _process_messages(self):
        """Process pending messages"""
        try:
            while True:
                text, msg_type = self.message_queue.get_nowait()
                self.conversation.add_message(text, msg_type)
        except queue.Empty:
            pass
    
    def _start_animation(self):
        """Start animation loop"""
        self._animate()
    
    def _animate(self):
        """Main animation frame"""
        if not self.running:
            return
        
        # Process messages
        self._process_messages()
        
        # Update audio level
        if self.is_speaking:
            self.audio_level = random.uniform(0.4, 0.9)
        elif self.is_listening:
            self.audio_level = random.uniform(0.1, 0.3)
        else:
            self.audio_level *= 0.9
        
        # Update visualizations
        self.arc_reactor.update(self.audio_level, self.is_active)
        self.waveform.update(self.is_speaking, self.is_listening)
        
        # Update system stats
        if PSUTIL_AVAILABLE and random.random() < 0.1:
            try:
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                self.status_bar.update(cpu=cpu, memory=mem)
                self.left_panel.update_value(self.sys_cpu, f"{cpu:.1f}%", 
                    ColorScheme.ACTIVE_GREEN if cpu < 50 else ColorScheme.WARNING_ORANGE)
                self.left_panel.update_value(self.sys_mem, f"{mem:.1f}%",
                    ColorScheme.ACTIVE_GREEN if mem < 60 else ColorScheme.WARNING_ORANGE)
            except:
                pass
        
        # Update uptime
        if hasattr(self, 'start_time'):
            uptime = datetime.now() - self.start_time
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.right_panel.update_value(self.session_uptime, f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Update status bar time
        self.status_bar.update()
        
        # Schedule next frame
        self.root.after(33, self._animate)
    
    def _on_resize(self, event):
        """Handle resize - rebuild UI elements for new size"""
        if event.widget == self.root:
            new_width = event.width
            new_height = event.height
            
            # Only rebuild if size actually changed significantly
            if abs(new_width - self.width) > 10 or abs(new_height - self.height) > 10:
                self.width = new_width
                self.height = new_height
                
                # Rebuild hex grid
                if hasattr(self, 'hex_grid'):
                    self.hex_grid.resize(self.width, self.height)
                
                # Reposition arc reactor to center
                if hasattr(self, 'arc_reactor'):
                    center_x = self.width // 2
                    center_y = self.height // 2 - 30
                    self.arc_reactor.reposition(center_x, center_y)
                
                # Reposition waveform
                if hasattr(self, 'waveform'):
                    wave_width = min(500, self.width - 200)
                    center_x = self.width // 2
                    center_y = self.height // 2 - 30
                    self.waveform.reposition(center_x - wave_width // 2, center_y + 180, wave_width)
                
                # Reposition status bar
                if hasattr(self, 'status_bar'):
                    self.status_bar.reposition(self.height - 40, self.width)
                
                # Reposition control button
                if hasattr(self, 'btn_bg'):
                    btn_width = 200
                    btn_height = 45
                    btn_x = self.width // 2 - btn_width // 2
                    btn_y = self.height - 100
                    self.canvas.coords(self.btn_bg, btn_x, btn_y, btn_x + btn_width, btn_y + btn_height)
                    self.canvas.coords(self.btn_text, self.width // 2, btn_y + btn_height // 2)
                
                # Reposition right panel
                if hasattr(self, 'right_panel'):
                    self.right_panel.reposition(self.width - 330, 120)
                
                # Reposition conversation panel
                if hasattr(self, 'conversation'):
                    self.conversation.reposition(50, self.height - 280)
    
    def _on_close(self):
        """Handle close"""
        self.running = False
        
        # Close CV control if active
        if self.cv_control and self.cv_control.is_active():
            self.cv_control.stop()
        
        if self.jarvis:
            self.jarvis.running = False
        self.root.after(100, self.root.destroy)
    
    def run(self):
        """Run the interface"""
        self.add_message("J.A.R.V.I.S Interface initialized", 'system')
        self.add_message("All systems nominal. Awaiting activation.", 'system')
        self.root.mainloop()


def main():
    """Main entry point"""
    app = JarvisInterface()
    app.run()


if __name__ == "__main__":
    main()
