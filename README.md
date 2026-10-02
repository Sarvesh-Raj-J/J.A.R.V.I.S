# J.A.R.V.I.S - Just A Rather Very Intelligent System

<div align="center">

**A Cinematic Iron Man-Inspired AI Voice Assistant with Holographic UI**

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## Overview

**J.A.R.V.I.S** is a fully-featured voice-controlled AI assistant built in Python, featuring a stunning **Iron Man-inspired holographic UI**. The interface includes a pulsating Arc Reactor, dynamic audio waveform visualization, hexagonal grid backgrounds, and real-time system monitoring â€” all designed to deliver a cinematic experience.

> **Main Entry Point:** `jarvis_futuristic_ui.py` â€” The complete Iron Man UI experience

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Holographic UI** | Arc Reactor animation, waveform visualizer, hexagonal grid, status panels |
| **Voice Recognition** | Natural language processing with wake phrase detection |
| **Text-to-Speech** | Customizable voice profiles (speed, volume, voice selection) |
| **App Control** | Open, close, and manage Windows applications by voice |
| **Spotify Integration** | Play music, control playback â€” persistent session support |
| **Gesture Controls** | Control brightness/volume using hand gestures (MediaPipe) |
| **AI Conversations** | Powered by Ollama for intelligent responses |
| **VS Code Integration** | Open projects, files, and workspaces |
| **System Control** | Battery status, shutdown, restart, lock, volume, brightness |
| **Web Search** | Google, YouTube, Wikipedia searches by voice |
| **Keyboard Shortcuts** | F key to interrupt speech, Space to toggle, ESC to exit |

---

## The Futuristic UI (`jarvis_futuristic_ui.py`)

The main interface is built with **Tkinter** and features:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—  â”‚
â”‚  â•‘                   JARVIS INTERFACE                        â•‘  â”‚
â”‚  â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£  â”‚
â”‚  â•‘   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â•‘  â”‚
â”‚  â•‘   â”‚              ARC REACTOR (Animated)             â”‚    â•‘  â”‚
â”‚  â•‘   â”‚         Pulses with voice activity              â”‚    â•‘  â”‚
â”‚  â•‘   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â•‘  â”‚
â”‚  â•‘                                                          â•‘  â”‚
â”‚  â•‘   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â•‘  â”‚
â”‚  â•‘   â”‚     âˆ¿âˆ¿âˆ¿ WAVEFORM VISUALIZER âˆ¿âˆ¿âˆ¿                â”‚    â•‘  â”‚
â”‚  â•‘   â”‚   Dynamic audio visualization                   â”‚    â•‘  â”‚
â”‚  â•‘   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â•‘  â”‚
â”‚  â•‘                                                          â•‘  â”‚
â”‚  â•‘  [STATUS] â— LISTENING    [CPU] 23%    [MEM] 45%         â•‘  â”‚
â”‚  â•‘  [BATTERY] 87%           [TIME] 14:32:05                 â•‘  â”‚
â”‚  â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•  â”‚
â”‚        â¬¡ â¬¡ â¬¡ HEXAGONAL GRID BACKGROUND â¬¡ â¬¡ â¬¡                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### UI Components:
- **`ArcReactor`** â€” Central animated reactor with rotating segments
- **`WaveformVisualizer`** â€” Real-time audio waveform display
- **`HexGrid`** â€” Animated hexagonal background pattern
- **`StatusPanel`** â€” System stats (CPU, Memory, Battery, Time)
- **`CVControlOverlay`** â€” Embedded gesture control popup

---

## Project Structure

