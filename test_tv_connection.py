"""
Script to test connection to an Android TV or Apple TV directly by IP.
"""
from androidtv import setup
import asyncio
import pyatv
import pychromecast
import sys
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_android_tv_adb(ip_address):
    print(f"\n--- Testing Android TV Connection via ADB to {ip_address} ---")
    try:
        # Create an AndroidTV object using the setup function (synchronous)
        print("Attempting to connect via ADB (port 5555)...")
        
        # Setup returns AndroidTVSync object (not async)
        aftv = setup(ip_address, device_class='androidtv')
        
        if aftv:
            print("Successfully connected to Android TV!")
            
            # Get device state (sync calls, no await)
            state = aftv.update()
            print(f"Device State: {state}")
            
            # Get current app
            current_app = aftv.current_app
            print(f"Current App: {current_app}")
            
            return True
        else:
            print("Could not connect via ADB.")
            return False
            
    except Exception as e:
        print(f"Error connecting to Android TV via ADB: {e}")
        return False

def test_cast_device(ip_address):
    print(f"\n--- Testing Google Cast Connection to {ip_address} ---")
    try:
        # Try to connect via Chromecast/Google Cast protocol
        print("Attempting to connect via Cast protocol...")
        
        cast = pychromecast.Chromecast(ip_address)
        cast.wait()
        
        print(f"Successfully connected via Cast!")
        print(f"Device Name: {cast.name}")
        print(f"Model Name: {cast.model_name}")
        print(f"Status: {cast.status}")
        
        return True
        
    except Exception as e:
        print(f"Error connecting via Cast: {e}")
        return False

async def scan_for_apple_tv():
    print("\n--- Scanning for Apple TV (pyatv) ---")
    atvs = await pyatv.scan(loop=asyncio.get_event_loop())
    
    if not atvs:
        print("No Apple TVs found via scan.")
        return

    for atv in atvs:
        print(f"Found Apple TV: {atv.name} at {atv.address}")
        print("To pair, we need to run a pairing script.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_ip = sys.argv[1]
        
        print(f"\n=== Testing Connection to {target_ip} ===\n")
        
        # Try Cast first (most common for Android TVs)
        if test_cast_device(target_ip):
            print("\n✓ Cast connection successful! Your TV supports Google Cast.")
        else:
            print("\n✗ Cast connection failed.")
        
        # Try ADB
        if test_android_tv_adb(target_ip):
            print("\n✓ ADB connection successful!")
        else:
            print("\n✗ ADB connection failed.")
            print("\nTo enable ADB:")
            print("1. Go to Settings → About → Build (tap 7 times)")
            print("2. Go to Developer Options → Network Debugging (enable)")
        
        # Try Apple TV scan
        print("\n--- Checking for Apple TV ---")
        asyncio.run(scan_for_apple_tv())
        
    else:
        # Check for user input or run scan
        print("Usage: python test_tv_connection.py <IP_ADDRESS_OF_TV>")
        print("Example: python test_tv_connection.py 192.168.1.15")
        
        # If no IP provided, try Apple TV scan just in case
        asyncio.run(scan_for_apple_tv())
