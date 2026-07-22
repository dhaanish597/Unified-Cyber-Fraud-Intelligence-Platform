import random

class VirtualBankModel:
    """
    Virtual Digital Bank Model for enterprise-scale simulation.
    Default bank: Fusion National Bank (Bank of Maharashtra / FinSpark PS2 Ecosystem).
    """
    def __init__(self, bank_name: str = "Fusion National Bank", bank_code: str = "FUSB"):
        self.bank_name = bank_name
        self.bank_code = bank_code
        self.ifsc_prefix = f"{bank_code}000"
        
        self.branches = [
            {"branch_code": "001", "name": "Nariman Point Main Branch", "city": "Mumbai", "ifsc": f"{self.ifsc_prefix}0001"},
            {"branch_code": "002", "name": "Connaught Place Central", "city": "Delhi", "ifsc": f"{self.ifsc_prefix}0002"},
            {"branch_code": "003", "name": "MG Road Digital Hub", "city": "Bangalore", "ifsc": f"{self.ifsc_prefix}0003"},
            {"branch_code": "004", "name": "Banjara Hills Corporate Branch", "city": "Hyderabad", "ifsc": f"{self.ifsc_prefix}0004"},
            {"branch_code": "005", "name": "GIFT City Special Branch", "city": "Ahmedabad", "ifsc": f"{self.ifsc_prefix}0005"}
        ]
        
        self.atm_terminals = [
            {"atm_id": "ATM_MUM_001", "city": "Mumbai", "location": "Fort Commercial Terminal", "type": "ON_US"},
            {"atm_id": "ATM_DEL_002", "city": "Delhi", "location": "CP Metro Station Terminal", "type": "ON_US"},
            {"atm_id": "ATM_BLR_003", "city": "Bangalore", "location": "Indiranagar 100ft Rd", "type": "OFF_US"},
            {"atm_id": "ATM_ATM_404", "city": "Mumbai", "location": "High-Risk Cash-Out Hub #4", "type": "OFF_US"}
        ]
        
        self.merchants = [
            {"merchant_id": "MERCH_AMZN_01", "name": "Amazon Retail India", "category": "E-COMMERCE", "risk_tier": "LOW"},
            {"merchant_id": "MERCH_SWIG_02", "name": "Swiggy Food Delivery", "category": "DINING", "risk_tier": "LOW"},
            {"merchant_id": "MERCH_PETRO_03", "name": "Indian Oil Fuel Station", "category": "FUEL", "risk_tier": "LOW"},
            {"merchant_id": "ACC_MERCHANT_99", "name": "Retail Supermarket Hub", "category": "RETAIL", "risk_tier": "LOW"},
            {"merchant_id": "ACC_ATM_404", "name": "Mule Cash-Out Terminal 404", "category": "MULE_RING", "risk_tier": "CRITICAL"}
        ]
        
        self.payment_gateways = ["UPI_NPCI", "NEFT_RBI", "RTGS_RBI", "IMPS_NCPI", "VISA_NET", "MASTERCARD_NET", "RUPAY_NET"]

    def get_random_branch(self) -> dict:
        return random.choice(self.branches)

    def get_random_merchant(self) -> dict:
        return random.choice(self.merchants)

    def to_dict(self) -> dict:
        return {
            "bank_name": self.bank_name,
            "bank_code": self.bank_code,
            "branches": len(self.branches),
            "atm_terminals": len(self.atm_terminals),
            "registered_merchants": len(self.merchants),
            "supported_gateways": self.payment_gateways
        }

default_bank = VirtualBankModel()
