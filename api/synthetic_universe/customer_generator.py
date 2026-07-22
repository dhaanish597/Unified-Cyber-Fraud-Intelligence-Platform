import random
import hashlib
from datetime import datetime, timedelta
from api.synthetic_universe.bank_model import default_bank

FIRST_NAMES = [
    "Rajesh", "Priya", "Amit", "Sunita", "Vikram", "Ananya", "Rohan", "Sneha", 
    "Karan", "Pooja", "Suresh", "Meera", "Deepak", "Kavita", "Sanjay", "Aarav", 
    "Diya", "Aditya", "Ishani", "Arjun", "Tanya", "Nitin", "Ritu", "Vivek"
]

LAST_NAMES = [
    "Kumar", "Sharma", "Patel", "Verma", "Rao", "Gupta", "Deshmukh", "Joshi", 
    "Singh", "Nair", "Chopra", "Reddy", "Mehta", "Iyer", "Kulkarni", "Bhatnagar", 
    "Banerjee", "Pillai", "Agarwal", "Saxena", "Shetty", "Thakur"
]

OCCUPATIONS = [
    {"title": "Software Principal Engineer", "income_range": (1200000, 4500000), "segment": "RETAIL"},
    {"title": "Corporate HR Director", "income_range": (1500000, 3800000), "segment": "RETAIL"},
    {"title": "Enterprise Business Owner", "income_range": (5000000, 25000000), "segment": "HNI"},
    {"title": "Investment Banking VP", "income_range": (2500000, 8500000), "segment": "HNI"},
    {"title": "Retail Chain Merchant", "income_range": (1000000, 9000000), "segment": "CORPORATE"},
    {"title": "Senior Medical Consultant", "income_range": (2000000, 12000000), "segment": "HNI"},
    {"title": "University Research Scholar", "income_range": (120000, 480000), "segment": "RETAIL"},
    {"title": "MSME Apparel Manufacturer", "income_range": (800000, 6000000), "segment": "MSME"},
    {"title": "Retired Central Govt Officer", "income_range": (400000, 1500000), "segment": "SENIOR_CITIZEN"}
]

CITIES_METRO = [
    {"city": "Mumbai", "state": "Maharashtra", "type": "URBAN"},
    {"city": "Delhi", "state": "Delhi NCR", "type": "URBAN"},
    {"city": "Bangalore", "state": "Karnataka", "type": "URBAN"},
    {"city": "Hyderabad", "state": "Telangana", "type": "URBAN"},
    {"city": "Ahmedabad", "state": "Gujarat", "type": "URBAN"},
    {"city": "Pune", "state": "Maharashtra", "type": "URBAN"},
    {"city": "Chennai", "state": "Tamil Nadu", "type": "URBAN"},
    {"city": "Kolkata", "state": "West Bengal", "type": "URBAN"}
]

CITIES_RURAL = [
    {"city": "Nashik", "state": "Maharashtra", "type": "RURAL"},
    {"city": "Anantapur", "state": "Andhra Pradesh", "type": "RURAL"},
    {"city": "Hubli", "state": "Karnataka", "type": "RURAL"},
    {"city": "Bhopal Outer", "state": "Madhya Pradesh", "type": "RURAL"}
]

KYC_STATUSES = ["VERIFIED TIER-1", "VERIFIED TIER-2", "VERIFIED TIER-3 (BIOMETRIC)", "PENDING_REKYC"]
CUSTOMER_RISK_TIERS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def generate_random_pan() -> str:
    letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
    digits = "".join(random.choices("0123456789", k=4))
    last = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{letters}{digits}{last}"

def generate_random_aadhaar() -> str:
    d = "".join(random.choices("0123456789", k=4))
    return f"XXXX-XXXX-{d}"

