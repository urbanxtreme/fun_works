# import requests
# import json

# # -------------------- CONFIG --------------------
# ORG_NAME = "LOAD TESTING"
# GET_ENDPOINT = f"https://apx.aneeshprasobhan.xyz/assets?org={ORG_NAME}"
# DELETE_ENDPOINT = "https://apx.aneeshprasobhan.xyz/delete-assets"
# AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNrcmhhcmkyMDIwQGdtYWlsLmNvbSIsInVzZXJfdHlwZSI6IlN1cGVyIEFkbWluIiwib3JnIjoiSFNXIiwiaWF0IjoxNzU0MjA0MjU4LCJleHAiOjE3NTY3OTYyNTh9.yp1m-6ArvjhYsAHkmrGDF5oZqtumWVUq-24T5x4pwyk"  # Replace with your actual token

# HEADERS_GET = {
#     "Content-Type": "application/json",
#     "Authorization": f"Bearer {AUTH_TOKEN}"  # ← Add this line
# }


# HEADERS_DELETE = {
#     "Content-Type": "application/json",
#     "Authorization": f"Bearer {AUTH_TOKEN}"
# }
# # -------------------------------------------------

# # Step 1: GET assets from org
# print("[*] Fetching asset data...")

# response_asset = requests.get(GET_ENDPOINT, headers=HEADERS_GET)

# if response_asset.status_code not in [200, 201]:
#     print(f"❌ Failed to fetch assets. Status code: {response_asset.status_code}")
#     print("Response:", response_asset.text)
#     exit()

# response_json = response_asset.json()

# # Step 2: Extract MAC addresses from all groups
# mac_address_list = []

# for group_name, assets in response_json.items():
#     if isinstance(assets, list):
#         for asset in assets:
#             mac = asset.get("macAddress")
#             if mac:
#                 mac_address_list.append(mac)

# if not mac_address_list:
#     print("⚠️ No MAC addresses found in the response.")
#     exit()

# # Optional: Display found MACs
# print(f"✅ Found {len(mac_address_list)} assets to delete:")
# for mac in mac_address_list:
#     print(" -", mac)

# # Step 3: Send delete request
# print("[*] Sending delete request to:", DELETE_ENDPOINT)

# delete_payload = {
#     "macAddresses": mac_address_list
# }

# response_delete = requests.delete(DELETE_ENDPOINT, headers=HEADERS_DELETE, json=delete_payload)

# # Step 4: Print response
# print("Status Code:", response_delete.status_code)
# try:
#     print("Response:", response_delete.json())
# except:
#     print("Response Text:", response_delete.text)





import requests

# -------------------- CONFIG --------------------
AUTH_TOKEN = "nahhhh, never!!"

GET_HUBS_ENDPOINT = (
    "https://apx.aneeshprasobhan.xyz/hubs?"
    "org=LOAD TESTING&locale_info=LOAD TESTING BUILDING&floor=0&open_ground=false"
)

DELETE_HUB_ENDPOINT_BASE = "https://apx.aneeshprasobhan.xyz/hubs/"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AUTH_TOKEN}"
}
# -------------------------------------------------

# Step 1: Fetch hubs
print("[*] Fetching hub data...")

response = requests.get(GET_HUBS_ENDPOINT, headers=HEADERS)

if response.status_code != 200:
    print(f"❌ Failed to fetch hubs. Status code: {response.status_code}")
    print("Response:", response.text)
    exit()

response_json = response.json()
hubs = response_json.get("hubs", [])

if not hubs:
    print("⚠️ No hubs found.")
    exit()

print(f"✅ Found {len(hubs)} hubs to delete.")

# Step 2: Delete each hub by hubId
for hub in hubs:
    hub_id = hub.get("hubId")
    if not hub_id:
        print("❌ hubId missing in one of the entries. Skipping.")
        continue

    delete_url = DELETE_HUB_ENDPOINT_BASE + hub_id
    print(f"[*] Deleting hub: {hub_id}")

    delete_response = requests.delete(delete_url, headers=HEADERS)

    if delete_response.status_code in [200, 204]:
        print(f"✅ Successfully deleted {hub_id}")
    else:
        print(f"❌ Failed to delete {hub_id}. Status: {delete_response.status_code}")
        try:
            print("Response:", delete_response.json())
        except:
            print("Response Text:", delete_response.text)
