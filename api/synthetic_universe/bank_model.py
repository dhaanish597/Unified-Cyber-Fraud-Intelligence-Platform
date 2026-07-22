import random

class VirtualBankModel:
    """
    Virtual Digital Bank Model for enterprise-scale simulation.
    Supports multiple banks (e.g. Fusion National Bank, Global Commercial Bank, Apex Demo Bank).
    Part 1 of Digital Banking Universe.
    """
    def __init__(self, bank_name: str = "Fusion National Bank", bank_code: str = "FUSB"):
        self.bank_name = bank_name
        self.bank_code = bank_code
        self.ifsc_prefix = f"{bank_code}000"
        
        self.branches = [
            {"branch_code": "001", "name": "Nariman Point Main Branch", "city": "Mumbai", "ifsc": f"{self.ifsc_prefix}0001", "manager": "EMP_MGR_001", "zone": "WEST"},
            {"branch_code": "002", "name": "Connaught Place Central", "city": "Delhi", "ifsc": f"{self.ifsc_prefix}0002", "manager": "EMP_MGR_002", "zone": "NORTH"},
            {"branch_code": "003", "name": "MG Road Digital Hub", "city": "Bangalore", "ifsc": f"{self.ifsc_prefix}0003", "manager": "EMP_MGR_003", "zone": "SOUTH"},
            {"branch_code": "004", "name": "Banjara Hills Corporate Branch", "city": "Hyderabad", "ifsc": f"{self.ifsc_prefix}0004", "manager": "EMP_MGR_004", "zone": "SOUTH"},
            {"branch_code": "005", "name": "GIFT City Special Branch", "city": "Ahmedabad", "ifsc": f"{self.ifsc_prefix}0005", "manager": "EMP_MGR_005", "zone": "WEST"},
            {"branch_code": "006", "name": "Park Street Commercial", "city": "Kolkata", "ifsc": f"{self.ifsc_prefix}0006", "manager": "EMP_MGR_006", "zone": "EAST"},
            {"branch_code": "007", "name": "JM Road Retail Hub", "city": "Pune", "ifsc": f"{self.ifsc_prefix}0007", "manager": "EMP_MGR_007", "zone": "WEST"}
        ]
        
        self.atm_terminals = [
            {"atm_id": "ATM_MUM_001", "city": "Mumbai", "location": "Fort Commercial Terminal", "type": "ON_US", "daily_cash_limit": 500000.0, "status": "ONLINE"},
            {"atm_id": "ATM_DEL_002", "city": "Delhi", "location": "CP Metro Station Terminal", "type": "ON_US", "daily_cash_limit": 400000.0, "status": "ONLINE"},
            {"atm_id": "ATM_BLR_003", "city": "Bangalore", "location": "Indiranagar 100ft Rd", "type": "OFF_US", "daily_cash_limit": 300000.0, "status": "ONLINE"},
            {"atm_id": "ATM_HYD_004", "city": "Hyderabad", "location": "HITEC City IT Park", "type": "ON_US", "daily_cash_limit": 600000.0, "status": "ONLINE"},
            {"atm_id": "ATM_ATM_404", "city": "Mumbai", "location": "High-Risk Cash-Out Hub #4", "type": "OFF_US", "daily_cash_limit": 1000000.0, "status": "FLAGGED_RISK"}
        ]

        self.employees = [
            {"emp_id": "EMP_MGR_001", "name": "Vikramaditya Sen", "role": "BRANCH_MANAGER", "branch": "Nariman Point Main Branch", "access_level": "LEVEL_4"},
            {"emp_id": "EMP_RM_010", "name": "Ananya Kulkarni", "role": "RELATIONSHIP_MANAGER", "branch": "Nariman Point Main Branch", "access_level": "LEVEL_2"},
            {"emp_id": "EMP_RM_020", "name": "Rajiv Nambiar", "role": "RELATIONSHIP_MANAGER", "branch": "MG Road Digital Hub", "access_level": "LEVEL_2"},
            {"emp_id": "EMP_SOC_99", "name": "Pooja Deshmukh", "role": "FRAUD_ANALYST", "branch": "HQ SOC Center", "access_level": "ADMIN"},
            {"emp_id": "EMP_TELLER_402", "name": "Suresh Bhatia", "role": "TELLER_PRIVILEGED", "branch": "GIFT City Special Branch", "access_level": "LEVEL_3"}
        ]
        
        self.merchants = [
            {"merchant_id": "MERCH_AMZN_01", "name": "Amazon Retail India", "category": "E-COMMERCE", "risk_tier": "LOW", "mcc": "5311"},
            {"merchant_id": "MERCH_SWIG_02", "name": "Swiggy Food Delivery", "category": "DINING", "risk_tier": "LOW", "mcc": "5812"},
            {"merchant_id": "MERCH_PETRO_03", "name": "Indian Oil Fuel Station", "category": "FUEL", "risk_tier": "LOW", "mcc": "5541"},
            {"merchant_id": "MERCH_FLIP_04", "name": "Flipkart Digital Market", "category": "E-COMMERCE", "risk_tier": "LOW", "mcc": "5311"},
            {"merchant_id": "MERCH_MAKE_05", "name": "MakeMyTrip Travel Hub", "category": "TRAVEL", "risk_tier": "MEDIUM", "mcc": "4722"},
            {"merchant_id": "ACC_MERCHANT_99", "name": "Retail Supermarket Hub", "category": "RETAIL", "risk_tier": "LOW", "mcc": "5411"},
            {"merchant_id": "ACC_ATM_404", "name": "Mule Cash-Out Terminal 404", "category": "MULE_RING", "risk_tier": "CRITICAL", "mcc": "6011"}
        ]
        
        self.payment_gateways = ["UPI_NPCI", "NEFT_RBI", "RTGS_RBI", "IMPS_NCPI", "VISA_NET", "MASTERCARD_NET", "RUPAY_NET", "SWIFT_GLOBAL"]
        
        self.bank_limits = {
            "daily_upi_limit": 100000.0,
            "daily_neft_limit": 2500000.0,
            "daily_rtgs_min": 200000.0,
            "daily_rtgs_max": 100000000.0,
            "daily_atm_limit": 50000.0,
            "high_risk_tx_threshold": 500000.0
        }

    def get_random_branch(self) -> dict:
        return random.choice(self.branches)

    def get_random_merchant(self) -> dict:
        return random.choice(self.merchants)

    def get_random_employee(self) -> dict:
        return random.choice(self.employees)

    def to_dict(self) -> dict:
        return {
            "bank_name": self.bank_name,
            "bank_code": self.bank_code,
            "branches_count": len(self.branches),
            "atm_terminals_count": len(self.atm_terminals),
            "employees_count": len(self.employees),
            "registered_merchants": len(self.merchants),
            "supported_gateways": self.payment_gateways,
            "bank_limits": self.bank_limits,
            "branches": self.branches,
            "atms": self.atm_terminals
        }

# Supported Bank Registry
BANK_REGISTRY = {
    "FUSB": VirtualBankModel("Fusion National Bank", "FUSB"),
    "GLBB": VirtualBankModel("Global Commercial Bank", "GLBB"),
    "APEX": VirtualBankModel("Apex Digital Bank", "APEX")
}

default_bank = BANK_REGISTRY["FUSB"]

def get_virtual_bank(bank_code: str = "FUSB") -> VirtualBankModel:
    return BANK_REGISTRY.get(bank_code.upper(), default_bank)

