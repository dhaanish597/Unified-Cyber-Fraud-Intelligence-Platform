import time
import datetime
import random
from typing import Dict, List, Any

# CRYPTO ASSET INVENTORY DATABASE (MODULE 3)
INVENTORY_DATABASE = [
    {
        "id": "ASSET_001",
        "name": "Core Banking CBS Gateway TLS",
        "type": "API Endpoint",
        "public_key_algo": "RSA-2048",
        "key_exchange": "ECDHE_RSA",
        "digital_signature": "RSA-PSS-SHA256",
        "tls_version": "TLS 1.3",
        "cert_expiry_days": 88,
        "crypto_library": "OpenSSL 3.1.2",
        "pqc_status": "HYBRID_READY",
        "quantum_risk": "HIGH_LONG_TERM",
        "agility_status": "PARTIALLY_ENABLED"
    },
    {
        "id": "ASSET_002",
        "name": "SWIFT Financial Messaging Node",
        "type": "Service",
        "public_key_algo": "RSA-4096",
        "key_exchange": "ECDHE_RSA",
        "digital_signature": "RSA-PSS-SHA512",
        "tls_version": "TLS 1.3",
        "cert_expiry_days": 210,
        "crypto_library": "BouncyCastle 1.74",
        "pqc_status": "PQC_MIGRATION_REQUIRED",
        "quantum_risk": "HIGH_LONG_TERM",
        "agility_status": "ENABLED"
    },
    {
        "id": "ASSET_003",
        "name": "UPI Payment Gateway Auth Token Issuer",
        "type": "Key Management",
        "public_key_algo": "ECDSA P-256",
        "key_exchange": "ECDH_P256",
        "digital_signature": "ECDSA-SHA256",
        "tls_version": "TLS 1.3",
        "cert_expiry_days": 42,
        "crypto_library": "OpenSSL 3.0.8",
        "pqc_status": "CRITICAL_VULNERABLE",
        "quantum_risk": "HIGH_LONG_TERM",
        "agility_status": "PARTIALLY_ENABLED"
    },
    {
        "id": "ASSET_004",
        "name": "HSM Core Evidence Key Manager Node 01",
        "type": "Hardware Security Module",
        "public_key_algo": "ML-KEM-768 (Kyber)",
        "key_exchange": "ML-KEM-768 + ECDHE",
        "digital_signature": "ML-DSA-3 (Dilithium)",
        "tls_version": "TLS 1.3 PQC",
        "cert_expiry_days": 365,
        "crypto_library": "liboqs 0.9.0",
        "pqc_status": "QUANTUM_RESISTANT",
        "quantum_risk": "QUANTUM_RESISTANT",
        "agility_status": "ENABLED"
    },
    {
        "id": "ASSET_005",
        "name": "Legacy ATM Batch Clearing System",
        "type": "Application",
        "public_key_algo": "RSA-1024",
        "key_exchange": "RSA_STATIC",
        "digital_signature": "RSA-SHA1",
        "tls_version": "TLS 1.2",
        "cert_expiry_days": 14,
        "crypto_library": "OpenSSL 1.0.2u",
        "pqc_status": "LEGACY_DEPRECATED",
        "quantum_risk": "CRITICAL_IMMEDIATE",
        "agility_status": "LEGACY"
    }
]