```
Jarvis_Laptop/
â”‚
â”œâ”€â”€ jarvis_futuristic_ui.py   # MAIN ENTRY â€” Iron Man UI
â”œâ”€â”€ jarvis_main.py            # Core Jarvis logic
â”œâ”€â”€ config.example.json       # Configuration template
â”œâ”€â”€ config.example.json       # Safe public configuration template
â”œâ”€â”€ requirements.txt          # Python dependencies
â”œâ”€â”€ start_jarvis.bat          # Windows launcher
â”œâ”€â”€ start_jarvis.sh           # Linux/Mac launcher
â”œâ”€â”€ .gitignore                # Git ignore rules
â”œâ”€â”€ README.md                 # This file
â”‚
â””â”€â”€ modules/                  # Core functionality modules
    â”œâ”€â”€ __init__.py
    â”œâ”€â”€ voice_engine.py       # Voice recognition & TTS
    â”œâ”€â”€ command_handler.py    # Command processing
    â”œâ”€â”€ app_controller.py     # Application management
    â”œâ”€â”€ system_controller.py  # System operations
    â”œâ”€â”€ spotify_controller.py # Spotify automation
    â”œâ”€â”€ vscode_controller.py  # VS Code integration
    â”œâ”€â”€ ai_assistant.py       # Ollama AI integration
    â”œâ”€â”€ email_manager.py      # Email functionality
    â”œâ”€â”€ app_actions.py        # App-specific actions
    â””â”€â”€ utilities.py          # Helper functions

# External files (place in parent directory):
../hand_landmarker.task          # MediaPipe hand model
../brightness_control.py         # Brightness control script
../volume_control.py             # Volume control script
```

---

## Installation

### Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **Windows 10/11**
- **Microphone** for voice input
- **Webcam** (optional â€” for gesture controls)
- **Chrome Browser** (for Spotify)

### Step 1: Clone the repository

```bash
git clone https://github.com/Sarvesh-Raj-J/Jarvis_Laptop.git
cd Jarvis_Laptop
```

### Step 2: Create a virtual environment

```bash
# Windows (PowerShell)
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Create your local configuration

Create a local configuration from the public template:

```powershell
Copy-Item config.example.json config.json
```

Edit `config.json` to change wake phrases, voice profiles, application mappings,
and other preferences. Email credentials are supplied through environment
variables:

```powershell
$env:JARVIS_EMAIL = "you@gmail.com"
$env:JARVIS_EMAIL_PASSWORD = "your-gmail-app-password"
```

For Gmail, enable two-step verification and create an app password at
[Google App Passwords](https://myaccount.google.com/apppasswords). Use the app
password instead of your normal Gmail password.

### Spotify setup

Spotify is controlled through Chrome and Selenium. A Spotify developer account
is not required. Start Jarvis, say a play command, and sign in when the
Spotify browser window opens. The local browser profile is reused on future
runs. To choose a profile location, set:

```powershell
$env:JARVIS_SPOTIFY_PROFILE = "C:\Users\YourName\AppData\Local\Jarvis\Spotify"
```

For reference, see [`spotify.example.json`](spotify.example.json).

### Android TV setup

Run device discovery when you want to find TVs on the local network:

```powershell
python discover_devices.py
```

Copy [`tv_devices.example.json`](tv_devices.example.json) to `tv_devices.json`
if you want to edit device names or locations manually. Otherwise Jarvis
creates the local device file when you add a TV. On the first connection,
approve the pairing request shown on the TV; the required certificate is
generated automatically.

### Optional Ollama-compatible proxy

The Off Grid Ollama-compatible proxy is loopback-only by default. To use it,
set a strong token before starting it:

```powershell
$env:JARVIS_PROXY_TOKEN = "generate-a-long-random-token"
$env:PROXY_HOST = "127.0.0.1"
python offgrid_jarvis_ollama_proxy.py
```

Send the token in an `Authorization: Bearer <token>` header when making
command requests. The proxy listens on the local computer by default.

### Ollama local AI

Install [Ollama](https://ollama.com), then download a model:

```powershell
ollama pull llama3.2
```

The default endpoint is `http://localhost:11434/api/generate`. Override it
with `OLLAMA_URL` when Ollama runs on another address.

### Gesture controls

