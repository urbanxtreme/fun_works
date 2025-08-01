from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import pyperclip
import asyncio
import aiohttp
import json
import random
from datetime import datetime
import logging

EMAIL = "skrhari2020@gmail.com"
PASSWORD = "Technology*19112005"
LOGIN_URL = "https://tracking.hard-softwerk.com"
INTERACTIVE_MODE = False
IMAGE_TO_UPLOAD = "latex.jpg"
# --------------------------- SELECTORS ---------------------------
EMAIL_SELECTOR = 'input[placeholder="Username/Email"]'
PASSWORD_SELECTOR = 'input[type="password"]'
LOGIN_BUTTON_SELECTOR = 'button:has-text("Login")'

USER_DROPDOWN_SELECTOR = 'button.user-dropdown-button'
ORG_SETTINGS_BUTTON='button.dropdown-item:has-text("ORG Settings")'
SEARCH_BAR_CLICK='input.form-control[placeholder="Search by name"]'
ORG_SELECTOR='div.org-item:has-text("Automation Org")'
GENERATE_BUTTON_SELECTOR = 'button.btn.btn-sm.org-settings-btn:has-text("Generate")';
CLOSE_BUTTON='button.modal-close-btn'



def login_to_app():
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(LOGIN_URL)
        page.wait_for_selector(EMAIL_SELECTOR)
        page.fill(EMAIL_SELECTOR, EMAIL)
        page.wait_for_selector(PASSWORD_SELECTOR)
        page.fill(PASSWORD_SELECTOR, PASSWORD)
        page.wait_for_selector(LOGIN_BUTTON_SELECTOR)
        page.click(LOGIN_BUTTON_SELECTOR)
        page.wait_for_timeout(5000)
        print("Login successful!")
        return page, browser, playwright
    except PlaywrightTimeoutError as e:
        print(f"Login failed due to timeout: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error during login: {e}")
        exit(1)


def take_x_api(page):
    try:
        page.wait_for_selector(USER_DROPDOWN_SELECTOR, timeout=5000)
        page.click(USER_DROPDOWN_SELECTOR)
        page.wait_for_selector(ORG_SETTINGS_BUTTON, timeout=5000)
        page.click(ORG_SETTINGS_BUTTON)
        page.wait_for_selector(SEARCH_BAR_CLICK, timeout=5000)
        page.click(SEARCH_BAR_CLICK)
        page.wait_for_selector(ORG_SELECTOR, timeout=5000)
        page.click(ORG_SELECTOR)
        copy_button = page.locator('button[title="Copy to clipboard"]:below(:text("Data API Key"))')
        generate_button = page.locator('button:has-text("Generate"):below(:text("Data API Key"))')
        if copy_button.is_visible():
            print("Copy button is already visible. Copying API key...")
            copy_button.click()
        else:
            print("Copy button not visible. Generating API key...")
            generate_button.wait_for(timeout=10000)
            generate_button.click()
            page.wait_for_timeout(2000)  # wait for key to be generated and copy button to appear
            copy_button.wait_for(timeout=5000)
            copy_button.click()
            print("API key generated and copied.")
        page.wait_for_selector(CLOSE_BUTTON, timeout=5000)
        page.click(CLOSE_BUTTON)
    except Exception as e:
        print(f"Error while handling API key: {e}")

def get_clipboard_content():
    try:
        return pyperclip.paste().strip()
    except Exception as e:
        print(f"Failed to get clipboard content: {e}")
        return None



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HubSimulator')

# Configuration
API_ENDPOINT = "https://apx.aneeshprasobhan.xyz/data"
API_KEY = "dfc8c4ba805658943dbfa69a18a2c1c6"

# Simulation Configuration
NUM_HUBS = 5  # Number of hubs to simulate
NUM_BEACONS_PER_HUB = 5  # Number of beacons each hub should detect

