"""
Home Automation Module for Jarvis
Supports Android TV Remote control using androidtvremote2
"""

import asyncio
import json
import logging
import os
import threading
import time
from typing import Optional, Dict, List
from androidtvremote2 import AndroidTVRemote
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime

logger = logging.getLogger(__name__)


class TVConfig:
    """Manages TV configurations and paired devices"""
    
    def __init__(self, config_dir: str = "."):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "tv_devices.json")
        self.devices: Dict[str, dict] = {}
        self._load_config()
    
    def _load_config(self):
        """Load TV configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.devices = data.get('devices', {})
                    logger.info(f"Loaded {len(self.devices)} TV device(s) from config")
            except Exception as e:
                logger.error(f"Failed to load TV config: {e}")
                self.devices = {}
        else:
            self.devices = {}
    
    def _save_config(self):
        """Save TV configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'devices': self.devices}, f, indent=2)
            logger.info(f"Saved {len(self.devices)} TV device(s) to config")
        except Exception as e:
            logger.error(f"Failed to save TV config: {e}")
    
    def add_device(self, ip: str, name: str, location: str = "", is_paired: bool = False):
        """Add or update a TV device"""
        self.devices[ip] = {
            'name': name,
            'location': location,
            'ip': ip,
            'is_paired': is_paired,
            'last_connected': None
        }
        self._save_config()
        logger.info(f"Added/updated TV: {name} at {ip}")
    
    def mark_paired(self, ip: str):
        """Mark a device as paired"""
        if ip in self.devices:
            self.devices[ip]['is_paired'] = True
            self.devices[ip]['last_connected'] = datetime.datetime.now().isoformat()
            self._save_config()
    
    def update_last_connected(self, ip: str):
        """Update last connected timestamp"""
        if ip in self.devices:
            self.devices[ip]['last_connected'] = datetime.datetime.now().isoformat()
            self._save_config()
    
    def get_device(self, ip: str) -> Optional[dict]:
        """Get device info by IP"""
        return self.devices.get(ip)
    
    def get_device_by_name(self, name: str) -> Optional[dict]:
        """Get device info by name (case-insensitive partial match)"""
        name_lower = name.lower()
        for ip, device in self.devices.items():
            if name_lower in device['name'].lower() or name_lower in device.get('location', '').lower():
                return device
        return None
    
    def get_all_devices(self) -> List[dict]:
        """Get list of all configured devices"""
        return list(self.devices.values())
    
    def remove_device(self, ip: str):
        """Remove a device"""
        if ip in self.devices:
            del self.devices[ip]
            self._save_config()
    
    def is_paired(self, ip: str) -> bool:
        """Check if a device is paired"""
        device = self.devices.get(ip)
        return device.get('is_paired', False) if device else False


