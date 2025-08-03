import requests
import json

# ---------------- USER CONFIG ----------------
DELETE_URL = "https://apx.aneeshprasobhan.xyz/delete-assets"
BEARER_TOKEN = "huh, why do you need that"

# Replace this list with actual MACs if known
mac_addresses_to_delete = [
    "7E928A75CD12","87574885683D","98528D5FD6F2","D258F6A91D4E","E3E9925FC8F8"
]

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

# Prepare payload
payload = {
    "macAddresses": mac_addresses_to_delete
}

# Send DELETE request
response = requests.delete(DELETE_URL, headers=HEADERS, data=json.dumps(payload))

# Handle response
if response.status_code in [200, 201]:
    print("✅ Assets deleted successfully!")
    print("Response:", response.json())
else:
    print("❌ Failed to delete assets!")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
