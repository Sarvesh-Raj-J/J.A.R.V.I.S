# J.A.R.V.I.S

J.A.R.V.I.S is a Python voice assistant for Windows with a futuristic Tkinter
interface, desktop automation, Spotify control, Android TV control, gesture
controls, and optional local AI through Ollama.

## Features

- Futuristic Tkinter interface with system status panels
- Speech recognition and text-to-speech
- Windows application and system controls
- Spotify playback through Chrome and Selenium
- Android TV discovery, pairing, and remote control
- Optional MediaPipe gesture controls
- Optional Ollama-powered conversations
- Optional mobile, browser, and Ollama-compatible proxy services

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- Microphone and speakers
- Chrome for Spotify
- Webcam for gesture controls
- Ollama for local AI conversations

## Installation

### 1. Clone and install

```powershell
git clone https://github.com/Sarvesh-Raj-J/J.A.R.V.I.S.git
Set-Location J.A.R.V.I.S
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 2. Create local configuration

```powershell
Copy-Item config.example.json config.json
```

Edit `config.json` for wake phrases, voice profiles, and application mappings.
The first run creates local runtime files automatically.

### 3. Configure Gmail email

Email is optional. Enable two-step verification, create a Gmail app password,
and set these variables before starting Jarvis:

```powershell
$env:JARVIS_EMAIL = "you@gmail.com"
$env:JARVIS_EMAIL_PASSWORD = "your-gmail-app-password"
```

Use a Gmail app password rather than your normal account password.

### 4. Start Jarvis

```powershell
python jarvis_futuristic_ui.py
```

For console mode:

```powershell
python jarvis_main.py
```

You can also double-click `start_jarvis.bat`.

## Optional setup

### Spotify

Spotify is controlled through Chrome; a Spotify developer account is not
required.

1. Install Chrome and have a Spotify account.
2. Start Jarvis and say, for example, `Play Shape of You`.
3. Sign in when the Spotify browser window opens.
4. The browser profile is reused on future runs.

To choose a different profile directory:

```powershell
$env:JARVIS_SPOTIFY_PROFILE = "C:\Users\YourName\AppData\Local\Jarvis\Spotify"
```

See `spotify.example.json` for the optional setting.

### Android TV

Discover devices on the local network:

```powershell
python discover_devices.py
```

Copy `tv_devices.example.json` to `tv_devices.json` if you want to edit device
names or locations manually. On first connection, approve the pairing request
shown on the TV. Jarvis generates the required local certificate automatically.

### Ollama

Install [Ollama](https://ollama.com), then download a model:

```powershell
ollama pull llama3.2
```

The default endpoint is `http://localhost:11434/api/generate`. Override it with:

```powershell
$env:OLLAMA_URL = "http://localhost:11434/api/generate"
```

### Gesture controls

Download `hand_landmarker.task` from the
[MediaPipe model page](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker#models)
and place it in the parent folder beside `J.A.R.V.I.S`. A webcam is required.

### Mobile and browser services

Set authentication tokens for the services you use:

```powershell
$env:JARVIS_MOBILE_TOKEN = "your-mobile-token"
$env:JARVIS_BRIDGE_TOKEN = "your-browser-token"
```

Start them separately:

```powershell
python jarvis_mobile_only.py
python browser_voice_bridge.py
```

The mobile client sends `JARVIS_MOBILE_TOKEN` during connection. Browser command
requests use `Authorization: Bearer <JARVIS_BRIDGE_TOKEN>`.

### Ollama-compatible proxy

```powershell
$env:JARVIS_PROXY_TOKEN = "your-proxy-token"
python offgrid_jarvis_ollama_proxy.py
```

Use `Authorization: Bearer <JARVIS_PROXY_TOKEN>` for command requests. The
proxy listens on the local computer by default.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| Space | Toggle active or standby mode |
| F | Interrupt speech |
| ESC | Exit Jarvis or close a control popup |

## Example voice commands

- `Hey Jarvis`
- `Open Chrome`
- `Play Shape of You`
- `Pause music`
- `Control my brightness`
- `Battery status`
- `Set volume to 50`
- `Search Python tutorials`
- `What time is it?`
- `Go to sleep`

## Configuration variables

| Variable | Purpose |
| --- | --- |
| `JARVIS_CONFIG` | Alternative configuration file |
| `JARVIS_EMAIL` | Gmail sender address |
| `JARVIS_EMAIL_PASSWORD` | Gmail app password |
| `OLLAMA_URL` | Ollama API endpoint |
| `JARVIS_SPOTIFY_PROFILE` | Spotify Chrome profile directory |
| `JARVIS_MOBILE_TOKEN` | Mobile service token |
| `JARVIS_BRIDGE_TOKEN` | Browser bridge token |
| `JARVIS_PROXY_TOKEN` | Ollama proxy token |

## Troubleshooting

### PyAudio installation fails

```powershell
pip install pipwin
pipwin install pyaudio
```

### Microphone is not found

Check Windows Sound Settings and select the correct default recording device.

### Chrome driver fails

```powershell
pip install --upgrade selenium webdriver-manager
```

### Spotify asks for login

Sign in in the Chrome window opened by Jarvis, then try the command again.

### Gesture model is missing

Confirm that `hand_landmarker.task` is in the parent folder beside the project.

## Project structure

```text
J.A.R.V.I.S/
|-- jarvis_futuristic_ui.py
|-- jarvis_main.py
|-- config.example.json
|-- requirements.txt
|-- spotify.example.json
|-- tv_devices.example.json
`-- modules/
    |-- voice_engine.py
    |-- command_handler.py
    |-- spotify_controller.py
    |-- ai_assistant.py
    `-- utilities.py
```

## License

This project is provided under the MIT License.