class QuantumTrustEngine:
    """
    Fusion Quantum Trust Layer (QTL) Engine.
    Provides Cryptographic Posture Assessment, Quantum Risk Analysis, Crypto Inventory, 
    Quantum Readiness Scoring, Crypto Agility Evaluation, Migration Recommendations, and Impact Simulation.
    """
    def __init__(self):
        self.inventory: List[dict] = INVENTORY_DATABASE
        self.assessment_cache: dict = {}

    def get_readiness_score(self) -> dict:
        """
        Module 4 & 5: Computes Quantum Readiness Score (0-100) and Crypto Agility Status.
        """
        total_assets = len(self.inventory)
        quantum_resistant_count = sum(1 for a in self.inventory if a["pqc_status"] == "QUANTUM_RESISTANT")
        legacy_count = sum(1 for a in self.inventory if a["quantum_risk"] == "CRITICAL_IMMEDIATE")
        high_risk_count = sum(1 for a in self.inventory if a["quantum_risk"] == "HIGH_LONG_TERM")
        cert_expiring_90d = sum(1 for a in self.inventory if a["cert_expiry_days"] <= 90)

        # Score calculation formula
        base_score = 75.0
        base_score += (quantum_resistant_count / total_assets) * 20.0
        base_score -= (legacy_count / total_assets) * 25.0
        base_score -= (cert_expiring_90d / total_assets) * 10.0

        readiness_score = round(max(10.0, min(98.5, base_score)), 1)

        if readiness_score >= 90:
            readiness_level = "EXCELLENT"
        elif readiness_score >= 75:
            readiness_level = "GOOD"
        elif readiness_score >= 60:
            readiness_level = "MODERATE"
        elif readiness_score >= 40:
            readiness_level = "NEEDS_ATTENTION"
        else:
            readiness_level = "CRITICAL"

        return {
            "readiness_score": readiness_score,
            "readiness_level": readiness_level,
            "crypto_agility_status": "PARTIALLY_ENABLED",
            "total_crypto_assets": total_assets,
            "quantum_resistant_assets": quantum_resistant_count,
            "legacy_deprecated_assets": legacy_count,
            "high_risk_assets": high_risk_count,
            "certificates_expiring_90d": cert_expiring_90d,
            "pqc_adoption_percent": round((quantum_resistant_count / total_assets) * 100.0, 1),
            "assessment_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        }

    def get_inventory(self) -> List[dict]:
        """
        Module 3: Returns searchable crypto asset inventory.
        """
        return self.inventory

    def get_assessment(self) -> dict:
        """
        Module 1 & 2: Returns detailed cryptographic security posture assessment.
        """
        readiness = self.get_readiness_score()
        return {
            "readiness_summary": readiness,
            "cryptographic_profile": {
                "active_tls_version": "TLS 1.3 (Hybrid PQC Enabled)",
                "default_key_exchange": "ECDHE_RSA-2048 & ML-KEM-768 Dual-Handshake",
                "digital_signature_suite": "RSA-PSS-SHA256 & ML-DSA-3 Hybrid",
                "symmetric_encryption": "AES-256-GCM (Grover Resistant)",
                "hash_function": "SHA-256 / SHA-512 (Collision Resistant)",
                "pqc_library_provider": "liboqs v0.9.0 + OpenSSL 3.1.2"
            },
            "risk_distribution": [
                {"risk": "Critical (Immediate Action)", "count": 1, "color": "#EF4444"},
                {"risk": "High (Long-Term Quantum Threat)", "count": 3, "color": "#F59E0B"},
                {"risk": "Low (Symmetric/Hash Grover Resistant)", "count": 0, "color": "#3B82F6"},
                {"risk": "Quantum Resistant (NIST PQC Standard)", "count": 1, "color": "#10B981"}
            ]
        }

    def analyze_asset(self, asset_id: str) -> dict:
        """
        Analyzes a specific asset for quantum vulnerability.
        """
        asset = next((a for a in self.inventory if a["id"] == asset_id), self.inventory[0])
        return {
            "asset": asset,
            "vulnerability_analysis": {
                "shors_algorithm_risk": "VULNERABLE (Factoring/Discrete Log)" if "RSA" in asset["public_key_algo"] or "ECD" in asset["public_key_algo"] else "QUANTUM_RESISTANT",
                "grovers_algorithm_risk": "MITIGATED (AES-256 key length sufficient)",
                "crqc_estimated_timeline": "2030-2035 (Estimated Cryptographically Relevant Quantum Computer)",
                "recommended_pqc_replacement": "ML-KEM-768 (Kyber)" if "RSA" in asset["public_key_algo"] else "ML-DSA-3 (Dilithium)"
            }
        }

    def get_recommendations(self) -> List[dict]:
        """
        Module 6: Actionable PQC Migration Recommendations.
        """
        return [
            {
                "id": "REC_001",
                "title": "Migrate Core Banking Gateway from RSA-2048 to ML-KEM-768 Hybrid",
                "priority": "HIGH",
                "target_system": "Core Banking CBS Gateway TLS (ASSET_001)",
                "action": "Deploy hybrid ECDHE + ML-KEM-768 TLS 1.3 key exchange to secure against Harvest-Now-Decrypt-Later (HNDL) attacks.",
                "estimated_complexity": "MEDIUM",
                "estimated_time_days": 45,
                "business_impact": "LOW (Zero downtime backward-compatible fallback)",
                "security_benefit": "Eliminates long-term CRQC decryption risk for sensitive banking session payloads."
            },
            {
                "id": "REC_002",
                "title": "Deprecate Legacy ATM RSA-1024 Clearing Certificate",
                "priority": "CRITICAL",
                "target_system": "Legacy ATM Batch Clearing System (ASSET_005)",
                "action": "Immediately revoke SHA-1 / RSA-1024 certificate and upgrade to RSA-4096 / AES-256-GCM.",
                "estimated_complexity": "HIGH",
                "estimated_time_days": 14,
                "business_impact": "MODERATE (Requires ATM firmware batch update)",
                "security_benefit": "Removes active cryptographic collision and weak key risk."
            },
            {
                "id": "REC_003",
                "title": "Transition SWIFT Signatures to NIST ML-DSA-3 (Dilithium)",
                "priority": "MEDIUM",
                "target_system": "SWIFT Financial Messaging Node (ASSET_002)",
                "action": "Upgrade HSM firmware to support ML-DSA-3 dual digital signing on high-value wire transfers.",
                "estimated_complexity": "MEDIUM",
                "estimated_time_days": 60,
                "business_impact": "LOW (Parallel signature verification enabled)",
                "security_benefit": "Guarantees post-quantum signature non-repudiation for international wire settlements."
            }
        ]

    def get_dashboard_summary(self) -> dict:
        """
        Module 8: Compliance & Security Posture Dashboard Payload.
        """
        readiness = self.get_readiness_score()
        assessment = self.get_assessment()
        recs = self.get_recommendations()

        return {
            "readiness": readiness,
            "assessment": assessment,
            "recommendations_count": len(recs),
            "compliance_standards": {
                "nist_pqc_standardization": "FIPS 203 (ML-KEM) & FIPS 204 (ML-DSA) Aligned",
                "rbi_cyber_security_framework": "COMPLIANT (Crypto Inventory Maintained)",
                "cert_in_quantum_preparedness": "IN_PROGRESS (Stage 2 Crypto-Agility Deployment)"
            }
        }

    def get_compliance_details(self) -> dict:
        return self.get_dashboard_summary()

    def simulate_quantum_scenario(self, scenario_data: dict) -> dict:
        """
        Module 7: Educational Quantum Threat Impact Simulator.
        """
        target_asset_id = scenario_data.get("asset_id", "ASSET_001")
        scenario_year = scenario_data.get("simulated_year", 2032)
        asset = next((a for a in self.inventory if a["id"] == target_asset_id), self.inventory[0])

        is_pqc = asset["pqc_status"] == "QUANTUM_RESISTANT"

        return {
            "simulation_id": f"SIM_Q_{random.randint(1000, 9999)}",
            "simulated_year": scenario_year,
            "target_asset": asset["name"],
            "current_algorithm": asset["public_key_algo"],
            "quantum_threat_result": {
                "shor_factoring_time_minutes": "IMMUNE" if is_pqc else "12.4 Minutes (Simulated CRQC 10,000 Qubits)",
                "payload_compromise_risk": "NONE (PQC Shield Active)" if is_pqc else "HIGH (HNDL Harvest-Now-Decrypt-Later Risk)",
                "business_risk": "SAFE" if is_pqc else "CRITICAL (Financial Session Replay Vulnerability)"
            },
            "recommended_migration_path": {
                "target_algorithm": "ML-KEM-1024 / ML-DSA-5",
                "estimated_migration_cost_inr": "INR 4,50,000.00",
                "recommended_completion_date": f"{scenario_year - 3}-12-31"
            },
            "disclaimer": "This is an educational architectural simulation for Post-Quantum Cryptography planning. No live cryptographic keys were altered."
        }

quantum_trust = QuantumTrustEngine()
