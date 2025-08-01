# import asyncio
# import aiohttp
# import json
# import random
# from datetime import datetime
# import logging



# import sys

# if len(sys.argv) < 3:
#     print("❌ Error: Please pass MAC ID and X-API Key as arguments.")
#     sys.exit(1)

# TEST_BEACON = sys.argv[1]
# X_API_KEY = sys.argv[2]


# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger('HubSimulator')

# # Configuration
# # API_ENDPOINT = "https://api-tracking.hard-softwerk.com/data"
# API_ENDPOINT = "https://apx-tracking.hard-softwerk.com/data"
# X_API_KEY = "bd8693649f121a16a6e8a40766eb6d02"

# # Hub configurations with different zones
# HUBS_CONFIG = [
#     {
#         'name': 'Kuhlraum 7',
#         'hubId': 'hub55555556',
#         'zone': 'Zone1',
#         'interval': 1.0,  # Send every 1 second
#         'rssi_range': (-80, -20)  # Customize RSSI range for this hub
#     },
#     {
#         'name': 'Kuhlraum 7',
#         'hubId': 'hub55555556',
#         'zone': 'Zone1',
#         'interval': 2.0,  # Send every 1 second
#         'rssi_range': (-60, -40)  # Slightly different RSSI range
#     }
# ]

# # Test beacon
# TEST_BEACON = 'E4E1129BDB4D'

# class HubSimulator:
#     def __init__(self, session):
#         self.session = session

#     def create_beacon_data(self, hub_config):
#         """Create beacon data with customized RSSI values for each hub"""
#         current_timestamp = int(datetime.now().timestamp() * 1000)
#         rssi_min, rssi_max = hub_config['rssi_range']
        
#         return {
#             "id": hub_config['hubId'],
#             "items": [{
#                 "macAddress": TEST_BEACON,
#                 "blukiiId": f"blukii BXXXXX {TEST_BEACON}",
#                 "batteryPct": 100,
#                 "timestamp": current_timestamp,
#                 "rssi": [{
#                     "rssi": random.randint(rssi_min, rssi_max),
#                     "timestamp": current_timestamp
#                 }],
#                 "iBeaconData": [{
#                     "uuid": "626C756B-6969-2E63-6F6D-626561636F6E",
#                     "major": 1,
#                     "minor": random.randint(10000, 50000),
#                     "measuredPower": -57,
#                     "timestamp": current_timestamp
#                 }]
#             }]
#         }

#     async def send_hub_data(self, hub_config):
#         """Continuously send data for a specific hub"""
#         while True:
#             try:
#                 data = self.create_beacon_data(hub_config)
                
#                 # Create headers with X-API-KEY
#                 headers = {
#                     'X-API-KEY': X_API_KEY,
#                     'Content-Type': 'application/json'
#                 }
                
#                 # Send to API with X-API-KEY header
#                 async with self.session.post(API_ENDPOINT, json=data, headers=headers) as response:
#                     if response.status == 200:
#                         logger.info(f"Data sent successfully for {hub_config['name']} "
#                                   f"(Hub ID: {hub_config['hubId']}) in {hub_config['zone']} with X-API-KEY")
#                     else:
#                         logger.error(f"Failed to send data for {hub_config['name']}. "
#                                    f"Status: {response.status}")
                
#                 # Wait for the specified interval
#                 await asyncio.sleep(hub_config['interval'])
                
#             except Exception as e:
#                 logger.error(f"Error sending data for {hub_config['name']}: {str(e)}")
#                 await asyncio.sleep(1)  # Wait before retrying

# async def main():
#     """Main function to run all hub simulators"""
#     async with aiohttp.ClientSession() as session:
#         simulator = HubSimulator(session)
        
#         # Create tasks for each hub
#         tasks = [simulator.send_hub_data(hub) for hub in HUBS_CONFIG]
        
#         try:
#             # Run all tasks concurrently
#             await asyncio.gather(*tasks)
#         except KeyboardInterrupt:
#             logger.info("Stopping simulation...")

# if __name__ == "__main__":
#     logger.info("Starting Hub Simulator...")
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Simulation terminated by user")




import asyncio
import aiohttp
import json
import random
from datetime import datetime
import logging
import sys
import os
import signal

# Parse command-line args
if len(sys.argv) < 3:
    print("\u274c Error: Please pass MAC ID and X-API Key as arguments.")
    sys.exit(1)

TEST_BEACON = sys.argv[1]
X_API_KEY = sys.argv[2]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HubSimulator')

# API_ENDPOINT = "https://api-tracking.hard-softwerk.com/data"
API_ENDPOINT = "https://apx-tracking.hard-softwerk.com/data"

HUBS_CONFIG = [
    {
        'name': 'Kuhlraum 7',
        'hubId': 'hub55555556',
        'zone': 'Zone1',
        'interval': 1.0,
        'rssi_range': (-80, -20)
    },
    {
        'name': 'Kuhlraum 7',
        'hubId': 'hub55555556',
        'zone': 'Zone1',
        'interval': 2.0,
        'rssi_range': (-60, -40)
    }
]

# Flag to indicate if the simulator should keep sending data
running = True

# Graceful shutdown signal handler
def shutdown_handler(signum, frame):
    global running
    running = False
    logger.info("\ud83d\udd1d Received shutdown signal. Stopping simulation...")

# Register signal handlers for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

class HubSimulator:
    def __init__(self, session):
        self.session = session

    def create_beacon_data(self, hub_config):
        current_timestamp = int(datetime.now().timestamp() * 1000)
        rssi_min, rssi_max = hub_config['rssi_range']
        return {
            "id": hub_config['hubId'],
            "items": [{
                "macAddress": TEST_BEACON,
                "blukiiId": f"blukii BXXXXX {TEST_BEACON}",
                "batteryPct": 100,
                "timestamp": current_timestamp,
                "rssi": [{
                    "rssi": random.randint(rssi_min, rssi_max),
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

    async def send_hub_data(self, hub_config):
        global running
        while running:
            try:
                data = self.create_beacon_data(hub_config)
                headers = {
                    'X-API-KEY': X_API_KEY,
                    'Content-Type': 'application/json'
                }
                async with self.session.post(API_ENDPOINT, json=data, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Data sent successfully for {hub_config['name']} in {hub_config['zone']}")
                    else:
                        logger.error(f"Failed to send data: {response.status}")
            except Exception as e:
                logger.error(f"Error sending data: {str(e)}")

            await asyncio.sleep(hub_config['interval'])

async def main():
    async with aiohttp.ClientSession() as session:
        simulator = HubSimulator(session)
        tasks = [simulator.send_hub_data(hub) for hub in HUBS_CONFIG]
        await asyncio.gather(*tasks)

def shutdown_handler(signum, frame):
    logger.info("🛑 Shutdown signal received. Exiting...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    logger.info("\ud83d\ude80 Hub Simulator started.")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\ud83d\udc4b Simulation terminated by user.")

