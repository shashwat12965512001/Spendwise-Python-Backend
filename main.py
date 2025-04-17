import logging, json, os, http, requests
import subprocess
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)
path = f"{os.getcwd()}/"

load_dotenv()
DEPLOY_SECRET = os.getenv("DEPLOY_SECRET")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    filename=f"{path}newfile.log",
    format='%(asctime)s %(levelname)s %(message)s',
)

@app.route('/deploy', methods=['POST'])
def deploy():
    token = request.headers.get("X-DEPLOY-TOKEN")
    if token != DEPLOY_SECRET:
        return jsonify({"error": "Unauthorized"}), 403
    try:
        subprocess.run(["git", "pull"], cwd="/home/weblytechnolab-backend/htdocs/backend.weblytechnolab.com/Spendwise-Python-Backend/")
        subprocess.run(["sudo", "systemctl", "restart", "spendwise.service"])
        return jsonify({"status": "Updated & restarted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to fetch the receiver's name
def get_receivers_name(upi_id, auth_token, client_secret):
    """Fetch the receiver's name using UPI ID."""
    if not upi_id or not auth_token or not client_secret:
        raise ValueError("UPI ID, Auth Token, and Client Secret are required")

    conn = http.client.HTTPSConnection("production.deepvue.tech")
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'x-api-key': client_secret,
        'Content-Type': 'application/json'
    }

    try:
        conn.request("GET", f"/v1/verification/upi?vpa={upi_id}", headers=headers)
        res = conn.getresponse()
        if res.status != 200:
            raise Exception(f"Error {res.status}: {res.reason}")
        data = json.loads(res.read().decode("utf-8"))

        if "data" in data and "name_information" in data["data"]:
            return data["data"]["name_information"].get("name_at_bank_cleaned", "Unknown")
        else:
            raise ValueError("Invalid response structure")

    except Exception as e:
        print(f"Error fetching receiver's name: {e}")
        return None
    finally:
        conn.close()

# Function to fetch authentication token
def auth_token_api(client_id, client_secret):
    """Fetch authentication token using client credentials."""
    if not client_id or not client_secret:
        raise ValueError("Client ID and Client Secret are required")

    conn = http.client.HTTPSConnection("production.deepvue.tech")
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    payload = f"""--{boundary}\r\nContent-Disposition: form-data; name=client_id;\r\n\r\n{client_id}\r\n--{boundary}\r\nContent-Disposition: form-data; name=client_secret;\r\n\r\n{client_secret}\r\n--{boundary}--\r\n""".encode("utf-8")

    headers = {
        'Content-type': f'multipart/form-data; boundary={boundary}'
    }

    try:
        conn.request("POST", "/v1/authorize", body=payload, headers=headers)
        res = conn.getresponse()
        if res.status != 200:
            raise Exception(f"Error {res.status}: {res.reason}")
        data = json.loads(res.read().decode("utf-8"))
        return data.get("access_token")

    except Exception as e:
        print(f"Error fetching auth token: {e}")
        return None
    finally:
        conn.close()

def percent(part, whole):
    return (part * whole) / 100

# Function to extract amount, UPI ID, and category from a message body
def extract_transaction_details(message):
    try:
        map = {}
        words = message.split(" ")
        for i, val in enumerate(words):
            if val == "No" and ".Ref" in words[i - 1]:
                if "." in words[i + 1]:
                    map["transaction_id"] = words[i + 1].split(".")[0]
                elif ")" in words[i + 1]:
                    map["transaction_id"] = words[i + 1].split(")")[0]
                else:
                    map["transaction_id"] = words[i + 1]
            if (val == "UPI" or val == "(UPI") and words[i + 1] == "Ref" and words[i + 2] == "No":
                if "." in words[i + 3]:
                    map["transaction_id"] = words[i + 3].split(".")[0]
                elif ")" in words[i + 3]:
                    map["transaction_id"] = words[i + 3].split(")")[0]
                else:
                    map["transaction_id"] = words[i + 3]
            if val == "debited" and words[i - 2] == "Rs":
                map["amount"] = words[i - 1]
                map["category"] = "Expense"
            if val == "VPA" and "@" in words[i + 1]:
                if ".Ref" in words[i + 1]:
                    map["upi_id"] = words[i + 1].split(".")[0]
            if val == "Txn" and words[i + 1] == "No":
                if "." in words[i + 2]:
                    map["transaction_id"] = words[i + 2].split(".")[0]
                elif ")" in words[i + 2]:
                    map["transaction_id"] = words[i + 2].split(")")[0]
                else:
                    map["transaction_id"] = words[i + 2]
            if val == "credited" and words[i - 1] == "was" and words[i - 3] == "₹":
                map["amount"] = words[i - 2]
                map["category"] = "Income"
            if "INR" in val and words[i + 2] == "was" and words[i + 3] == "credited":
                map["amount"] = val[3:]
                map["category"] = "Income"
            if val == "INR" and words[i + 2] == "has" and words[i + 3] == "been" and words[i + 4] == "credited":
                map["amount"] = words[i + 1]
                map["category"] = "Income"

        return map
    except Exception as e:
        app.logger.error(f"Error extracting details: {e}")
        return {"amount": 0.0, "upi_id": "Error", "category": "Error"}

def assign_expense_type():
    pass

@app.route('/getSuggestions')
def getSuggestions():
    pass

@app.route('/getMonthlyBudget', methods=['POST'])
def get_monthly_budget():
    try:
        user_id = request.json.get('user_id')
        if not user_id:
            return {"error": "user_id is required"}, 400
        today = datetime.today()
        url = f"https://shashwat.weblytechnolab.com/api/transactions/yearly/{user_id}/{today.year}"
        response = requests.request("GET", url)

        if response.status_code == 200:
            data = response.json()
            transactions = data.get("transactions", {})
            with open("response.json", "w") as f:
                json.dump(transactions, f, indent=4)
            return {"transactions": transactions}
        else:
            return {"error": "Failed to fetch transactions", "status": response.status_code}, response.status_code
    except Exception as e:
        app.logger.error(f"Error in /getMonthlyBudget: {e}")
        return jsonify({"status": False, "message": str(e)}), 500

@app.route('/transactions', methods=['POST'])
def process_transactions():
    try:
        # Step 1: Parse request data
        data = request.get_json()
        transactions = data.get("transactions", [])

        if not transactions:
            return jsonify({"status": False, "message": "No transactions provided"}), 400

        # Step 2: Extract details for each transaction
        detailed_transactions = []
        for transaction in transactions:
            message = transaction.get("Message", "")
            details = extract_transaction_details(message)
            if details:
                transaction.update(details)  # Add extracted details to transaction
                detailed_transactions.append(transaction)

        with open(path + 'data.json', 'w') as f:
            f.write(json.dumps(detailed_transactions))

        # ================================================

        # # Client ID and Client Secret
        # client_id = "free_tier_shashwat_f528f71e9c"
        # client_secret = "a08fa2e82f164bb2ab31424dd59e913b"

        # # Get auth token
        # # access_token = auth_token_api(client_id, client_secret)
        # access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjMzMjg4OTQzMzYyNjM2MDk3IiwiaWF0IjoxNjY3NjI1MzM0LCJleHAiOjE2Njg3MjMzMzR9.Ec0YBxX8i5nZ7tMf7xYH3fHtXwKXHj6SgBx2KkXx1f8"

        # # Get data
        # file = open(path + 'data.json')
        # full_data = json.load(file)
        # # data = full_data[:500]  # Get only the first 500 records

        # # Step 3: Get receiver's name
        # if access_token:
        #     for transaction in full_data:
        #         if 'upi_id' in transaction:
        #             # name = get_receivers_name(transaction['upi_id'], access_token, client_secret)
        #             name = "Shashwat Srivastava"
        #             if name:
        #                 print(f"Receiver's Name: {name}")
        #                 transaction['name'] = name
        #                 transaction['expense_type'] = assign_expense_type(name)
        #             else:
        #                 print("Failed to retrieve receiver's name.")
        #         else:
        #             print("No UPI ID found in transaction.")
        # else:
        #     print("Failed to retrieve auth token.")

        # file.close()

        # ================================================

        # Step 4: Response
        response = {
            "status": True,
        }
        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"Error processing transactions: {e}")
        return jsonify({"status": False, "message": str(e)}), 500

@app.route('/')
def hello_world():
    return 'Hello from Spendwise.'

if __name__ == '__main__':
    app.run(debug=True, port=8090)