Download the `hand_landmarker.task` model from the
[MediaPipe model page](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker#models)
and place it in the parent folder beside `Jarvis_Laptop`. A webcam is required.

### Mobile and browser services

Set only the tokens for the services you want to use:

```powershell
$env:JARVIS_MOBILE_TOKEN = "your-mobile-token"
$env:JARVIS_BRIDGE_TOKEN = "your-browser-token"
```

Start them with:

```powershell
python jarvis_mobile_only.py
python browser_voice_bridge.py
```

The browser command endpoint requires `JARVIS_BRIDGE_TOKEN`. The mobile client
must send `JARVIS_MOBILE_TOKEN` as its connection authentication token.

### Step 5: Install Platform-Specific Dependencies

```bash
# Voice (PyAudio - may need special installation on Windows)
pip install pyaudio

# If PyAudio fails on Windows, try:
pip install pipwin
pipwin install pyaudio

# Gesture Controls
pip install mediapipe opencv-python pillow

# Volume Control (Windows)
pip install pycaw comtypes

# Brightness Control
pip install screen-brightness-control

# Spotify Automation
pip install selenium webdriver-manager

# Keyboard Shortcuts
pip install keyboard
```

### Step 6: Download MediaPipe Model

Download `hand_landmarker.task` from [MediaPipe Hand Landmarker](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker#models) and place it in the **parent directory** of Jarvis_Laptop.

### Step 7: (Optional) Setup Personaplex for AI

Personaplex is a speech-to-speech conversational model. To use it:

1. Clone the repo: `git clone https://github.com/NVIDIA/personaplex.git`
2. Accept the license at https://huggingface.co/nvidia/personaplex-7b-v1
3. Set HF_TOKEN in personaplex/.env
4. Run with Docker: `cd personaplex && docker-compose up --build`
5. For the web client: `cd personaplex/client && npm install && npm run dev`

The desktop UI embeds the Personaplex web client for fully conversational AI. For mobile (iOS/Android), integrate the web client as a WebView in the React Native app.

---

## Running Jarvis

### Method 1: Direct Python (recommended)

```powershell
.\.venv\Scripts\Activate.ps1
python jarvis_futuristic_ui.py
```

### Method 2: One-Liner (Windows PowerShell)

```powershell
Set-Location "C:\path\to\Jarvis_Laptop"
.\.venv\Scripts\Activate.ps1
python jarvis_futuristic_ui.py
```

### Method 3: Batch File

Double-click `start_jarvis.bat` from the repository folder. It starts the
futuristic UI and prints an error message if a dependency is missing.

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Toggle Jarvis active/standby mode |
| `F` | **Interrupt Jarvis while speaking** |
| `ESC` | Close gesture control popup / Exit app |

---

## Voice Commands

### Basic Control
| Command | Action |
|---------|--------|
| "Hey Jarvis" | Wake up (if in standby) |
| "Go to sleep" | Enter standby mode |
| "Exit" / "Quit" | Shutdown Jarvis |

### App Control
| Command | Action |
|---------|--------|
| "Open Chrome" | Launch Chrome browser |
| "Open VS Code" | Launch Visual Studio Code |
| "Open Notepad" | Launch Notepad |
| "Close Chrome" | Close Chrome application |

### Spotify Music
| Command | Action |
|---------|--------|
| "Play Shape of You" | Play song on Spotify |
| "Play Anirudh Ravichander" | Play artist on Spotify |
| "Pause music" | Pause playback |
| "Resume music" | Resume playback |
| "Next song" | Skip to next track |
| "Previous song" | Go to previous track |

### Gesture Controls
| Command | Action |
|---------|--------|
| "Control my brightness" | Open hand gesture brightness control |
| "Control my volume" | Open hand gesture volume control |

### System Control
| Command | Action |
|---------|--------|
| "Battery status" | Check battery percentage |
| "Set volume to 50" | Set system volume |
| "Increase brightness" | Increase screen brightness |
| "Shutdown computer" | Shutdown PC |
| "Restart computer" | Restart PC |
| "Lock my PC" | Lock workstation |

### Web & Search
| Command | Action |
|---------|--------|
| "Search Python tutorials" | Google search |
| "YouTube cat videos" | YouTube search |
| "Wikipedia Albert Einstein" | Wikipedia lookup |

### Information
| Command | Action |
|---------|--------|
| "What time is it?" | Current time |
| "What's the date?" | Current date |
| "What can you do?" | Show help |

### AI Conversations
Simply ask any question naturally:
- "What is machine learning?"
- "Tell me a joke"
- "Explain quantum computing"

---

## Configuration

Create `config.json` from `config.example.json` and customize it locally.
Supported environment variables:

- `JARVIS_CONFIG` â€” path to an alternative configuration file
- `JARVIS_EMAIL` and `JARVIS_EMAIL_PASSWORD` â€” Gmail sender credentials
- `OLLAMA_URL` â€” Ollama API endpoint
- `JARVIS_SPOTIFY_PROFILE` â€” Chrome profile directory for Spotify
- `JARVIS_MOBILE_TOKEN` â€” mobile Socket.IO authentication token
- `JARVIS_BRIDGE_TOKEN` â€” browser bridge bearer token
- `JARVIS_PROXY_TOKEN` â€” Ollama-compatible proxy bearer token

The template contains no account-specific values. The first launch creates
local runtime state automatically.

```json
{
    "wake_phrases": ["hey jarvis", "jarvis"],
    "sleep_commands": ["sleep", "go to sleep", "standby"],
    "voice_settings": {
        "rate": 170,
        "volume": 1.0,
        "voice_index": 0
    },
    "email": {
        "sender_email": "",
        "sender_password": "",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587
    },
    "personaplex": {
        "enabled": true,
        "voice_prompt": "NATF2.pt",
        "text_prompt": "You are a wise and friendly teacher. Answer questions or provide advice in a clear and engaging way.",
        "offline_script": "python -m moshi.offline",
        "context_aware": true,
        "max_context_messages": 10
    }
}
```

### Email Setup (Gmail)
1. Enable 2-Factor Authentication
2. Generate App Password: [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Use App Password in config (not your regular password)

---

## Troubleshooting

### PyAudio Installation Error
```
ERROR: Could not build wheels for pyaudio
```
**Fix:**
```bash
pip install pipwin
pipwin install pyaudio
```

### Microphone Not Found
```
OSError: [Errno -9996] Invalid input device
```
**Fix:** Check Windows Sound Settings â†’ Set microphone as default recording device

### Chrome Driver Issues
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```
**Fix:**
```bash
pip install webdriver-manager --upgrade
```

### MediaPipe Model Not Found
```
RuntimeError: Unable to open file at hand_landmarker.task
```
**Fix:** Download model and place in parent directory of Jarvis_Laptop

### Spotify Login Required
**Fix:** First time only â€” log in manually in the browser window that opens. Session is saved.

### Volume Not Changing
**Fix:** Ensure pycaw is installed:
```bash
pip install pycaw comtypes
```

### Keyboard Library Permission (Linux)
```
ImportError: You must be root to use this library
```
**Fix:**
```bash
sudo python jarvis_futuristic_ui.py
```

---

## Requirements

Key dependencies (see `requirements.txt` for full list):

| Package | Purpose |
|---------|---------|
| `pyttsx3` | Text-to-speech |
| `SpeechRecognition` | Voice recognition |
| `pyaudio` | Audio input |
| `mediapipe` | Hand gesture tracking |
| `opencv-python` | Computer vision |
| `pycaw` | Windows volume control |
| `screen-brightness-control` | Brightness control |
| `selenium` | Web automation (Spotify) |
| `psutil` | System monitoring |
| `keyboard` | Keyboard shortcuts |
| `requests` | HTTP requests (Ollama) |

---

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- Inspired by **Iron Man's J.A.R.V.I.S**
- [MediaPipe](https://developers.google.com/mediapipe) for hand tracking
- [Ollama](https://ollama.ai) for AI capabilities
- The amazing Python community

---

<div align="center">

**Star this repo if you find it useful!**

Made with Python

</div>