# Hub base configuration
HUB_BASE_CONFIG = {
    'name_prefix': 'Asset',
    'hub_id_prefix': 'hub',
    'zone_prefix': 'Test222',
    'interval_range': (5.0, 20.0),  # Random interval between these values
    'rssi_range': (-100, -40)  # RSSI range for random generation
}

class HubSimulator:
    def __init__(self, session):
        self.session = session

    def generate_random_mac_address(self):
        """Generate a random MAC address"""
        return ''.join([f'{random.randint(0, 255):02X}' for _ in range(6)])

    def generate_hub_config(self, hub_index):
        """Generate configuration for a hub"""
        return {
            'name': f"{HUB_BASE_CONFIG['name_prefix']} {hub_index + 1}",
            'hubId': f"{HUB_BASE_CONFIG['hub_id_prefix']}{hub_index:02d}",
            'zone': f"{HUB_BASE_CONFIG['zone_prefix']}{hub_index + 1}",
            'interval': random.uniform(*HUB_BASE_CONFIG['interval_range']),
            'rssi_range': HUB_BASE_CONFIG['rssi_range']
        }

    def generate_beacon_data(self, hub_config):
        """Generate multiple beacon data entries for a hub"""
        current_timestamp = int(datetime.now().timestamp() * 1000)
        rssi_min, rssi_max = hub_config['rssi_range']
        
        items = []
        for i in range(NUM_BEACONS_PER_HUB):
            mac_address = self.generate_random_mac_address()
            
            beacon_item = {
                "macAddress": mac_address,
                "blukiiId": f"blukii BXXXXX {mac_address}",
                "batteryPct": random.randint(20, 100),  # Random battery level
                "rssi": [{
                        "rssi": random.randint(rssi_min, rssi_max),
                        "timestamp": current_timestamp
                } for _ in range(10)],
                "iBeaconData": [{
                        "uuid": "626C756B-6969-2E63-6F6D-626561636F6E",
                        "major": random.randint(1, 65535),  # Random major value
                "minor": random.randint(1, 65535),  # Random minor value
                "measuredPower": random.randint(-70, -50),  # Random measured power
                "timestamp": current_timestamp + random.randint(-500, 500)
                }]
            }
            items.append(beacon_item)
        
        return {
            "id": hub_config['hubId'],
            "items": items
        }

    async def send_hub_data(self, hub_config):
        """Continuously send data for a specific hub"""
        logger.info(f"Starting simulation for {hub_config['name']} "
                   f"(Hub ID: {hub_config['hubId']}) with {NUM_BEACONS_PER_HUB} beacons")
        
        while True:
            try:
                data = self.generate_beacon_data(hub_config)
                headers = {"x-api-key": API_KEY}
                
                async with self.session.post(API_ENDPOINT, json=data, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Data sent successfully for {hub_config['name']} "
                                  f"(Hub ID: {hub_config['hubId']}) in {hub_config['zone']} "
                                  f"- {NUM_BEACONS_PER_HUB} beacons")
                    else:
                        logger.error(f"Failed to send data for {hub_config['name']}. "
                                   f"Status: {response.status}")
                
                await asyncio.sleep(hub_config['interval'])
                
            except Exception as e:
                logger.error(f"Error sending data for {hub_config['name']}: {str(e)}")
                await asyncio.sleep(1)

async def main():
    """Main function to run all hub simulators"""
    async with aiohttp.ClientSession() as session:
        simulator = HubSimulator(session)
        
        # Generate hub configurations
        hubs_config = [simulator.generate_hub_config(i) for i in range(NUM_HUBS)]
        
        # Log simulation setup
        logger.info(f"Starting simulation with {NUM_HUBS} hubs, "
                   f"{NUM_BEACONS_PER_HUB} beacons per hub")
        
        # Create tasks for each hub
        tasks = [simulator.send_hub_data(hub) for hub in hubs_config]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Stopping simulation...")

if __name__ == "__main__":
    page, browser, playwright = login_to_app()
    logger.info("Starting Hub Simulator...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Simulation terminated by user")
