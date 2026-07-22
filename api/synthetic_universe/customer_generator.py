import random
import hashlib
from datetime import datetime, timedelta
from api.synthetic_universe.bank_model import default_bank

FIRST_NAMES = ["Rajesh", "Priya", "Amit", "Sunita", "Vikram", "Ananya", "Rohan", "Sneha", "Karan", "Pooja", "Suresh", "Meera", "Deepak", "Kavita", "Sanjay"]
LAST_NAMES = ["Kumar", "Sharma", "Patel", "Verma", "Rao", "Gupta", "Deshmukh", "Joshi", "Singh", "Nair", "Chopra", "Reddy", "Mehta", "Iyer", "Kulkarni"]
OCCUPATIONS = [
    {"title": "Software Engineer", "income_range": (600000, 3500000), "segment": "RETAIL"},
    {"title": "Corporate HR Manager", "income_range": (800000, 2800000), "segment": "RETAIL"},
    {"title": "Business Owner", "income_range": (2000000, 15000000), "segment": "HNI"},
    {"title": "Bank Executive", "income_range": (1200000, 4500000), "segment": "RETAIL"},
    {"title": "Retail Merchant", "income_range": (500000, 5000000), "segment": "CORPORATE"},
    {"title": "Medical Consultant", "income_range": (1500000, 8000000), "segment": "HNI"},
    {"title": "University Student", "income_range": (60000, 300000), "segment": "RETAIL"}
]

CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Pune", "Chennai", "Kolkata"]

def generate_random_pan() -> str:
    letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
    digits = "".join(random.choices("0123456789", k=4))
    last = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{letters}{digits}{last}"

def generate_random_aadhaar() -> str:
    d = "".join(random.choices("0123456789", k=4))
    return f"XXXX-XXXX-{d}"

def generate_customer_profile(idx: int, seed: int = None) -> dict:
    if seed:
        random.seed(seed + idx)

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    occ = random.choice(OCCUPATIONS)
    city = random.choice(CITIES)
    branch = default_bank.get_random_branch()

    user_id = f"usr_{idx:06d}"
    age = random.randint(21, 68)
    salary = random.randint(occ["income_range"][0], occ["income_range"][1])
    
    # Predefined demo profiles for exact demo requirements
    if idx == 0:
        user_id = "usr_abc"
        first = "Rajesh"
        last = "Kumar"
        city = "Mumbai"
        salary = 3600000

    pan = generate_random_pan()
    aadhaar = generate_random_aadhaar()

    # Accounts generation
    main_acc_num = f"ACC_{user_id.upper()}_{random.randint(100, 999)}"
    main_balance = float(round(random.uniform(50000, salary * 0.8), 2))
    
    if idx == 0:
        main_acc_num = "ACC_ABC_123"
        main_balance = 1450000.00

    accounts = [
        {
            "account_number": main_acc_num,
            "type": "SAVINGS",
            "balance": main_balance,
            "ifsc": branch["ifsc"],
            "status": "ACTIVE"
        },
        {
            "account_number": f"ACC_SAL_{user_id.upper()}",
            "type": "SALARY",
            "balance": float(round(salary / 12, 2)),
            "ifsc": branch["ifsc"],
            "status": "ACTIVE"
        }
    ]

    upi_id = f"{user_id}@fusb"

    return {
        "customer_id": user_id,
        "full_name": f"{first} {last}",
        "age": age,
        "occupation": occ["title"],
        "annual_salary": salary,
        "segment": occ["segment"],
        "kyc_status": "VERIFIED TIER-3",
        "pan": pan,
        "aadhaar": aadhaar,
        "city": city,
        "home_branch": branch["name"],
        "ifsc": branch["ifsc"],
        "relationship_manager": f"RM_{random.randint(10, 99):02d}",
        "primary_account": main_acc_num,
        "accounts": accounts,
        "upi_id": upi_id,
        "risk_tier": "HIGH" if idx in [0, 1] else ("MEDIUM" if idx == 2 else "LOW")
    }

def generate_customers_batch(count: int = 100) -> list:
    return [generate_customer_profile(i) for i in range(count)]