class HomeAutomation:
    """Control smart home devices with persistent async event loop"""
    
    def __init__(self, cert_dir: str = "."):
        self.tv_remote: Optional[AndroidTVRemote] = None
        self.tv_ip = None
        self.tv_name = None
        self.is_connected = False
        self.cert_dir = cert_dir
        self.certfile = os.path.join(cert_dir, "jarvis_tv_cert.pem")
        self.keyfile = os.path.join(cert_dir, "jarvis_tv_key.pem")
        
        # TV Configuration manager
        self.tv_config = TVConfig(cert_dir)
        
        # Event loop management - keeps connection alive
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Generate cert/key if they don't exist
        self._ensure_certificates()
        
        # Add default devices if none exist
        self._ensure_default_devices()
    
    def _ensure_default_devices(self):
        """Add default TV devices if config is empty"""
        if not self.tv_config.devices:
            # Add the hall TV as default
            self.tv_config.add_device(
                ip="192.168.1.2",
                name="Hall TV",
                location="Hall",
                is_paired=True  # Already paired from previous sessions
            )
    
    def add_tv(self, ip: str, name: str, location: str = "") -> bool:
        """Add a new TV to the configuration"""
        self.tv_config.add_device(ip, name, location)
        return True
    
    def get_tv_list(self) -> List[dict]:
        """Get list of all configured TVs"""
        return self.tv_config.get_all_devices()
    
    def find_tv_by_name(self, name: str) -> Optional[dict]:
        """Find a TV by name or location"""
        return self.tv_config.get_device_by_name(name)
    
    def get_current_tv_info(self) -> Optional[dict]:
        """Get info about currently connected TV"""
        if self.tv_ip:
            return self.tv_config.get_device(self.tv_ip)
        return None
    
    def _ensure_certificates(self):
        """Generate SSL certificates if they don't exist"""
        if os.path.exists(self.certfile) and os.path.exists(self.keyfile):
            return
        
        logger.info("Generating SSL certificates for TV connection...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Generate self-signed certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"Jarvis"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=3650)
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # Write private key
        with open(self.keyfile, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Write certificate
        with open(self.certfile, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        logger.info(f"Certificates created: {self.certfile}, {self.keyfile}")
    
    def _run_event_loop(self):
        """Run the event loop in a background thread"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    def _start_event_loop(self):
        """Start the background event loop thread"""
        if self._loop_thread is not None and self._loop_thread.is_alive():
            return
        
        self._loop = asyncio.new_event_loop()
        self._running = True
        self._loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._loop_thread.start()
    
    def _stop_event_loop(self):
        """Stop the background event loop"""
        if self._loop is not None and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._running = False
        if self._loop_thread is not None:
            self._loop_thread.join(timeout=2)
            self._loop_thread = None
            self._loop = None
    
    async def _async_connect_tv(self, ip_address: str, client_name: str = "Jarvis") -> bool:
        """Async TV connection implementation"""
        try:
            self.tv_ip = ip_address
            self.tv_remote = AndroidTVRemote(
                client_name=client_name,
                certfile=self.certfile,
                keyfile=self.keyfile,
                host=ip_address,
                loop=self._loop
            )
            
            # Try to connect
            try:
                await self.tv_remote.async_connect()
                self.is_connected = True
                self.tv_config.update_last_connected(ip_address)
                
                # Get device name if available
                device = self.tv_config.get_device(ip_address)
                self.tv_name = device['name'] if device else ip_address
                
                logger.info(f"Successfully connected to TV at {ip_address}")
                return True
            except Exception as connect_error:
                if "Need to pair" in str(connect_error):
                    # Start pairing process
                    logger.info("Starting pairing process...")
                    print("\n=== PAIRING REQUIRED ===")
                    print(f"Look at your TV screen (at {ip_address}).")
                    print("A pairing request should appear.")
                    print("Accept it, and a pairing code will be shown.\n")
                    
                    # Start pairing
                    await self.tv_remote.async_start_pairing()
                    
                    pairing_code = input("Enter the pairing code from your TV: ")
                    
                    await self.tv_remote.async_finish_pairing(pairing_code)
                    
                    # Now connect
                    await self.tv_remote.async_connect()
                    
                    self.is_connected = True
                    
                    # Mark as paired in config
                    self.tv_config.mark_paired(ip_address)
                    device = self.tv_config.get_device(ip_address)
                    self.tv_name = device['name'] if device else ip_address
                    
                    logger.info(f"Successfully paired and connected to TV at {ip_address}")
                    return True
                else:
                    raise connect_error
            
        except Exception as e:
            logger.error(f"Failed to connect to TV: {e}")
            self.is_connected = False
            return False
    
    def connect_tv(self, ip_address: str, client_name: str = "Jarvis") -> bool:
        """
        Connect to Android TV using the Remote protocol (sync wrapper)
        
        Args:
            ip_address: IP address of the TV
            client_name: Name to display on TV during pairing
            
        Returns:
            True if connected successfully
        """
        # Start the event loop if not running
        self._start_event_loop()
        
        # Schedule the connection and wait for result
        future = asyncio.run_coroutine_threadsafe(
            self._async_connect_tv(ip_address, client_name),
            self._loop
        )
        
        try:
            # Wait for connection with timeout
            return future.result(timeout=120)
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect_tv(self):
        """Disconnect from TV"""
        if self.tv_remote:
            try:
                self.tv_remote.disconnect()
            except:
                pass
            self.tv_remote = None
            self.is_connected = False
            logger.info("Disconnected from TV")
        
        # Stop the event loop
        self._stop_event_loop()
    
    def tv_send_key(self, key_code: str) -> bool:
        """
        Send a key command to TV
        
        Common key codes:
        - KEYCODE_POWER
        - KEYCODE_HOME
        - KEYCODE_BACK
        - KEYCODE_DPAD_UP, KEYCODE_DPAD_DOWN, KEYCODE_DPAD_LEFT, KEYCODE_DPAD_RIGHT
        - KEYCODE_DPAD_CENTER (OK/Select)
        - KEYCODE_VOLUME_UP, KEYCODE_VOLUME_DOWN, KEYCODE_VOLUME_MUTE
        - KEYCODE_MEDIA_PLAY, KEYCODE_MEDIA_PAUSE, KEYCODE_MEDIA_PLAY_PAUSE
        - KEYCODE_MEDIA_NEXT, KEYCODE_MEDIA_PREVIOUS
        """
        if not self.is_connected or not self.tv_remote:
            logger.error("Not connected to TV")
            return False
        
        if self._loop is None or not self._loop.is_running():
            logger.error("Event loop is not running")
            return False
            
        try:
            # send_key_command is sync but needs the loop to be running
            self.tv_remote.send_key_command(key_code)
            return True
        except Exception as e:
            logger.error(f"Failed to send key {key_code}: {e}")
            return False
    
    # Convenience methods
    def tv_power_toggle(self):
        """Toggle TV power"""
        return self.tv_send_key("KEYCODE_POWER")
    
    def tv_home(self):
        """Go to home screen"""
        return self.tv_send_key("KEYCODE_HOME")
    
    def tv_back(self):
        """Press back button"""
        return self.tv_send_key("KEYCODE_BACK")
    
    def tv_play_pause(self):
        """Toggle play/pause"""
        return self.tv_send_key("KEYCODE_MEDIA_PLAY_PAUSE")
    
    def tv_volume_up(self):
        """Increase volume"""
        return self.tv_send_key("KEYCODE_VOLUME_UP")
    
    def tv_volume_down(self):
        """Decrease volume"""
        return self.tv_send_key("KEYCODE_VOLUME_DOWN")
    
    def tv_mute(self):
        """Toggle mute"""
        return self.tv_send_key("KEYCODE_VOLUME_MUTE")
    
    def tv_navigate_up(self):
        """Navigate up"""
        return self.tv_send_key("KEYCODE_DPAD_UP")
    
    def tv_navigate_down(self):
        """Navigate down"""
        return self.tv_send_key("KEYCODE_DPAD_DOWN")
    
    def tv_navigate_left(self):
        """Navigate left"""
        return self.tv_send_key("KEYCODE_DPAD_LEFT")
    
    def tv_navigate_right(self):
        """Navigate right"""
        return self.tv_send_key("KEYCODE_DPAD_RIGHT")
    
    def tv_select(self):
        """Press OK/Select"""
        return self.tv_send_key("KEYCODE_DPAD_CENTER")
    
    def tv_search(self):
        """Open search/voice search"""
        return self.tv_send_key("KEYCODE_SEARCH")
    
    def tv_send_text(self, text: str) -> bool:
        """
        Send text input to TV (for search boxes, etc.)
        
        Args:
            text: Text to send
            
        Returns:
            True if text sent successfully
        """
        if not self.is_connected or not self.tv_remote:
            logger.error("Not connected to TV")
            return False
        
        if self._loop is None or not self._loop.is_running():
            logger.error("Event loop is not running")
            return False
        
        try:
            # androidtvremote2 doesn't have direct text input, so we simulate typing
            # by sending individual key events for each character
            # Actually, let's use the clipboard/paste approach or voice search
            
            # For now, trigger voice search which works well on Android TV
            self.tv_remote.send_key_command("KEYCODE_SEARCH")
            logger.info(f"Triggered search on TV")
            return True
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            return False
    
    # ============ APP LAUNCHERS ============
    # Common Android TV app package names and deep link URIs for search
    STREAMING_APPS = {
        'netflix': 'com.netflix.ninja',
        'prime': 'com.amazon.avod',
        'prime video': 'com.amazon.avod',
        'amazon prime': 'com.amazon.avod',
        'youtube': 'com.google.android.youtube.tv',
        'hotstar': 'in.startv.hotstar',
        'disney': 'in.startv.hotstar',
        'disney hotstar': 'in.startv.hotstar',
        'disney+': 'in.startv.hotstar',
        'zee5': 'com.graymatrix.did',
        'zee': 'com.graymatrix.did',
        'sonyliv': 'com.sonyliv',
        'sony liv': 'com.sonyliv',
        'sony': 'com.sonyliv',
        'jiocinema': 'com.jio.media.ondemand',
        'jio cinema': 'com.jio.media.ondemand',
        'jio': 'com.jio.media.ondemand',
        'spotify': 'com.spotify.tv.android',
        'plex': 'com.plexapp.android',
        'kodi': 'org.xbmc.kodi',
    }
    
    # Deep link URI templates for searching within apps
    APP_SEARCH_INTENTS = {
        'youtube': 'https://www.youtube.com/results?search_query={query}',
        'netflix': 'https://www.netflix.com/search?q={query}',
        'prime': 'https://www.primevideo.com/search?phrase={query}',
        'hotstar': 'https://www.hotstar.com/in/search?q={query}',
        'spotify': 'spotify:search:{query}',
    }
    
    def tv_launch_app_with_search(self, app_name: str, search_query: str = None) -> bool:
        """
        Launch a streaming app and optionally search for content
        
        Args:
            app_name: Name of the app (netflix, prime, youtube, etc.)
            search_query: Optional search query to find content
            
        Returns:
            True if command sent successfully
        """
        if not self.is_connected or not self.tv_remote:
            logger.error("Not connected to TV")
            return False
        
        if self._loop is None or not self._loop.is_running():
            logger.error("Event loop is not running")
            return False
        
        app_name_lower = app_name.lower().strip()
        package_name = self.STREAMING_APPS.get(app_name_lower)
        
        if not package_name:
            logger.error(f"Unknown app: {app_name}. Available: {list(self.STREAMING_APPS.keys())}")
            return False
        
        try:
            if search_query:
                # Try to use deep link with search query
                import urllib.parse
                encoded_query = urllib.parse.quote(search_query)
                
                # Check if we have a search intent for this app
                search_template = self.APP_SEARCH_INTENTS.get(app_name_lower)
                
                if search_template:
                    search_uri = search_template.format(query=encoded_query)
                    # Send the URI as a deep link
                    try:
                        self.tv_remote.send_launch_app_command(search_uri)
                        logger.info(f"Launched {app_name} with search: {search_query}")
                        return True
                    except:
                        pass
                
                # Fallback: Launch app normally, then we'll handle search separately
                self.tv_remote.send_launch_app_command(package_name)
                logger.info(f"Launched app: {app_name}, search query: {search_query}")
                
                # Note: To actually search, user would need to use voice search on TV
                # or we'd need to implement ADB text input
                return True
            else:
                # Just launch the app
                self.tv_remote.send_launch_app_command(package_name)
                logger.info(f"Launched app: {app_name} ({package_name})")
                return True
                
        except Exception as e:
            logger.error(f"Failed to launch app {app_name}: {e}")
            return False
    
    def tv_launch_app(self, app_name: str, search_query: str = None) -> bool:
        """
        Launch a streaming app on the TV (wrapper for tv_launch_app_with_search)
        
        Args:
            app_name: Name of the app (netflix, prime, youtube, etc.)
            search_query: Optional search query
            
        Returns:
            True if command sent successfully
        """
        return self.tv_launch_app_with_search(app_name, search_query)
    
    def tv_open_netflix(self, search_query: str = None):
        """Open Netflix, optionally with a search"""
        return self.tv_launch_app('netflix', search_query)
    
    def tv_open_prime(self, search_query: str = None):
        """Open Amazon Prime Video, optionally with a search"""
        return self.tv_launch_app('prime', search_query)
    
    def tv_open_youtube(self, search_query: str = None):
        """Open YouTube, optionally with a search"""
        return self.tv_launch_app('youtube', search_query)
    
    def tv_open_hotstar(self):
        """Open Disney+ Hotstar"""
        return self.tv_launch_app('hotstar')
    
    def tv_open_zee5(self):
        """Open ZEE5"""
        return self.tv_launch_app('zee5')
    
    def tv_open_sonyliv(self):
        """Open SonyLIV"""
        return self.tv_launch_app('sonyliv')
    
    def tv_open_jiocinema(self):
        """Open JioCinema"""
        return self.tv_launch_app('jiocinema')


# Test function
def test_tv_connection(ip_address: str):
    """Test TV connection"""
    ha = HomeAutomation()
    
    print(f"Connecting to TV at {ip_address}...")
    if ha.connect_tv(ip_address):
        print("✓ Connected successfully!")
        
        # Test some commands
        print("\nTesting commands...")
        print("Sending HOME...")
        ha.tv_home()
        time.sleep(1)
        
        print("Sending VOLUME_UP...")
        ha.tv_volume_up()
        time.sleep(1)
        
        print("Sending VOLUME_DOWN...")
        ha.tv_volume_down()
        time.sleep(1)
        
        ha.disconnect_tv()
        print("\n✓ Test complete!")
    else:
        print("✗ Connection failed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        test_tv_connection(ip)
    else:
        print("Usage: python home_automation.py <TV_IP_ADDRESS>")
        print("Example: python home_automation.py 192.168.1.2")
