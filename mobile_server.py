"""
Mobile Server for Jarvis
Enables mobile app to connect and send commands via Socket.IO
"""

from flask import Flask
from flask_socketio import SocketIO, emit
import json
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("JARVIS_MOBILE_SECRET", os.urandom(32))
MOBILE_TOKEN = os.getenv("JARVIS_MOBILE_TOKEN")
ALLOWED_ORIGINS = os.getenv("JARVIS_MOBILE_ORIGINS", "http://localhost")
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS, async_mode='threading')

# Store handlers in app config to persist across threads
app.config['JARVIS_COMMAND_HANDLER'] = None
app.config['JARVIS_VOICE_ENGINE'] = None
app.config['JARVIS_HOME_AUTOMATION'] = None


def set_handlers(cmd_handler, voice_eng):
    """Set the command handler and voice engine from main app"""
    app.config['JARVIS_COMMAND_HANDLER'] = cmd_handler
    app.config['JARVIS_VOICE_ENGINE'] = voice_eng
    logger.info(f"[Mobile] Handlers set - command_handler: {cmd_handler is not None}, voice_engine: {voice_eng is not None}")
    print(f"[Mobile] Handlers configured successfully")


def set_home_automation(ha):
    """Set home automation module for TV control"""
    app.config['JARVIS_HOME_AUTOMATION'] = ha


def _is_authorized(data):
    """Require an explicit shared token for every remote command."""
    if not MOBILE_TOKEN:
        logger.error("JARVIS_MOBILE_TOKEN is not configured; rejecting mobile request")
        return False
    auth = data.get("auth", {}) if isinstance(data, dict) else {}
    return auth.get("token") == MOBILE_TOKEN


class MobileVoiceEngine:
    """Voice engine wrapper that captures responses for mobile"""
    
    def __init__(self, original_engine):
        self.original_engine = original_engine
        self.last_response = ""
    
    def speak(self, text):
        """Capture text and optionally speak it"""
        self.last_response = text
        # Optionally also speak on desktop
        if self.original_engine:
            self.original_engine.speak(text)
    
    def listen(self):
        """Not used for mobile - returns empty"""
        return ""
    
    def get_last_response(self):
        """Get the last spoken response"""
        return self.last_response


