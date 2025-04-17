import json
import random
from datetime import datetime, timedelta

# Config
num_records = 10000  # Adjust as needed
output_file = 'dummy.json'

# Sample data
banks = [
    "FEDBNK", "HDFCBK", "SBIN", "ICICIBK", "AXISBK", "KOTAKBK", "PNBBK", 
    "IDFCBK", "YESBANK", "CANBK", "BOIBK", "UNIONBK", "BOMBK", "UCOBK"
]
names = [
    "Shashwat Srivastava", "Rahul Verma", "Priya Sharma", "Amit Patel", "Neha Gupta",
    "Vikram Mehta", "Sneha Joshi", "Aditya Rao", "Karan Malhotra", "Deepika Singh",
    "Rohan Khanna", "Anjali Sinha", "Siddharth Desai", "Ishika Chawla", "Aarav Bhatia",
    "Tanvi Kapoor", "Manish Agarwal", "Sakshi Jain", "Harsh Vardhan", "Riya Sen",
    "Aakash Tyagi", "Madhur Mittal", "Simran Kaur", "Arjun Thakur", "Pooja Iyer"
]
upi_ids = [
    "adsiddhu69@axl", "rahul123@okhdfcbank", "priya.s@okaxis", "amit.p@okicici", 
    "neha.g@okpaytm", "vikram.m@okkotak", "sneha.j@okyesbank", "aditya.r@okicici", 
    "karan.m@oksbi", "deepika.s@okhdfcbank", "rohan.k@okaxis", "anjali.s@okicici", 
    "siddharth.d@okkotak", "ishika.c@okhdfcbank", "aarav.b@okaxis", 
    "tanvi.k@okpaytm", "manish.a@okyesbank", "sakshi.j@okkotak", "harsh.v@okicici",
    "riya.s@okhdfcbank", "aakash.t@okaxis", "madhur.m@okpaytm", "simran.k@okicici",
    "arjun.t@okkotak", "pooja.i@okyesbank"
]
expense_types = ["Health", "Food", "Travel", "Shopping", "Entertainment", "Bills", "Education"]
categories = ["Expense", "Income"]

# Dummy user_ids (e.g., 10 test users)
user_ids = [f"user_{i}" for i in range(1, 11)]

# Generator
def generate_transaction(record_id):
    bank = random.choice(banks)
    receiver_name = random.choice(names)
    upi_id = random.choice(upi_ids)
    expense_type = random.choice(expense_types)
    category = random.choice(categories)
    amount = round(random.uniform(50, 5000), 2)
    transaction_id = str(500000000000 + record_id)
    date_time = datetime.now() - timedelta(days=random.randint(0, 365), minutes=random.randint(0, 1440))
    date_iso = date_time.isoformat()
    message_date = date_time.strftime("%d-%m-%Y %H:%M:%S")
    user_id = random.choice(user_ids)

    return {
        "name": f"VM-{bank}",
        "date": date_iso,  # ISO 8601 (Mongo will parse this as Date)
        "amount": amount,
        "category": category,
        "expense_type": expense_type,
        "user_id": user_id,
        "upi_id": upi_id,
        "transaction_id": transaction_id,
        "message": f"Rs {amount} debited via UPI on {message_date} to VPA {upi_id}.Ref No {transaction_id}.",
        "receiver_name": receiver_name,
        "address": f"VM-{bank}"
    }

# Generate
transactions = [generate_transaction(i) for i in range(1, num_records + 1)]

# Save
with open(output_file, 'w') as file:
    json.dump(transactions, file, indent=4)

print(f"✅ Generated {num_records} transactions → {output_file}")
