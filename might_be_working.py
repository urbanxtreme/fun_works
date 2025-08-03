import asyncio
import aiohttp
import random
from datetime import datetime
import logging
import signal
import json
import os
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HubAssetSimulator")

API_ENDPOINT = "https://apx.aneeshprasobhan.xyz/data"
X_API_KEY = "again, hell nahhh!!"

if not os.path.exists("created_data.json"):
    logger.error("'created_data.json' ot found bruhh!!")
    exit(1)

with open("created_data.json", "r") as f:
    data = json.load(f)

ASSET_MACS = data["assets"]
ASSETS = list(ASSET_MACS.keys())
HUBS_CONFIG = data["hubs"]
ASSETS = list(ASSET_MACS.keys())
running = True
running = True

def shutdown():
    global running
    logger.info("Stop signal received. Shutting down................")
    running = False

def wait_for_enter():
    input("Press Enter to stop the simulation...........\n")
    shutdown()
signal.signal(signal.SIGINT, lambda s, f: shutdown())
signal.signal(signal.SIGTERM, lambda s, f: shutdown())
threading.Thread(target=wait_for_enter, daemon=True).start()

class HubAssetSimulator:
    def __init__(self, session):
        self.session = session
    def create_data_packet(self, hub, asset_name, mac_address):
        current_timestamp = int(datetime.now().timestamp() * 1000)
        rssi_value = random.randint(*hub['rssi_range'])
        return {
            "id": hub['hubId'],
            "items": [{
                "macAddress": mac_address,
                "blukiiId": f"blukii {asset_name}",
                "batteryPct": 100,
                "timestamp": current_timestamp,
                "rssi": [{
                    "rssi": rssi_value,
                    "timestamp": current_timestamp
                }],
                "iBeaconData": [{
                    "uuid": "626C756B-6969-2E63-6F6D-626561636F6E",
                    "major": 1,
                    "minor": random.randint(10000, 50000),
                    "measuredPower": -57,
                    "timestamp": current_timestamp
                }]
            }]
        }

    async def send_to_hub(self, hub):
        global running
        while running:
            for asset_name in ASSETS:
                mac_address = ASSET_MACS[asset_name]
                try:
                    data = self.create_data_packet(hub, asset_name, mac_address)
                    headers = {
                        'X-API-KEY': X_API_KEY,
                        'Content-Type': 'application/json'
                    }
                    async with self.session.post(API_ENDPOINT, json=data, headers=headers) as response:
                        if response.status == 200:
                            logger.info(f"Sent {asset_name} to {hub['name']} in {hub['zone']}")
                        else:
                            logger.warning(f"Failed to send {asset_name} to {hub['name']}: Status {response.status}")
                except Exception as e:
                    logger.error(f"Error sending {asset_name} to {hub['name']}: {str(e)}")
            await asyncio.sleep(hub['interval'])

async def main():
    async with aiohttp.ClientSession() as session:
        simulator = HubAssetSimulator(session)
        tasks = [simulator.send_to_hub(hub) for hub in HUBS_CONFIG]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    logger.info("Hub-Asset Simulation Started.......")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Simulation manually stopped by user.")
