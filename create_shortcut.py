"""
Create JARVIS icon and desktop shortcut
Run this once to set up the desktop shortcut
"""

import os
import sys

def create_icon():
    """Create a simple JARVIS icon using PIL"""
    try:
        from PIL import Image, ImageDraw
        
        # Create 256x256 icon
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        cx, cy = size // 2, size // 2
        
        # Outer glow (dark blue circle)
        r = 120
        draw.ellipse([cx-r-8, cy-r-8, cx+r+8, cy+r+8], fill=(0, 50, 70, 200))
        
        # Main ring (cyan)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(0, 168, 181, 255), width=6)
        
        # Inner ring
        r2 = 90
        draw.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], outline=(0, 100, 120, 255), width=3)
        
        # Core outer
        r3 = 50
        draw.ellipse([cx-r3, cy-r3, cx+r3, cy+r3], fill=(10, 30, 40, 255), outline=(0, 212, 255, 255), width=4)
        
        # Core inner
        r4 = 30
        draw.ellipse([cx-r4, cy-r4, cx+r4, cy+r4], fill=(0, 168, 181, 255), outline=(0, 255, 255, 255), width=2)
        
        # Center bright
        r5 = 12
        draw.ellipse([cx-r5, cy-r5, cx+r5, cy+r5], fill=(255, 255, 255, 255))
        
        # Draw triangle
        tri_r = 45
        import math
        points = []
        for i in range(3):
            angle = i * (2 * math.pi / 3) - math.pi / 2
            x = cx + tri_r * math.cos(angle)
            y = cy + tri_r * math.sin(angle)
            points.append((x, y))
        draw.polygon(points, outline=(0, 240, 255, 255), width=3)
        
        # Arc segments around the ring
        for i in range(8):
            angle_start = i * 45 + 10
            angle_end = angle_start + 25
            r_arc = 105
            # Draw arc as series of lines
            for j in range(10):
                a1 = math.radians(angle_start + j * 2.5)
                a2 = math.radians(angle_start + (j + 1) * 2.5)
                x1 = cx + r_arc * math.cos(a1)
                y1 = cy + r_arc * math.sin(a1)
                x2 = cx + r_arc * math.cos(a2)
                y2 = cy + r_arc * math.sin(a2)
                draw.line([(x1, y1), (x2, y2)], fill=(0, 240, 255, 255), width=4)
        
        # Save as ICO
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "jarvis_icon.ico")
        
        # Create multiple sizes for ICO
        img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        
        print(f"Icon created: {icon_path}")
        return icon_path
        
    except ImportError:
        print("PIL not installed. Installing...")
        os.system(f"{sys.executable} -m pip install Pillow")
        return create_icon()


def create_desktop_shortcut(icon_path):
    """Create a desktop shortcut for JARVIS"""
    try:
        import winreg
        from pathlib import Path
        
        # Get desktop path
        desktop = Path.home() / "Desktop"
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        vbs_path = os.path.join(script_dir, "Launch_Jarvis.vbs")
        
        # Create shortcut using PowerShell
        shortcut_path = str(desktop / "JARVIS.lnk")
        
        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = '"{vbs_path}"'
$Shortcut.WorkingDirectory = "{script_dir}"
$Shortcut.IconLocation = "{icon_path}"
$Shortcut.Description = "J.A.R.V.I.S - AI Voice Assistant"
$Shortcut.Save()
'''
        
        import subprocess
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"Desktop shortcut created: {shortcut_path}")
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("  JARVIS Desktop Shortcut Creator")
    print("=" * 50)
    print()
    
    # Create assets folder if needed
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Create icon
    print("[1/2] Creating JARVIS icon...")
    icon_path = create_icon()
    
    if icon_path and os.path.exists(icon_path):
        # Create shortcut
        print("[2/2] Creating desktop shortcut...")
        if create_desktop_shortcut(icon_path):
            print()
            print("=" * 50)
            print("  SUCCESS! JARVIS shortcut is now on your desktop!")
            print("  Double-click it to launch JARVIS with the")
            print("  animated Arc Reactor splash screen.")
            print("=" * 50)
        else:
            print("Failed to create shortcut.")
    else:
        print("Failed to create icon.")
    
    input("\nPress Enter to exit...")
