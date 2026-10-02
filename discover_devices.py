"""
Home Automation Device Discovery and Control Module
Supports: TP-Link Kasa, Google Cast (Chromecast/Android TV), mDNS Discovery
"""

import asyncio
import socket
import logging
import json
import time

# TP-Link Kasa
from kasa import Discover

# Google Cast
import pychromecast

# mDNS / Zeroconf
from zeroconf import Zeroconf, ServiceBrowser

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MDNSListener:
    def __init__(self):
        self.services = []

    def remove_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            self.services.append({
                "name": name,
                "type": type,
                "address": ".".join(map(str, info.addresses[0])) if info.addresses else None,
                "port": info.port,
                "server": info.server
            })

class HomeAutomationDiscovery:
    def __init__(self):
        self.discovered_devices = {
            "kasa": [],
            "cast": [],
            "general_mdns": []
        }

    async def discover_kasa_devices(self):
        """Discover TP-Link Kasa devices (Plugs, Bulbs, Switches)"""
        print("\n--- Scanning for TP-Link Kasa Devices ---")
        try:
            found_devices = await Discover.discover()
            for addr, dev in found_devices.items():
                await dev.update()
                device_info = {
                    "alias": dev.alias,
                    "model": dev.model,
                    "ip": addr,
                    "type": dev.device_type.name,
                    "state": "ON" if dev.is_on else "OFF"
                }
                self.discovered_devices["kasa"].append(device_info)
                print(f"[Kasa] Found: {dev.alias} ({dev.model}) at {addr}")
        except Exception as e:
            logger.error(f"Error discovering Kasa devices: {e}")

    def discover_cast_devices(self):
        """Discover Google Cast / Android TV devices"""
        print("\n--- Scanning for Google Cast / Android TV Devices ---")
        try:
            services, browser = pychromecast.discovery.discover_chromecasts()
            pychromecast.discovery.stop_discovery(browser)
            
            for service in services:
                # service is a tuple (uuid, service_name, friendly_name, host, port)
                # or an object depending on version. Let's inspect safely.
                friendly_name = service.friendly_name
                ip_address = service.host
                port = service.port
                uuid = str(service.uuid)
                
                device_info = {
                    "friendly_name": friendly_name,
                    "ip": ip_address,
                    "port": port,
                    "uuid": uuid,
                    "type": "cast"
                }
                self.discovered_devices["cast"].append(device_info)
                print(f"[Cast] Found: {friendly_name} at {ip_address}:{port}")
                
        except Exception as e:
            logger.error(f"Error discovering Cast devices: {e}")

    def discover_general_mdns(self):
        """
        Broad mDNS scan to find other potential smart devices 
        (Apple TV, Printers, HomeKit, etc.)
        """
        print("\n--- Scanning mDNS Services (General) ---")
        zeroconf = Zeroconf()
        listener = MDNSListener()
        # Common service types
        service_types = [
            "_googlecast._tcp.local.",
            "_airplay._tcp.local.",
            "_spotify-connect._tcp.local.",
            "_miio._udp.local.", # Xiaomi
            "_hap._tcp.local."   # HomeKit
        ]
        
        browser = ServiceBrowser(zeroconf, service_types, listener)
        time.sleep(3) # Wait for responses
        zeroconf.close()
        
        for svc in listener.services:
            # Avoid duplicates if possible or just log them
            self.discovered_devices["general_mdns"].append(svc)
            print(f"[mDNS] Found service: {svc['name']} at {svc['address']}")

    async def run_all_discovery(self):
        await self.discover_kasa_devices()
        self.discover_cast_devices()
        self.discover_general_mdns()
        
        print("\n--- Discovery Summary ---")
        print(json.dumps(self.discovered_devices, indent=4))
        
        # Save to file for Jarvis to use later
        with open("discovered_devices.json", "w") as f:
            json.dump(self.discovered_devices, f, indent=4)
        print("Devices saved to discovered_devices.json")

if __name__ == "__main__":
    discovery = HomeAutomationDiscovery()
    asyncio.run(discovery.run_all_discovery())
