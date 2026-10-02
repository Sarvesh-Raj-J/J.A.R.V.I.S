"""
J.A.R.V.I.S - Advanced Holographic Interface
Cinematic Iron Man inspired AI assistant interface
Designed for maximum visual impact and professional aesthetics
"""

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


class TVRemoteOverlay:
    """Futuristic TV Remote Control Overlay embedded in Jarvis UI - Modular & Dynamic"""
    
    def __init__(self, parent, on_close_callback=None):
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.running = False
        self.overlay = None
        self.home_automation = None
        self.tv_ip = None
        self.tv_name = "TV"
        self.tv_location = ""
        self.is_connected = False
        self.connection_task = None
        self.pending_app_launch = None
        self.pending_search_query = None  # For searching within apps
        self.pending_key_code = None
        self.status_label = None
        self.title_label = None
        self.tv_selector = None
        self.available_tvs = []
    
    def _lighten_color(self, hex_color, factor=0.3):
        """Lighten a hex color for hover effect"""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return ColorScheme.CYAN_DARK
    
    def _update_title(self):
        """Update the title label with current TV info"""
        if self.title_label:
            display_name = self.tv_name or "TV"
            if self.tv_location:
                display_name = f"{self.tv_location} {display_name}"
            self.title_label.config(text=f" {display_name.upper()} REMOTE")
        
    def _create_remote_button(self, parent, text, command, width=60, height=50, 
                               bg=ColorScheme.PANEL_BG, fg=ColorScheme.CYAN_BRIGHT,
                               font_size=12, is_icon=False, bg_color=None):
        """Create a futuristic styled button. bg_color overrides bg for streaming apps."""
        actual_bg = bg_color if bg_color else bg
        btn_frame = tk.Frame(parent, bg=ColorScheme.BACKGROUND, width=width, height=height)
        btn_frame.pack_propagate(False)
        
        btn = tk.Label(
            btn_frame,
            text=text,
            bg=actual_bg,
            fg='white' if bg_color else fg,
            font=('Segoe UI Symbol' if is_icon else 'Segoe UI', font_size, 'bold'),
            cursor='hand2',
            relief='flat'
        )
        btn.pack(expand=True, fill='both', padx=2, pady=2)
        
        # Hover effects
        hover_bg = ColorScheme.CYAN_DARK if not bg_color else self._lighten_color(bg_color)
        
        def on_enter(e):
            btn.config(bg=hover_bg, fg=ColorScheme.TEXT_PRIMARY)
        
        def on_leave(e):
            btn.config(bg=actual_bg, fg='white' if bg_color else fg)
        
        def on_click(e):
            btn.config(bg=ColorScheme.CYAN_BRIGHT, fg=ColorScheme.BACKGROUND)
            self.parent.after(100, lambda: btn.config(bg=actual_bg, fg='white' if bg_color else fg))
            if command:
                command()
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', on_click)
        
        return btn_frame
    
    def _create_circular_button(self, parent, text, command, size=70, 
                                  bg=ColorScheme.CYAN_DARK, fg=ColorScheme.CYAN_GLOW):
        """Create a circular navigation button"""
        canvas = tk.Canvas(parent, width=size, height=size, 
                          bg=ColorScheme.BACKGROUND, highlightthickness=0)
        
        # Draw outer glow
        canvas.create_oval(5, 5, size-5, size-5, 
                          outline=ColorScheme.CYAN_MID, width=2)
        # Draw inner circle
        canvas.create_oval(10, 10, size-10, size-10, 
                          fill=bg, outline=ColorScheme.CYAN_BRIGHT, width=1)
        # Draw text
        text_id = canvas.create_text(size//2, size//2, text=text, 
                                     fill=fg, font=('Segoe UI Symbol', 16, 'bold'))
        
        def on_click(e):
            canvas.itemconfig(text_id, fill=ColorScheme.TEXT_PRIMARY)
            self.parent.after(100, lambda: canvas.itemconfig(text_id, fill=fg))
            if command:
                command()
        
        canvas.bind('<Button-1>', on_click)
        return canvas
    
    def _connect_tv_sync(self):
        """Sync TV connection (runs in thread)"""
        try:
            # Import here to avoid circular imports
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from modules.home_automation import HomeAutomation
            
            self.home_automation = HomeAutomation(cert_dir=os.path.dirname(os.path.abspath(__file__)))
            
            # Load available TVs from config
            self.available_tvs = self.home_automation.get_tv_list()
            
            # If no IP specified, try to get from TV name/location or use first paired TV
            if not self.tv_ip:
                if self.tv_name or self.tv_location:
                    search_term = self.tv_location or self.tv_name
                    device = self.home_automation.find_tv_by_name(search_term)
                    if device:
                        self.tv_ip = device['ip']
                        self.tv_name = device['name']
                        self.tv_location = device.get('location', '')
                
                # Still no IP? Use first available paired TV
                if not self.tv_ip and self.available_tvs:
                    for tv in self.available_tvs:
                        if tv.get('is_paired'):
                            self.tv_ip = tv['ip']
                            self.tv_name = tv['name']
                            self.tv_location = tv.get('location', '')
                            break
                    
                    # If no paired TV, just use the first one
                    if not self.tv_ip:
                        self.tv_ip = self.available_tvs[0]['ip']
                        self.tv_name = self.available_tvs[0]['name']
                        self.tv_location = self.available_tvs[0].get('location', '')
            
            # Get TV info from config if we have an IP
            if self.tv_ip:
                device = self.home_automation.tv_config.get_device(self.tv_ip)
                if device:
                    self.tv_name = device['name']
                    self.tv_location = device.get('location', '')
            
            # Update title on main thread
            self.parent.after(0, self._update_title)
            
            # Update status on main thread
            status_text = f"Connecting to {self.tv_name}..."
            self.parent.after(0, lambda: self.status_label.config(text=status_text, fg=ColorScheme.WARNING_ORANGE))
            
            # connect_tv is now sync (handles its own event loop internally)
            success = self.home_automation.connect_tv(self.tv_ip)
            
            if success:
                self.is_connected = True
                self.parent.after(0, lambda: self.status_label.config(text="● Connected", fg=ColorScheme.ACTIVE_GREEN))
                self.parent.after(0, self._enable_buttons)

                # Check if there's a pending key command (e.g., power toggle)
                if self.pending_key_code:
                    import time
                    time.sleep(0.4)
                    key_code = self.pending_key_code
                    self.parent.after(0, lambda: self._send_command(key_code))
                    self.pending_key_code = None
                
                # Check if there's a pending app to launch
                if self.pending_app_launch:
                    import time
                    time.sleep(0.5)  # Brief delay to ensure connection is stable
                    app = self.pending_app_launch
                    query = self.pending_search_query
                    self.parent.after(0, lambda: self._launch_app(app, query))
                    self.pending_app_launch = None
                    self.pending_search_query = None
                    
                # Update TV selector dropdown with available TVs
                self.parent.after(0, self._populate_tv_selector)
            else:
                self.parent.after(0, lambda: self.status_label.config(text="● Disconnected", fg=ColorScheme.ERROR_RED))
                self.is_connected = False
                
        except Exception as e:
            print(f"TV connection error: {e}")
            self.parent.after(0, lambda: self.status_label.config(text="● Connection Failed", fg=ColorScheme.ERROR_RED))
            self.is_connected = False
    
    def _populate_tv_selector(self):
        """Populate the TV selector dropdown with available TVs"""
        if not self.tv_selector or not self.home_automation:
            return
        
        # Get available TVs
        tvs = self.home_automation.get_tv_list()
        self.available_tvs = tvs
        
        # Clear existing menu
        menu = self.tv_selector['menu']
        menu.delete(0, 'end')
        
        if not tvs:
            menu.add_command(label="No TVs configured", command=lambda: None)
            return
        
        # Add each TV to dropdown
        for tv in tvs:
            display = f"{tv['name']}"
            if tv.get('location'):
                display = f"{tv['location']} - {tv['name']}"
            display += f" ({tv['ip']})"
            
            # Mark paired TVs
            if tv.get('is_paired'):
                display = "✓ " + display
            
            menu.add_command(
                label=display,
                command=lambda ip=tv['ip']: self._on_tv_selected(ip)
            )
        
        # Update current selection
        if self.tv_ip:
            device = self.home_automation.tv_config.get_device(self.tv_ip)
            if device:
                display = f"✓ {device['name']} ({self.tv_ip})"
                self.tv_selector_var.set(display)
    
    def _on_tv_selected(self, selection):
        """Handle TV selection from dropdown"""
        # Extract IP from selection if it's a display string
        if '(' in selection and ')' in selection:
            ip = selection.split('(')[-1].rstrip(')')
        else:
            ip = selection
        
        # Don't do anything if same TV selected
        if ip == self.tv_ip and self.is_connected:
            return
        
        # Switch to the selected TV
        self.switch_tv(ip)
    
    def _show_add_tv_dialog(self):
        """Show dialog to add a new TV"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New TV")
        dialog.geometry("300x200")
        dialog.configure(bg=ColorScheme.BACKGROUND)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 300) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 200) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        tk.Label(dialog, text="Add New TV", bg=ColorScheme.BACKGROUND,
                fg=ColorScheme.CYAN_BRIGHT, font=('Segoe UI', 12, 'bold')).pack(pady=10)
        
        # IP Address
        ip_frame = tk.Frame(dialog, bg=ColorScheme.BACKGROUND)
        ip_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(ip_frame, text="IP Address:", bg=ColorScheme.BACKGROUND,
                fg=ColorScheme.TEXT_DIM, font=('Segoe UI', 9), width=10, anchor='w').pack(side='left')
        ip_entry = tk.Entry(ip_frame, bg=ColorScheme.PANEL_BG, fg=ColorScheme.TEXT_PRIMARY,
                           insertbackground=ColorScheme.CYAN_BRIGHT, font=('Segoe UI', 10))
        ip_entry.pack(side='left', fill='x', expand=True)
        
        # Name
        name_frame = tk.Frame(dialog, bg=ColorScheme.BACKGROUND)
        name_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(name_frame, text="Name:", bg=ColorScheme.BACKGROUND,
                fg=ColorScheme.TEXT_DIM, font=('Segoe UI', 9), width=10, anchor='w').pack(side='left')
        name_entry = tk.Entry(name_frame, bg=ColorScheme.PANEL_BG, fg=ColorScheme.TEXT_PRIMARY,
                             insertbackground=ColorScheme.CYAN_BRIGHT, font=('Segoe UI', 10))
        name_entry.pack(side='left', fill='x', expand=True)
        
        # Location
        loc_frame = tk.Frame(dialog, bg=ColorScheme.BACKGROUND)
        loc_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(loc_frame, text="Location:", bg=ColorScheme.BACKGROUND,
                fg=ColorScheme.TEXT_DIM, font=('Segoe UI', 9), width=10, anchor='w').pack(side='left')
        loc_entry = tk.Entry(loc_frame, bg=ColorScheme.PANEL_BG, fg=ColorScheme.TEXT_PRIMARY,
                            insertbackground=ColorScheme.CYAN_BRIGHT, font=('Segoe UI', 10))
        loc_entry.pack(side='left', fill='x', expand=True)
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=ColorScheme.BACKGROUND)
        btn_frame.pack(pady=15)
        
        def add_tv():
            ip = ip_entry.get().strip()
            name = name_entry.get().strip() or "TV"
            location = loc_entry.get().strip()
            
            if not ip:
                return
            
            if self.home_automation:
                self.home_automation.add_tv(ip, name, location)
                self._populate_tv_selector()
            dialog.destroy()
        
        add_btn = tk.Button(btn_frame, text="Add TV", command=add_tv,
                           bg=ColorScheme.ACTIVE_GREEN, fg='white',
                           font=('Segoe UI', 10, 'bold'), cursor='hand2')
        add_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                              bg=ColorScheme.ERROR_RED, fg='white',
                              font=('Segoe UI', 10, 'bold'), cursor='hand2')
        cancel_btn.pack(side='left', padx=10)
    
    def _connect_tv(self):
        """Connect to TV in background thread"""
        import threading
        
        thread = threading.Thread(target=self._connect_tv_sync, daemon=True)
        thread.start()
    
    def _enable_buttons(self):
        """Enable all remote buttons after connection"""
        # Buttons are always enabled, but this can be used to change appearance
        pass
    
    def _send_command(self, key_code):
        """Send a key command to TV"""
        if not self.is_connected or not self.home_automation:
            self.status_label.config(text="● Not Connected", fg=ColorScheme.ERROR_RED)
            return
        
        try:
            self.home_automation.tv_send_key(key_code)
            # Flash status to show command sent
            self.status_label.config(text="● Command Sent", fg=ColorScheme.CYAN_GLOW)
            self.parent.after(500, lambda: self.status_label.config(
                text="● Connected", fg=ColorScheme.ACTIVE_GREEN))
        except Exception as e:
            print(f"Command error: {e}")
            self.status_label.config(text="● Error", fg=ColorScheme.ERROR_RED)
    
    def _launch_app(self, app_name, search_query=None):
        """Launch a streaming app on TV, optionally with a search query"""
        if not self.is_connected or not self.home_automation:
            self.status_label.config(text="● Not Connected", fg=ColorScheme.ERROR_RED)
            return
        
        try:
            success = self.home_automation.tv_launch_app(app_name, search_query)
            if success:
                if search_query:
                    self.status_label.config(text=f"● Playing '{search_query[:15]}...'", fg=ColorScheme.CYAN_GLOW)
                else:
                    self.status_label.config(text=f"● Opening {app_name.title()}", fg=ColorScheme.CYAN_GLOW)
                self.parent.after(1500, lambda: self.status_label.config(
                    text="● Connected", fg=ColorScheme.ACTIVE_GREEN))
            else:
                self.status_label.config(text="● App Not Found", fg=ColorScheme.WARNING_ORANGE)
                self.parent.after(1500, lambda: self.status_label.config(
                    text="● Connected", fg=ColorScheme.ACTIVE_GREEN))
        except Exception as e:
            print(f"App launch error: {e}")
            self.status_label.config(text="● Error", fg=ColorScheme.ERROR_RED)
    
    def launch_app_on_start(self, app_name, search_query=None):
        """Launch an app automatically after connection is established"""
        self.pending_app_launch = app_name
        self.pending_search_query = search_query
    
    def start(self, tv_ip=None, tv_name=None, tv_location=None, launch_app=None, search_query=None):
        """Start the TV remote overlay
        
        Args:
            tv_ip: IP address of the TV (optional if name/location provided)
            tv_name: Name of the TV to connect to
            tv_location: Location of the TV (e.g., 'hall', 'bedroom')
            launch_app: App to launch immediately after connection (netflix, prime, etc.)
            search_query: Optional search query for the app
        """
        if tv_ip:
            self.tv_ip = tv_ip
        
        if tv_name:
            self.tv_name = tv_name
            
        if tv_location:
            self.tv_location = tv_location
        
        if launch_app:
            self.pending_app_launch = launch_app
            self.pending_search_query = search_query
        
        self.running = True
        self._create_overlay()
        self._connect_tv()
        return True

    def send_key_on_connect(self, key_code: str):
        """Queue a key command to send once TV is connected"""
        self.pending_key_code = key_code
    
    def switch_tv(self, tv_ip: str):
        """Switch to a different TV"""
        if self.is_connected and self.home_automation:
            self.home_automation.disconnect_tv()
            self.is_connected = False
        
        self.tv_ip = tv_ip
        device = None
        if self.home_automation:
            device = self.home_automation.tv_config.get_device(tv_ip)
        
        if device:
            self.tv_name = device['name']
            self.tv_location = device.get('location', '')
        else:
            self.tv_name = tv_ip
            self.tv_location = ''
        
        self._update_title()
        self._connect_tv()
    
    def _create_overlay(self):
        """Create the futuristic TV remote UI"""
        # Main overlay frame
        self.overlay = tk.Frame(
            self.parent,
            bg=ColorScheme.BACKGROUND,
            highlightbackground=ColorScheme.CYAN_BRIGHT,
            highlightthickness=2
        )
        
        # Position: center-right of screen
        overlay_width = 320
        overlay_height = 750  # Increased height for TV selector + streaming apps
        x_pos = self.parent.winfo_width() - overlay_width - 50
        y_pos = (self.parent.winfo_height() - overlay_height) // 2
        
        self.overlay.place(x=x_pos, y=y_pos, width=overlay_width, height=overlay_height)
        
        # === HEADER ===
        header = tk.Frame(self.overlay, bg=ColorScheme.PANEL_BG, height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # TV icon and title
        title_frame = tk.Frame(header, bg=ColorScheme.PANEL_BG)
        title_frame.pack(side='left', padx=15, pady=10)
        
        tk.Label(title_frame, text="📺", bg=ColorScheme.PANEL_BG, 
                fg=ColorScheme.CYAN_BRIGHT, font=('Segoe UI Symbol', 16)).pack(side='left')
        
        # Dynamic title - will be updated when connected
        display_name = self.tv_name or "TV"
        if self.tv_location:
            display_name = f"{self.tv_location} {display_name}"
        
        self.title_label = tk.Label(
            title_frame, text=f" {display_name.upper()} REMOTE", 
            bg=ColorScheme.PANEL_BG, fg=ColorScheme.CYAN_BRIGHT, 
            font=('Segoe UI', 11, 'bold')
        )
        self.title_label.pack(side='left')
        
        # Close button
        close_btn = tk.Label(
            header, text="✕", bg=ColorScheme.PANEL_BG, fg=ColorScheme.ERROR_RED,
            font=('Segoe UI', 14, 'bold'), cursor='hand2'
        )
        close_btn.pack(side='right', padx=15)
        close_btn.bind('<Button-1>', lambda e: self.stop())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg='#ff6677'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg=ColorScheme.ERROR_RED))
        
        # Separator with glow effect
        sep_frame = tk.Frame(self.overlay, bg=ColorScheme.BACKGROUND, height=3)
        sep_frame.pack(fill='x')
        tk.Frame(sep_frame, bg=ColorScheme.CYAN_DARK, height=1).pack(fill='x')
        tk.Frame(sep_frame, bg=ColorScheme.CYAN_BRIGHT, height=1).pack(fill='x')
        tk.Frame(sep_frame, bg=ColorScheme.CYAN_DARK, height=1).pack(fill='x')
        
        # === TV SELECTOR ===
        selector_frame = tk.Frame(self.overlay, bg=ColorScheme.BACKGROUND)
        selector_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(selector_frame, text="Select TV:", bg=ColorScheme.BACKGROUND,
                fg=ColorScheme.TEXT_DIM, font=('Segoe UI', 9)).pack(side='left', padx=5)
        
        # Create TV selector dropdown (will be populated after connection)
        self.tv_selector_var = tk.StringVar(value=self.tv_ip or "Connecting...")
        self.tv_selector = tk.OptionMenu(
            selector_frame, self.tv_selector_var, "Loading...",
            command=self._on_tv_selected
        )
        self.tv_selector.config(
            bg=ColorScheme.PANEL_BG, fg=ColorScheme.CYAN_BRIGHT,
            activebackground=ColorScheme.CYAN_DARK, activeforeground=ColorScheme.TEXT_PRIMARY,
            highlightthickness=0, font=('Segoe UI', 9), width=20
        )
        self.tv_selector['menu'].config(
            bg=ColorScheme.PANEL_BG, fg=ColorScheme.CYAN_BRIGHT,
            activebackground=ColorScheme.CYAN_DARK, activeforeground=ColorScheme.TEXT_PRIMARY
        )
        self.tv_selector.pack(side='left', padx=5)
        
        # Add new TV button
        add_tv_btn = tk.Label(
            selector_frame, text="➕", bg=ColorScheme.BACKGROUND,
            fg=ColorScheme.ACTIVE_GREEN, font=('Segoe UI Symbol', 12), cursor='hand2'
        )
        add_tv_btn.pack(side='right', padx=5)
        add_tv_btn.bind('<Button-1>', lambda e: self._show_add_tv_dialog())
        add_tv_btn.bind('<Enter>', lambda e: add_tv_btn.config(fg='#66ff66'))
        add_tv_btn.bind('<Leave>', lambda e: add_tv_btn.config(fg=ColorScheme.ACTIVE_GREEN))
        
        # === STATUS BAR ===
        status_frame = tk.Frame(self.overlay, bg=ColorScheme.PANEL_BG, height=35)
        status_frame.pack(fill='x', padx=10, pady=(10, 5))
        status_frame.pack_propagate(False)
        
        tk.Label(status_frame, text=f"IP: {self.tv_ip}", bg=ColorScheme.PANEL_BG,
                fg=ColorScheme.TEXT_DIM, font=('Consolas', 9)).pack(side='left', padx=10)
        
        self.status_label = tk.Label(status_frame, text="● Connecting...", 
                                     bg=ColorScheme.PANEL_BG, fg=ColorScheme.WARNING_ORANGE,
                                     font=('Segoe UI', 9, 'bold'))
        self.status_label.pack(side='right', padx=10)
        
        # === POWER ROW ===
        power_frame = tk.Frame(self.overlay, bg=ColorScheme.BACKGROUND)
        power_frame.pack(pady=10)
        
        self._create_remote_button(
            power_frame, "⏻", lambda: self._send_command("KEYCODE_POWER"),
            width=80, height=45, bg='#330000', fg=ColorScheme.ERROR_RED, 
            font_size=18, is_icon=True
        ).pack(side='left', padx=5)
        
        self._create_remote_button(
            power_frame, "🏠", lambda: self._send_command("KEYCODE_HOME"),
            width=80, height=45, font_size=16, is_icon=True
        ).pack(side='left', padx=5)
        
        self._create_remote_button(
            power_frame, "⬅", lambda: self._send_command("KEYCODE_BACK"),
            width=80, height=45, font_size=16, is_icon=True
        ).pack(side='left', padx=5)
        
        # === NAVIGATION D-PAD ===
        nav_frame = tk.Frame(self.overlay, bg=ColorScheme.BACKGROUND)
        nav_frame.pack(pady=15)
        
        # Create a canvas for the D-pad
        dpad_size = 200
        dpad_canvas = tk.Canvas(nav_frame, width=dpad_size, height=dpad_size,
                                bg=ColorScheme.BACKGROUND, highlightthickness=0)
        dpad_canvas.pack()
        
        cx, cy = dpad_size // 2, dpad_size // 2
        
        # Outer ring
        dpad_canvas.create_oval(10, 10, dpad_size-10, dpad_size-10,
                               outline=ColorScheme.CYAN_DARK, width=2)
        
        # UP button
        up_btn = dpad_canvas.create_polygon(
            cx, 25, cx-25, 65, cx+25, 65,
            fill=ColorScheme.PANEL_BG, outline=ColorScheme.CYAN_MID, width=1
        )
        dpad_canvas.create_text(cx, 45, text="▲", fill=ColorScheme.CYAN_BRIGHT,
                               font=('Segoe UI Symbol', 14))
        
        # DOWN button
        down_btn = dpad_canvas.create_polygon(
            cx, dpad_size-25, cx-25, dpad_size-65, cx+25, dpad_size-65,
            fill=ColorScheme.PANEL_BG, outline=ColorScheme.CYAN_MID, width=1
        )
        dpad_canvas.create_text(cx, dpad_size-45, text="▼", fill=ColorScheme.CYAN_BRIGHT,
                               font=('Segoe UI Symbol', 14))
        
        # LEFT button
        left_btn = dpad_canvas.create_polygon(
            25, cy, 65, cy-25, 65, cy+25,
            fill=ColorScheme.PANEL_BG, outline=ColorScheme.CYAN_MID, width=1
        )
        dpad_canvas.create_text(45, cy, text="◀", fill=ColorScheme.CYAN_BRIGHT,
                               font=('Segoe UI Symbol', 14))
        
        # RIGHT button  
        right_btn = dpad_canvas.create_polygon(
            dpad_size-25, cy, dpad_size-65, cy-25, dpad_size-65, cy+25,
            fill=ColorScheme.PANEL_BG, outline=ColorScheme.CYAN_MID, width=1
        )
        dpad_canvas.create_text(dpad_size-45, cy, text="▶", fill=ColorScheme.CYAN_BRIGHT,
                               font=('Segoe UI Symbol', 14))
        
        # CENTER OK button
        ok_btn = dpad_canvas.create_oval(cx-30, cy-30, cx+30, cy+30,
                                         fill=ColorScheme.CYAN_DARK, 
                                         outline=ColorScheme.CYAN_BRIGHT, width=2)
        ok_text = dpad_canvas.create_text(cx, cy, text="OK", fill=ColorScheme.CYAN_GLOW,
                                          font=('Segoe UI', 12, 'bold'))
        
        # Bind D-pad clicks
        def dpad_click(event):
            x, y = event.x, event.y
            # Determine which button was clicked based on position
            if abs(x - cx) < 30 and abs(y - cy) < 30:
                self._send_command("KEYCODE_DPAD_CENTER")
            elif y < cy - 30 and abs(x - cx) < 40:
                self._send_command("KEYCODE_DPAD_UP")
            elif y > cy + 30 and abs(x - cx) < 40:
                self._send_command("KEYCODE_DPAD_DOWN")
            elif x < cx - 30 and abs(y - cy) < 40:
                self._send_command("KEYCODE_DPAD_LEFT")
            elif x > cx + 30 and abs(y - cy) < 40:
                self._send_command("KEYCODE_DPAD_RIGHT")
        
        dpad_canvas.bind('<Button-1>', dpad_click)
        
        # === VOLUME & MEDIA CONTROLS ===
        controls_frame = tk.Frame(self.overlay, bg=ColorScheme.BACKGROUND)
        controls_frame.pack(pady=10)
        
        # Volume column
        vol_frame = tk.Frame(controls_frame, bg=ColorScheme.BACKGROUND)
        vol_frame.pack(side='left', padx=15)
        
        tk.Label(vol_frame, text="VOLUME", bg=ColorScheme.BACKGROUND,
                fg=ColorScheme.TEXT_DIM, font=('Segoe UI', 8)).pack()
        
        self._create_remote_button(
            vol_frame, "🔊+", lambda: self._send_command("KEYCODE_VOLUME_UP"),
            width=70, height=40, font_size=11
        ).pack(pady=2)
        
        self._create_remote_button(
            vol_frame, "🔇", lambda: self._send_command("KEYCODE_VOLUME_MUTE"),
            width=70, height=35, font_size=10
        ).pack(pady=2)
        
        self._create_remote_button(
            vol_frame, "🔉-", lambda: self._send_command("KEYCODE_VOLUME_DOWN"),
            width=70, height=40, font_size=11
        ).pack(pady=2)
        
        # Media column
        media_frame = tk.Frame(controls_frame, bg=ColorScheme.BACKGROUND)
        media_frame.pack(side='right', padx=15)
        
        tk.Label(media_frame, text="MEDIA", bg=ColorScheme.BACKGROUND,
                fg=ColorScheme.TEXT_DIM, font=('Segoe UI', 8)).pack()
        
        self._create_remote_button(
            media_frame, "⏮", lambda: self._send_command("KEYCODE_MEDIA_PREVIOUS"),
            width=70, height=40, font_size=14, is_icon=True
        ).pack(pady=2)
        
        self._create_remote_button(
            media_frame, "⏯", lambda: self._send_command("KEYCODE_MEDIA_PLAY_PAUSE"),
            width=70, height=35, font_size=14, is_icon=True
        ).pack(pady=2)
        
        self._create_remote_button(
            media_frame, "⏭", lambda: self._send_command("KEYCODE_MEDIA_NEXT"),
            width=70, height=40, font_size=14, is_icon=True
        ).pack(pady=2)
        
        # === STREAMING APPS ===
        apps_frame = tk.Frame(self.overlay, bg=ColorScheme.BACKGROUND)
        apps_frame.pack(pady=8)
        
        tk.Label(apps_frame, text="─── STREAMING APPS ───", bg=ColorScheme.BACKGROUND,
                fg=ColorScheme.TEXT_DIM, font=('Segoe UI', 8)).pack(pady=(0, 5))
        
        # Row 1: Netflix, Prime, YouTube
        apps_row1 = tk.Frame(apps_frame, bg=ColorScheme.BACKGROUND)
        apps_row1.pack(pady=2)
        
        self._create_remote_button(
            apps_row1, "Netflix", lambda: self._launch_app("netflix"),
            width=90, height=35, font_size=9, bg_color='#E50914'
        ).pack(side='left', padx=3)
        
        self._create_remote_button(
            apps_row1, "Prime", lambda: self._launch_app("prime"),
            width=90, height=35, font_size=9, bg_color='#00A8E1'
        ).pack(side='left', padx=3)
        
        self._create_remote_button(
            apps_row1, "YouTube", lambda: self._launch_app("youtube"),
            width=90, height=35, font_size=9, bg_color='#FF0000'
        ).pack(side='left', padx=3)
        
        # Row 2: Hotstar, ZEE5, SonyLIV
        apps_row2 = tk.Frame(apps_frame, bg=ColorScheme.BACKGROUND)
        apps_row2.pack(pady=2)
        
        self._create_remote_button(
            apps_row2, "Hotstar", lambda: self._launch_app("hotstar"),
            width=90, height=35, font_size=9, bg_color='#1F80E0'
        ).pack(side='left', padx=3)
        
        self._create_remote_button(
            apps_row2, "ZEE5", lambda: self._launch_app("zee5"),
            width=90, height=35, font_size=9, bg_color='#8B5CF6'
        ).pack(side='left', padx=3)
        
        self._create_remote_button(
            apps_row2, "SonyLIV", lambda: self._launch_app("sonyliv"),
            width=90, height=35, font_size=9, bg_color='#1A1A2E'
        ).pack(side='left', padx=3)
        
        # Row 3: JioCinema, Spotify, Settings
        apps_row3 = tk.Frame(apps_frame, bg=ColorScheme.BACKGROUND)
        apps_row3.pack(pady=2)
        
        self._create_remote_button(
            apps_row3, "JioCinema", lambda: self._launch_app("jiocinema"),
            width=90, height=35, font_size=9, bg_color='#E91E63'
        ).pack(side='left', padx=3)
        
        self._create_remote_button(
            apps_row3, "Spotify", lambda: self._launch_app("spotify"),
            width=90, height=35, font_size=9, bg_color='#1DB954'
        ).pack(side='left', padx=3)
        
        self._create_remote_button(
            apps_row3, "Settings", lambda: self._send_command("KEYCODE_SETTINGS"),
            width=90, height=35, font_size=9
        ).pack(side='left', padx=3)
        
        # === FOOTER ===
        footer = tk.Frame(self.overlay, bg=ColorScheme.PANEL_BG, height=40)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        
        tk.Label(footer, text='Say "close remote" or press ESC', bg=ColorScheme.PANEL_BG,
                fg=ColorScheme.TEXT_DIM, font=('Segoe UI', 8, 'italic')).pack(pady=10)
    
    def stop(self):
        """Stop the TV remote overlay"""
        self.running = False
        
        # Disconnect from TV
        if self.home_automation:
            try:
                self.home_automation.disconnect_tv()
            except:
                pass
            self.home_automation = None
        
        # Destroy overlay
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
        
        # Callback
        if self.on_close_callback:
            self.on_close_callback()
    
    def is_active(self):
        """Check if remote overlay is active"""
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
        
        # TV Remote overlay
        self.tv_remote = None
        
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
        """Handle escape key - close overlays or exit"""
        if self.cv_control and self.cv_control.is_active():
            self.cv_control.stop()
            self.add_message("Hand gesture control closed.", 'system')
        elif self.tv_remote and self.tv_remote.is_active():
            self.tv_remote.stop()
            self.add_message("TV remote closed.", 'system')
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
            'small': tkfont.Font(family='Segoe UI', size=8),
            'header': tkfont.Font(family='Segoe UI', size=12, weight='bold')
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
                    
                    query_lower = query.lower()
                    
                    # Check if CV control is active and user says "ok jarvis" to close it
                    if self.cv_control and self.cv_control.is_active():
                        if any(phrase in query_lower for phrase in ['ok jarvis', 'okay jarvis', 'fine jarvis', 'stop', 'close', 'done']):
                            self.root.after(0, self.stop_cv_control)
                            self.jarvis.voice_engine.speak("Gesture control closed.")
                            continue
                    
                    # Check if TV remote is active and user wants to close it
                    if self.tv_remote and self.tv_remote.is_active():
                        if any(phrase in query_lower for phrase in ['close remote', 'close tv', 'ok jarvis', 'done', 'stop']):
                            self.root.after(0, self.stop_tv_remote)
                            self.jarvis.voice_engine.speak("TV remote closed.")
                            continue
                    
                    # Check for streaming app commands on TV
                    streaming_apps = {
                        'netflix': ['netflix', 'net flix'],
                        'prime': ['prime', 'amazon prime', 'prime video'],
                        'youtube': ['youtube', 'you tube'],
                        'hotstar': ['hotstar', 'hot star', 'disney', 'disney plus', 'disney+'],
                        'zee5': ['zee5', 'zee 5', 'zee'],
                        'sonyliv': ['sony liv', 'sonyliv', 'sony live', 'sony'],
                        'jiocinema': ['jio cinema', 'jiocinema', 'jio'],
                        'spotify': ['spotify']
                    }
                    
                    # TV location keywords for dynamic selection
                    tv_locations = {
                        'hall': ['hall', 'living room', 'living', 'main'],
                        'bedroom': ['bedroom', 'bed room', 'master bedroom'],
                        'kitchen': ['kitchen'],
                        'guest': ['guest', 'guest room'],
                    }
                    
                    # Detect which TV location is mentioned
                    detected_location = None
                    for loc, keywords in tv_locations.items():
                        if any(kw in query_lower for kw in keywords):
                            detected_location = loc
                            break
                    
                    # Function to extract search query from command
                    def extract_search_query(query_text, app_keywords):
                        """Extract what to search for from the voice command"""
                        q = query_text.lower()
                        search_query = None
                        
                        # Remove common phrases
                        for phrase in ['play', 'open', 'launch', 'start', 'watch', 'search', 'find', 
                                      'on my tv', 'on tv', 'on the tv', 'on my hall tv', 'on hall tv',
                                      'on my bedroom tv', 'on bedroom tv', 'in my tv', 'in tv',
                                      'on television', 'on my television']:
                            q = q.replace(phrase, ' ')
                        
                        # Remove app name keywords
                        for kw in app_keywords:
                            q = q.replace(kw, ' ')
                        
                        # Remove location keywords
                        for loc_kws in tv_locations.values():
                            for kw in loc_kws:
                                q = q.replace(kw, ' ')
                        
                        # Clean up
                        search_query = ' '.join(q.split()).strip()
                        
                        # Return None if query is too short or just noise
                        if len(search_query) < 3:
                            return None
                        return search_query
                    
                    # Check for direct TV power commands
                    tv_context = any(word in query_lower for word in ['tv', 'television'] + list(tv_locations.keys()))

                    if any(phrase in query_lower for phrase in [
                        'turn on tv', 'turn on the tv', 'switch on tv', 'power on tv',
                        'turn off tv', 'turn off the tv', 'switch off tv', 'power off tv',
                        'toggle tv power', 'tv power'
                    ]) and tv_context:
                        self.root.after(0, lambda loc=detected_location:
                            self.start_tv_remote(tv_location=loc or "hall"))
                        self.root.after(300, lambda:
                            self.tv_remote and self.tv_remote.send_key_on_connect("KEYCODE_POWER"))
                        loc_name = detected_location.title() if detected_location else "Hall"
                        self.jarvis.voice_engine.speak(f"Power command sent to your {loc_name} TV.")
                        continue

                    # Check if user wants to play/open an app on TV
                    if any(phrase in query_lower for phrase in ['play', 'open', 'launch', 'start', 'watch']) and \
                       any(word in query_lower for word in ['tv', 'television'] + list(tv_locations.keys())):
                        for app_name, keywords in streaming_apps.items():
                            if any(kw in query_lower for kw in keywords):
                                # Extract search query (e.g., "cat videos" from "play cat videos on youtube on my tv")
                                search_query = extract_search_query(query, keywords)
                                
                                self.root.after(0, lambda app=app_name, loc=detected_location, sq=search_query: 
                                    self.start_tv_remote(tv_location=loc or "hall", launch_app=app, search_query=sq))
                                
                                loc_name = detected_location.title() if detected_location else "Hall"
                                if search_query:
                                    self.jarvis.voice_engine.speak(f"Playing {search_query} on {app_name.title()} on your {loc_name} TV.")
                                else:
                                    self.jarvis.voice_engine.speak(f"Opening {app_name.title()} on your {loc_name} TV.")
                                break
                        else:
                            # No specific app mentioned, just open the remote
                            self.root.after(0, lambda loc=detected_location: 
                                self.start_tv_remote(tv_location=loc or "hall"))
                            self.jarvis.voice_engine.speak("Opening TV remote control.")
                        continue
                    
                    # Check for TV control command (just the remote without app)
                    remote_phrases = [
                        'tv', 'television', 'tv remote', 'remote',
                        'control tv', 'control the tv', 'control my tv', 'control',
                        'open tv', 'open remote', 'open tv remote'
                    ]
                    if any(phrase in query_lower for phrase in remote_phrases):
                        if tv_context:
                            self.root.after(0, lambda loc=detected_location:
                                self.start_tv_remote(tv_location=loc or "hall"))
                            loc_name = detected_location.title() if detected_location else "Hall"
                            self.jarvis.voice_engine.speak(f"Opening TV remote control for your {loc_name} TV.")
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
    
    def start_tv_remote(self, tv_ip=None, tv_name=None, tv_location=None, launch_app=None, search_query=None):
        """Start embedded TV remote control
        
        Args:
            tv_ip: IP address of the TV (optional if name/location provided)
            tv_name: Name of the TV to connect to
            tv_location: Location of the TV (e.g., 'hall', 'bedroom')
            launch_app: Optional app to launch (netflix, prime, youtube, etc.)
            search_query: Optional search query for the app (e.g., "stranger things")
        """
        if self.tv_remote and self.tv_remote.is_active():
            # Remote already open, check if different TV requested
            if tv_ip and tv_ip != self.tv_remote.tv_ip:
                # Switch to different TV
                self.tv_remote.switch_tv(tv_ip)
                self.add_message(f"Switching to TV at {tv_ip}.", 'system')
            elif tv_location and tv_location.lower() != (self.tv_remote.tv_location or '').lower():
                # Try to find TV by location
                if self.tv_remote.home_automation:
                    device = self.tv_remote.home_automation.find_tv_by_name(tv_location)
                    if device:
                        self.tv_remote.switch_tv(device['ip'])
                        self.add_message(f"Switching to {tv_location.title()} TV.", 'system')
            
            # Launch the app if specified
            if launch_app and self.tv_remote.is_connected:
                self.tv_remote._launch_app(launch_app, search_query)
                if search_query:
                    self.add_message(f"Playing '{search_query}' on {launch_app.title()}.", 'system')
                else:
                    self.add_message(f"Launching {launch_app.title()} on TV.", 'system')
            elif not launch_app:
                self.add_message("TV remote is already open.", 'system')
            return True
        
        # Build display message
        loc_display = tv_location.title() if tv_location else (tv_name or "")
        app_msg = f" and launching {launch_app.title()}" if launch_app else ""
        search_msg = f" (searching: {search_query})" if search_query else ""
        self.add_message(f"Opening {loc_display} TV remote control{app_msg}{search_msg}...", 'system')
        
        self.tv_remote = TVRemoteOverlay(self.root, self._on_tv_remote_closed)
        
        if self.tv_remote.start(tv_ip=tv_ip, tv_name=tv_name, tv_location=tv_location, 
                                launch_app=launch_app, search_query=search_query):
            self.add_message("TV remote ready. Use the on-screen controls or voice commands.", 'jarvis')
            return True
        else:
            self.add_message("Failed to open TV remote.", 'error')
            return False
    
    def stop_tv_remote(self):
        """Stop the TV remote overlay"""
        if self.tv_remote and self.tv_remote.is_active():
            self.tv_remote.stop()
            self.add_message("TV remote closed.", 'system')
    
    def _on_tv_remote_closed(self):
        """Callback when TV remote is closed"""
        self.tv_remote = None
        self.add_message("TV remote deactivated.", 'system')
    
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
        
        # Close TV remote if active
        if self.tv_remote and self.tv_remote.is_active():
            self.tv_remote.stop()
        
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