@socketio.on('connect')
def handle_connect(auth=None):
    """Handle mobile client connection"""
    if not _is_authorized({"auth": auth or {}}):
        logger.warning("Rejected unauthorized mobile connection")
        return False
    logger.info('Mobile client connected')
    print('[Mobile] Client connected')
    emit('response', {'text': 'Connected to Jarvis. How can I assist you?'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle mobile client disconnection"""
    logger.info('Mobile client disconnected')
    print('[Mobile] Client disconnected')


@socketio.on('tv_command')
def handle_tv_command(data):
    """Handle TV remote commands from mobile app"""
    if not _is_authorized(data):
        emit('tv_response', {'status': 'unauthorized'})
        return
    home_automation = app.config.get('JARVIS_HOME_AUTOMATION')
    
    action = data.get('action', '')
    cmd_data = data.get('data', '')
    
    logger.info(f'[Mobile] TV Command: {action} - {cmd_data}')
    print(f'[Mobile] TV Command: {action} - {cmd_data}')
    
    try:
        if not home_automation:
            emit('tv_response', {'status': 'no_home_automation'})
            return
        
        # Helper function to ensure TV is connected
        def ensure_connected():
            if home_automation.is_connected:
                return True
            # Auto-connect to first available TV
            devices = home_automation.tv_config.devices  # Access the devices dict via tv_config
            print(f'[Mobile] Devices: {devices}')
            for ip, info in devices.items():
                print(f'[Mobile] Trying to connect to TV at {ip}...')
                success = home_automation.connect_tv(ip)
                if success:
                    print(f'[Mobile] Connected to TV at {ip}')
                    return True
            return False
        
        if action == 'connect':
            # Connect to TV by location
            location = cmd_data.lower() if cmd_data else 'hall'
            # Find TV by location
            devices = home_automation.tv_config.devices  # Access the devices dict via tv_config
            tv_ip = None
            for ip, info in devices.items():
                if location in info.get('location', '').lower() or location in info.get('name', '').lower():
                    tv_ip = ip
                    break
            
            if tv_ip:
                print(f'[Mobile] Connecting to TV at {tv_ip}...')
                success = home_automation.connect_tv(tv_ip)
                if success:
                    print(f'[Mobile] Successfully connected to TV')
                    emit('tv_response', {'status': 'connected'})
                else:
                    print(f'[Mobile] Failed to connect to TV')
                    emit('tv_response', {'status': 'connection_failed'})
            else:
                emit('tv_response', {'status': 'tv_not_found', 'message': f'No TV found for location: {location}'})
        
        elif action == 'key':
            # Auto-connect if not connected
            if not ensure_connected():
                emit('tv_response', {'status': 'tv_not_connected', 'message': 'Could not connect to TV'})
                return
            # Send keycode to TV
            print(f'[Mobile] Sending key: {cmd_data}')
            success = home_automation.tv_send_key(cmd_data)
            print(f'[Mobile] Key sent, success: {success}')
            emit('tv_response', {'status': 'success' if success else 'failed', 'action': action})
        
        elif action == 'launch_app':
            # Auto-connect if not connected
            if not ensure_connected():
                emit('tv_response', {'status': 'tv_not_connected', 'message': 'Could not connect to TV'})
                return
            # Launch streaming app - map package names to friendly names
            # These match the package IDs from Flutter app to home_automation.py STREAMING_APPS keys
            app_map = {
                'com.netflix.ninja': 'netflix',
                'com.amazon.avod': 'prime video',  # Changed to match STREAMING_APPS
                'com.google.android.youtube.tv': 'youtube',
                'com.hotstar.android': 'hotstar',
                'in.startv.hotstar': 'disney hotstar',
                'com.disney.disneyplus': 'disney',
                'com.graymatrix.did': 'zee5',
                'com.graymatrix.did.zee5': 'zee5',
                'com.sonyliv': 'sonyliv',
                'com.sony.liv': 'sony liv',
                'com.jio.media.ondemand': 'jiocinema',
                'tv.voot.android': 'jiocinema',
                'com.spotify.tv.android': 'spotify',
                'tv.plex.android': 'plex',
                'com.plexapp.android': 'plex',
                'org.xbmc.kodi': 'kodi'
            }
            app_name = app_map.get(cmd_data, cmd_data)  # Use friendly name or original if not in map
            print(f'[Mobile] Launching app: {cmd_data} -> {app_name}')
            success = home_automation.tv_launch_app(app_name)
            emit('tv_response', {'status': 'success' if success else 'failed', 'action': 'app_launched'})
        
        else:
            emit('tv_response', {'status': 'unknown_action'})
    except Exception as e:
        logger.error(f'[Mobile] TV Command error: {e}')
        print(f'ERROR: {e}')
        emit('tv_response', {'status': 'error', 'message': str(e)})


@socketio.on('command')
def handle_command(data):
    """Handle command from mobile app"""
    if not _is_authorized(data):
        emit('response', {'text': 'Unauthorized mobile client.'})
        return
    # Get handlers from app config
    command_handler = app.config.get('JARVIS_COMMAND_HANDLER')
    voice_engine = app.config.get('JARVIS_VOICE_ENGINE')
    home_automation = app.config.get('JARVIS_HOME_AUTOMATION')
    
    text = data.get('text', '').strip()
    logger.info(f'[Mobile] Received command: {text}')
    logger.info(f'[Mobile] command_handler available: {command_handler is not None}')
    print(f'[Mobile] Command: {text}')
    print(f'[Mobile] Handler available: {command_handler is not None}')
    
    if not text:
        emit('response', {'text': "I didn't catch that. Could you repeat?"})
        return
    
    # Check if this is a TV control command
    text_lower = text.lower()
    tv_keywords = ['control', 'open', 'show', 'remote']
    location_keywords = ['hall', 'bedroom', 'living room', 'kitchen', 'my']
    
    if 'tv' in text_lower and any(kw in text_lower for kw in tv_keywords):
        # Extract location
        location = 'Hall'  # default
        for loc in ['hall', 'bedroom', 'living room', 'kitchen']:
            if loc in text_lower:
                location = loc.title()
                break
        
        # Tell the app to open TV remote
        emit('open_tv_remote', {'location': location, 'tv_name': 'TV'})
        emit('response', {'text': f'Opening {location} TV remote control...'})
        
        # Also try to connect to the TV on the server side
        if home_automation:
            try:
                home_automation.tv_connect_async(location.lower())
            except:
                pass
        return
    
    try:
        if command_handler:
            # Create a wrapper to capture the response
            mobile_voice = MobileVoiceEngine(voice_engine)
            
            # Temporarily swap voice engine
            original_voice = command_handler.voice_engine
            command_handler.voice_engine = mobile_voice
            
            # Process the command
            result = command_handler.process_command(text)
            
            # Restore original voice engine
            command_handler.voice_engine = original_voice
            
            # Get the response
            response = mobile_voice.get_last_response()
            
            if response:
                emit('response', {'text': response})
            else:
                emit('response', {'text': 'Command executed successfully.'})
        else:
            # Fallback responses when handler not available
            emit('response', {'text': "I'm initializing. Please try again in a moment."})
            
    except Exception as e:
        logger.error(f'[Mobile] Error processing command: {e}')
        emit('response', {'text': f"I encountered an error: {str(e)}"})


@socketio.on('ping_server')
def handle_ping():
    """Handle ping to check server status"""
    emit('pong', {'status': 'online', 'version': '1.0.0'})


def run_mobile_server(host='0.0.0.0', port=5000):
    """Run the mobile server"""
    print(f'\n[Mobile Server] Starting on {host}:{port}')
    print(f'[Mobile Server] Connect your mobile app to this IP address')
    
    # Get local IP for display
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f'[Mobile Server] Your local IP: {local_ip}')
    except:
        print('[Mobile Server] Could not determine local IP')
    
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False)


def start_mobile_server_thread(cmd_handler=None, voice_eng=None, host='0.0.0.0', port=5000):
    """Start mobile server in a background thread"""
    import threading
    
    if cmd_handler and voice_eng:
        set_handlers(cmd_handler, voice_eng)
    
    server_thread = threading.Thread(
        target=run_mobile_server, 
        args=(host, port),
        daemon=True
    )
    server_thread.start()
    return server_thread


if __name__ == '__main__':
    # Standalone mode for testing
    logging.basicConfig(level=logging.INFO)
    run_mobile_server()