def generate_customer_profile(idx: int, seed: int = None) -> dict:
    """
    Generates a full enterprise customer profile with Accounts, Cards, Loans, Insurance & Habits.
    Part 2 & Part 3 of Digital Banking Universe.
    """
    if seed is not None:
        random.seed(seed + idx)

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    occ = random.choice(OCCUPATIONS)
    loc = random.choice(CITIES_METRO if random.random() > 0.15 else CITIES_RURAL)
    branch = default_bank.get_random_branch()

    user_id = f"usr_{idx:06d}"
    age = random.randint(22, 75) if occ["segment"] != "SENIOR_CITIZEN" else random.randint(62, 85)
    salary = random.randint(occ["income_range"][0], occ["income_range"][1])
    
    # Preserving exact demo shortcuts
    if idx == 0:
        user_id = "usr_abc"
        first = "Rajesh"
        last = "Kumar"
        loc = {"city": "Mumbai", "state": "Maharashtra", "type": "URBAN"}
        salary = 3600000
        age = 38

    pan = generate_random_pan()
    aadhaar = generate_random_aadhaar()
    kyc = "VERIFIED TIER-3 (BIOMETRIC)" if idx == 0 else random.choice(KYC_STATUSES)

    # PART 3: ACCOUNTS GENERATION
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
            "amb": float(round(main_balance * 0.85, 2)),
            "daily_limit": 500000.0,
            "single_tx_limit": 200000.0,
            "ifsc": branch["ifsc"],
            "opening_date": "2020-03-15",
            "status": "ACTIVE"
        },
        {
            "account_number": f"ACC_SAL_{user_id.upper()}",
            "type": "SALARY",
            "balance": float(round(salary / 12, 2)),
            "amb": float(round(salary / 12, 2)),
            "daily_limit": 1000000.0,
            "single_tx_limit": 500000.0,
            "ifsc": branch["ifsc"],
            "opening_date": "2020-03-15",
            "status": "ACTIVE"
        }
    ]

    # Add optional Corporate or Credit accounts
    if occ["segment"] in ["HNI", "CORPORATE", "MSME"]:
        accounts.append({
            "account_number": f"ACC_CORP_{user_id.upper()}",
            "type": "CORPORATE",
            "balance": float(round(random.uniform(1000000, 15000000), 2)),
            "amb": float(round(random.uniform(800000, 10000000), 2)),
            "daily_limit": 5000000.0,
            "single_tx_limit": 2500000.0,
            "ifsc": branch["ifsc"],
            "opening_date": "2021-06-01",
            "status": "ACTIVE"
        })

    # Cards & Loans
    cards = [
        {
            "card_number": f"4532-XXXX-XXXX-{random.randint(1000, 9999)}",
            "card_type": "DEBIT_VISA_PLATINUM",
            "linked_account": main_acc_num,
            "status": "ACTIVE",
            "expiry": "12/28"
        }
    ]
    if salary > 800000:
        cards.append({
            "card_number": f"5241-XXXX-XXXX-{random.randint(1000, 9999)}",
            "card_type": "CREDIT_MASTERCARD_WORLD",
            "credit_limit": float(round(salary * 0.2, 2)),
            "available_credit": float(round(salary * 0.18, 2)),
            "status": "ACTIVE",
            "expiry": "08/29"
        })

    loans = []
    if random.random() > 0.5:
        loans.append({
            "loan_id": f"LOAN_{user_id.upper()}_01",
            "type": "HOME_LOAN",
            "principal": 5000000.0,
            "outstanding": 3200000.0,
            "monthly_emi": 45000.0
        })

    insurance_policies = [
        {"policy_num": "POL_HEALTH_992", "type": "HEALTH_INSURANCE", "coverage": 1000000.0, "status": "ACTIVE"}
    ]

    beneficiaries = [
        {"beneficiary_id": f"BENEF_{random.randint(100, 999)}", "name": f"ACC_BENEF_{random.randint(100, 999)}", "bank": "HDFC Bank", "ifsc": "HDFC0000123"},
        {"beneficiary_id": f"BENEF_{random.randint(100, 999)}", "name": f"ACC_BENEF_{random.randint(100, 999)}", "bank": "State Bank of India", "ifsc": "SBIN0000456"}
    ]

    upi_id = f"{user_id}@fusb"

    risk_tier = "HIGH" if idx in [0, 1] else ("MEDIUM" if idx == 2 else random.choice(["LOW", "LOW", "LOW", "MEDIUM"]))

    # PART 7: CUSTOMER BEHAVIOR HABITS PROFILE
    behavior_profile = {
        "preferred_login_hours": [8, 9, 10, 11, 14, 15, 19, 20, 21],
        "salary_day_of_month": 1,
        "fuel_day_of_week": "Friday",
        "atm_frequency_days": 15,
        "avg_daily_tx_count": random.randint(2, 6),
        "typical_spending_category": "RETAIL_SHOPPING",
        "trusted_ip_subnets": [f"49.207.{random.randint(1, 20)}.0/24"],
        "primary_device_id": "dev_9999" if idx == 0 else f"dev_{idx:05d}"
    }

    return {
        "customer_id": user_id,
        "full_name": f"{first} {last}",
        "age": age,
        "occupation": occ["title"],
        "annual_salary": salary,
        "segment": occ["segment"],
        "kyc_status": kyc,
        "pan": pan,
        "aadhaar": aadhaar,
        "city": loc["city"],
        "state": loc["state"],
        "urban_rural": loc["type"],
        "home_branch": branch["name"],
        "ifsc": branch["ifsc"],
        "relationship_manager": f"RM_{random.randint(10, 99):02d}",
        "primary_account": main_acc_num,
        "accounts": accounts,
        "cards": cards,
        "loans": loans,
        "insurance_policies": insurance_policies,
        "beneficiaries": beneficiaries,
        "upi_id": upi_id,
        "risk_tier": risk_tier,
        "behavior_profile": behavior_profile
    }

def generate_customers_batch(count: int = 100, seed: int = 42) -> list:
    return [generate_customer_profile(i, seed=seed) for i in range(count)]

