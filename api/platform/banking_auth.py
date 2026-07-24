from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
import uuid
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from api.store import delete, get, put

from .config import platform_settings
from .security import create_access_token


REFRESH_COLLECTION = "banking_refresh_tokens"
USER_COLLECTION = "banking_users"
PBKDF2_ITERATIONS = 310_000


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=8, max_length=256)
    device_id: str = Field(min_length=1, max_length=256)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=128)
    password: str = Field(min_length=8, max_length=256)
    email: str = Field(min_length=3, max_length=256)
    display_name: str = Field(min_length=1, max_length=256)
    phone: str = ""


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=512)
    device_id: str = Field(min_length=1, max_length=256)


class LogoutRequest(BaseModel):
    refresh_token: str | None = Field(default=None, max_length=512)


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    access_expires_at: int
    refresh_expires_at: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_token": self.access_token,
            "token_type": "Bearer",
            "expires_at": self.access_expires_at,
            "expires_in": max(0, self.access_expires_at - int(time.time())),
            "refresh_token": self.refresh_token,
            "refresh_expires_at": self.refresh_expires_at,
        }


def _token_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _password_hash(password: str, salt: bytes | None = None) -> str:
    actual_salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), actual_salt, PBKDF2_ITERATIONS
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${actual_salt.hex()}${digest.hex()}"


