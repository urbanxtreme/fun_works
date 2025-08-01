import requests
import json
import random
import string

# API URLs
ASSET_URL = "https://apx.aneeshprasobhan.xyz/new-assets"
HUB_URL = "https://apx.aneeshprasobhan.xyz/hubs"

# Bearer Token
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNrcmhhcmkyMDIwQGdtYWlsLmNvbSIsInVzZXJfdHlwZSI6IlN1cGVyIEFkbWluIiwib3JnIjoiSFNXIiwiaWF0IjoxNzU0MDMwNjU1LCJleHAiOjE3NTY2MjI2NTV9.eeP0nok_XVqpRWq3tSmC57K35DN4vRefXw4EMob0F2c"

# Common headers
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

# Constants
ORG_NAME = "LOAD TESTING"
LOCALE = "LOAD TESTING BUILDING"
ZONES = ["Test222", "Test333"]


def generate_mac():
    return ''.join(random.choices("ABCDEF0123456789", k=12))


def generate_hub_id():
    return "hub" + ''.join(random.choices("0123456789ABCDEF", k=8))


# Create 10 Assets
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
    print("✅ 10 Assets created successfully!")
    print("Response:", response_asset.json())
else:
    print("❌ Asset creation failed!")
    print("Status Code:", response_asset.status_code)
    print("Response:", response_asset.text)

# Create 5 Hubs with alternating zone names
for i in range(5):
    hub = {
        "hubId": generate_hub_id(),
        "org": ORG_NAME,
        "locale_info": LOCALE,
        "floor": 0,
        "open_ground": False,
        "zoneName": ZONES[i % len(ZONES)],
        "weight": 1.0,
        "type": "RSSIhub",
        "coordinates": {
            "lat": round(random.uniform(8.691094549454160, 8.691067851055125), 6),
            "lng": round(random.uniform(76.819592673363445, 76.820271436029216), 6)
        },
        "height": 2.5,
        "orientationAngle": 0,
        "tiltAngle": 0
    }

    response_hub = requests.post(HUB_URL, headers=HEADERS, data=json.dumps(hub))
    if response_hub.status_code in [200, 201]:
        print(f"✅ Hub {i+1} created in zone {hub['zoneName']} successfully!")
        print("Response:", response_hub.json())
    else:
        print(f"❌ Hub {i+1} creation failed!")
        print("Status Code:", response_hub.status_code)
        print("Response:", response_hub.text)
