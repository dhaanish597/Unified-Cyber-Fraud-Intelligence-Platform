from __future__ import annotations

import hashlib
import secrets
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class PairingRecord:
    pair_id: str
    bootstrap_token_hash: str
    backend_url: str
    ws_url: str
    expires_at: float
    created_at: float
    used: bool = False

    def payload(self) -> dict[str, Any]:
        return {
            "backend": self.backend_url,
            "ws": self.ws_url,
            "pairId": self.pair_id,
            "bootstrapToken": None,
            "expires": datetime.fromtimestamp(self.expires_at, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        }


class PairingRegistry:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self.records: dict[str, PairingRecord] = {}
        self.devices: dict[str, dict[str, Any]] = {}

    def _purge(self) -> None:
        now = time.time()
        self.records = {key: value for key, value in self.records.items() if value.expires_at > now}

    def create(self, backend_url: str, ws_url: str) -> dict[str, Any]:
        self._purge()
        pair_id = f"PAIR_{secrets.token_hex(3).upper()}"
        token = secrets.token_urlsafe(24)
        record = PairingRecord(
            pair_id=pair_id,
            bootstrap_token_hash=hashlib.sha256(token.encode()).hexdigest(),
            backend_url=backend_url.rstrip("/"),
            ws_url=ws_url.rstrip("/"),
            expires_at=time.time() + self.ttl_seconds,
            created_at=time.time(),
        )
        self.records[pair_id] = record
        payload = record.payload()
        payload["bootstrapToken"] = token
        return {"pairing": payload, "pair_id": pair_id, "expires_in": self.ttl_seconds}

    def consume(self, pair_id: str, token: str) -> PairingRecord | None:
        self._purge()
        record = self.records.get(pair_id)
        if not record or record.used or record.expires_at <= time.time():
            return None
        supplied = hashlib.sha256(token.encode()).hexdigest()
        if not secrets.compare_digest(supplied, record.bootstrap_token_hash):
            return None
        record.used = True
        return record

    def register_device(self, pair_id: str, data: dict[str, Any]) -> dict[str, Any]:
        device_id = data.get("device_uuid") or data.get("device_id") or f"DEV_{uuid.uuid4().hex[:10].upper()}"
        device = {
            "device_id": device_id,
            "device_uuid": device_id,
            "pair_id": pair_id,
            "android_version": data.get("android_version"),
            "manufacturer": data.get("manufacturer"),
            "model": data.get("model"),
            "sdk_version": data.get("sdk_version"),
            "app_version": data.get("app_version"),
            "fingerprint": data.get("fingerprint"),
            "status": "CONNECTED",
            "kind": "LIVE_DEVICE",
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "last_seen": datetime.now(timezone.utc).isoformat(),
        }
        self.devices[device_id] = device
        return device

    def list_devices(self) -> list[dict[str, Any]]:
        return list(self.devices.values())


pairing_registry = PairingRegistry()