def _password_matches(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, expected_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(digest, bytes.fromhex(expected_hex))
    except (ValueError, TypeError):
        return False


class BankingAuthService:
    def __init__(self) -> None:
        self.refresh_ttl_seconds = int(
            os.getenv("BANK_REFRESH_TTL_SECONDS", str(30 * 24 * 60 * 60))
        )
        self._load_configured_users()

    def _load_configured_users(self) -> None:
        raw = os.getenv("FUSION_BANK_USERS_JSON")
        if raw:
            configured = json.loads(raw)
            if not isinstance(configured, list):
                raise RuntimeError("FUSION_BANK_USERS_JSON must contain a JSON array")
        elif platform_settings.security_mode == "production":
            raise RuntimeError("FUSION_BANK_USERS_JSON is required in production")
        else:
            configured = [
                {
                    "username": "demo_user",
                    "password": "FusionDemo!2026",
                    "user_id": "USR_DEMO_001",
                    "display_name": "Development Banking User",
                    "email": "demo.user@localhost.invalid",
                }
            ]
        for item in configured:
            username = str(item.get("username", "")).strip().lower()
            password = item.get("password")
            password_hash = item.get("password_hash")
            if not username or not (password or password_hash):
                raise RuntimeError("Each configured banking user needs username and password/hash")
            existing = get(USER_COLLECTION, username)
            record = {
                "username": username,
                "user_id": str(item.get("user_id") or f"USR_{uuid.uuid4().hex[:12].upper()}"),
                "display_name": str(item.get("display_name") or username),
                "email": str(item.get("email") or ""),
                "tenant_id": str(item.get("tenant_id") or "TENANT_FUSB_001"),
                "app_id": str(item.get("app_id") or "com.fusionbank.mobileapp"),
                "password_hash": str(password_hash or _password_hash(str(password))),
                "disabled": bool(item.get("disabled", False)),
                "phone": str(item.get("phone") or ""),
                "account_number": str(item.get("account_number") or f"FUS-{uuid.uuid4().hex[:12].upper()}"),
                "registered_devices": list(item.get("registered_devices") or []),
                "active_sessions": [],
                "transaction_history": list(item.get("transaction_history") or []),
                "known_locations": list(item.get("known_locations") or []),
                "known_networks": list(item.get("known_networks") or []),
                "known_beneficiaries": list(item.get("known_beneficiaries") or []),
                "security_preferences": dict(item.get("security_preferences") or {}),
                "notification_preferences": dict(item.get("notification_preferences") or {"email": True, "in_app": True}),
                "risk_profile": dict(item.get("risk_profile") or {}),
                "trust_profile": dict(item.get("trust_profile") or {}),
            }
            if existing and "password" not in item and not password_hash:
                record["password_hash"] = existing["password_hash"]
            put(USER_COLLECTION, username, record)

    @staticmethod
    def _public_profile(user: dict[str, Any]) -> dict[str, Any]:
        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "display_name": user["display_name"],
            "email": user["email"],
            "tenant_id": user["tenant_id"],
            "phone": user.get("phone", ""),
            "account_number": user.get("account_number"),
            "registered_devices": user.get("registered_devices", []),
            "active_sessions": user.get("active_sessions", []),
            "risk_profile": user.get("risk_profile", {}),
            "trust_profile": user.get("trust_profile", {}),
        }

    def authenticate(self, username: str, password: str) -> dict[str, Any]:
        user = get(USER_COLLECTION, username.strip().lower())
        stored_hash = user.get("password_hash", "") if user else _password_hash("invalid")
        if not user or user.get("disabled") or not _password_matches(password, stored_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        return user

    def _issue(self, user: dict[str, Any], device_id: str) -> TokenPair:
        client = {
            "roles": ["customer", "sdk"],
            "tenant_id": user["tenant_id"],
            "app_id": user["app_id"],
        }
        access_token, access_expires_at = create_access_token(
            f"banking:{user['user_id']}",
            client,
            subject=user["user_id"],
        )
        refresh_token = secrets.token_urlsafe(48)
        refresh_expires_at = int(time.time()) + self.refresh_ttl_seconds
        put(
            REFRESH_COLLECTION,
            _token_hash(refresh_token),
            {
                "user_id": user["user_id"],
                "username": user["username"],
                "device_id": device_id,
                "expires_at": refresh_expires_at,
                "issued_at": int(time.time()),
            },
        )
        return TokenPair(
            access_token,
            refresh_token,
            access_expires_at,
            refresh_expires_at,
        )

    def login(self, request: LoginRequest) -> tuple[TokenPair, dict[str, Any]]:
        user = self.authenticate(request.username, request.password)
        new_device = request.device_id not in user.get("registered_devices", [])
        if new_device:
            user.setdefault("registered_devices", []).append(request.device_id)
        user.setdefault("active_sessions", []).append({"device_id": request.device_id, "login_at": int(time.time()), "status": "ACTIVE"})
        put(USER_COLLECTION, user["username"], user)
        profile = self._public_profile(user)
        profile["new_device"] = new_device
        return self._issue(user, request.device_id), profile

    def register(self, request: RegisterRequest) -> dict[str, Any]:
        username = request.username.strip().lower()
        if get(USER_COLLECTION, username):
            raise HTTPException(status_code=409, detail="Username is already registered")
        user = {
            "username": username, "user_id": f"USR_{uuid.uuid4().hex[:12].upper()}",
            "display_name": request.display_name, "email": request.email, "phone": request.phone,
            "tenant_id": "TENANT_FUSB_001", "app_id": "com.fusionbank.mobileapp",
            "password_hash": _password_hash(request.password), "disabled": False,
            "registered_devices": [], "active_sessions": [], "transaction_history": [],
            "known_locations": [], "known_networks": [], "known_beneficiaries": [],
            "security_preferences": {}, "notification_preferences": {"email": True, "in_app": True},
            "risk_profile": {}, "trust_profile": {},
        }
        put(USER_COLLECTION, username, user)
        return self._public_profile(user)

    def refresh(self, request: RefreshRequest) -> tuple[TokenPair, dict[str, Any]]:
        key = _token_hash(request.refresh_token)
        record = get(REFRESH_COLLECTION, key)
        if (
            not record
            or record.get("device_id") != request.device_id
            or int(record.get("expires_at", 0)) <= int(time.time())
        ):
            delete(REFRESH_COLLECTION, key)
            raise HTTPException(status_code=401, detail="Refresh token is invalid or expired")
        user = get(USER_COLLECTION, record["username"])
        if not user or user.get("disabled"):
            delete(REFRESH_COLLECTION, key)
            raise HTTPException(status_code=401, detail="Banking user is unavailable")
        delete(REFRESH_COLLECTION, key)
        return self._issue(user, request.device_id), self._public_profile(user)

    def logout(self, refresh_token: str | None) -> None:
        if refresh_token:
            delete(REFRESH_COLLECTION, _token_hash(refresh_token))

    def profile_for_subject(self, subject: str) -> dict[str, Any]:
        # User count is deliberately small in the reference deployment. A
        # username index can replace this lookup for a larger identity store.
        from api.store import list_all

        user = next(
            (item for item in list_all(USER_COLLECTION) if item.get("user_id") == subject),
            None,
        )
        if not user or user.get("disabled"):
            raise HTTPException(status_code=404, detail="Banking profile not found")
        return self._public_profile(user)


banking_auth = BankingAuthService()
router = APIRouter(prefix="/banking", tags=["Banking Authentication"])


@router.post("/auth/login")
async def login(payload: LoginRequest):
    pair, profile = banking_auth.login(payload)
    from api.platform.notifications import notification_service
    if profile.get("new_device"):
        notification_service.create(
            user_id=profile["user_id"], device_id=payload.device_id,
            kind="NEW_DEVICE_LOGIN", severity="WARNING",
            message=f"We detected a login from a new device ({payload.device_id}).",
        )
        from api.platform.events import platform_event_broker
        await platform_event_broker.publish({
            "msg_type": "security_notification",
            "event_type": "NEW_DEVICE_LOGIN",
            "user_id": profile["user_id"],
            "device_id": payload.device_id,
            "severity": "WARNING",
        })
    return {**pair.to_dict(), "profile": profile}


@router.post("/auth/register", status_code=201)
async def register(payload: RegisterRequest):
    return banking_auth.register(payload)


@router.post("/auth/refresh")
async def refresh(payload: RefreshRequest):
    pair, profile = banking_auth.refresh(payload)
    return {**pair.to_dict(), "profile": profile}


@router.post("/auth/logout", status_code=204)
async def logout(payload: LogoutRequest):
    banking_auth.logout(payload.refresh_token)
    return None


@router.get("/profile")
async def profile(request: Request):
    return banking_auth.profile_for_subject(request.state.auth.subject)
