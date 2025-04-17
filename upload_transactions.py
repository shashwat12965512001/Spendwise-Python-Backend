import json
import requests
import time

# Config
json_file = 'dummy.json'
endpoint = "https://shashwat.weblytechnolab.com/api/transactions/add"
delay_between_requests = 0.05  # 50ms to prevent server overload

# Load data
with open(json_file, 'r') as f:
    transactions = json.load(f)

total = len(transactions)
success = 0
failures = 0

for idx, txn in enumerate(transactions, start=1):
    try:
        response = requests.post(endpoint, json=txn)
        if response.status_code == 201:
            success += 1
        else:
            print(f"[{idx}] ❌ Failed: {response.status_code} - {response.text}")
            failures += 1
        time.sleep(delay_between_requests)  # Optional delay to throttle
    except Exception as e:
        print(f"[{idx}] ❌ Exception: {e}")
        failures += 1

print(f"\n✅ Upload complete! Success: {success}, Failed: {failures}, Total: {total}")
