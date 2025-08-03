import requests
import json
import random
import string

ASSET_URL = "https://apx.aneeshprasobhan.xyz/new-assets"
HUB_URL = "https://apx.aneeshprasobhan.xyz/hubs"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNrcmhhcmkyMDIwQGdtYWlsLmNvbSIsInVzZXJfdHlwZSI6IlN1cGVyIEFkbWluIiwib3JnIjoiSFNXIiwiaWF0IjoxNzU0MDMwNjU1LCJleHAiOjE3NTY2MjI2NTV9.eeP0nok_XVqpRWq3tSmC57K35DN4vRefXw4EMob0F2c"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}"
}
ORG_NAME = "LOAD TESTING"
LOCALE = "LOAD TESTING BUILDING"
ZONES = ["Test222", "Test333"]

def generate_mac():
    return ''.join(random.choices("ABCDEF0123456789", k=12))

def generate_hub_id():
    return "hub" + ''.join(random.choices("0123456789ABCDEF", k=8))

# ----------------- Create 10 Assets -----------------
assets = []
for i in range(10):
    asset = {
        "macAddress": generate_mac(),
        "assetName": f"Asset {i+1}",
        "humanFlag": False,
        "org": ORG_NAME
    }
    assets.append(asset)

response_asset = requests.post(ASSET_URL, headers=HEADERS, data=json.dumps(assets))
if response_asset.status_code in [200, 201]:
    print("10 Assets created successfully!")
    print("Response:", response_asset.json())
else:
    print("Asset creation failed!")
    print("Status Code:", response_asset.status_code)
    print("Response:", response_asset.text)

response_json = response_asset.json() if response_asset.status_code in [200, 201] else {}
results = response_json.get("results", [])
asset_macs = {
    f"asset_{i+1}": asset["macAddress"]
    for i, asset in enumerate(results)
    if "macAddress" in asset
}




hub_configs = []
for i in range(5):
    hub_id = generate_hub_id()
    zone = ZONES[i % len(ZONES)]
    hub_payload = {
        "hubId": hub_id,
        "org": ORG_NAME,
        "locale_info": LOCALE,
        "floor": 0,
        "open_ground": False,
        "zoneName": zone,
        "weight": 1.0,
        "type": "RSSIhub",
        "coordinates": {
            "lat": round(random.uniform(8.691093358756355, 8.691110581493389), 6),
            "lng": round(random.uniform(76.820471421065861, 76.820877956116448), 6)
        },
        "height": 2.5,
        "orientationAngle": 0,
        "tiltAngle": 0
    }
    response = requests.post(HUB_URL, headers=HEADERS, data=json.dumps(hub_payload))
    if response.status_code in [200, 201]:
        print(f"Hub {i+1} created in zone {zone} successfully!")
        print("Response:", response.json())
        hub_configs.append({
            "hubId": hub_id,
            "name": zone,
            "zone": zone,
            "interval": 1.0,
            "rssi_range": [-80, -40]
        })
    else:
        print(f"Hub {i+1} creation failed!")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

with open("created_data.json", "w") as f:
    json.dump({
        "assets": asset_macs,
        "hubs": hub_configs
    }, f, indent=2)

print("Saved created hubs and assets to 'created_data.json'")