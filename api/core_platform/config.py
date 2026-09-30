from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any


def _csv(name: str, default: str = "") -> tuple[str, ...]:
    return tuple(item.strip() for item in os.getenv(name, default).split(",") if item.strip())


def _clients(mode: str) -> dict[str, dict[str, Any]]:
    raw = os.getenv("FUSION_AUTH_CLIENTS_JSON")
    if raw:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise RuntimeError("FUSION_AUTH_CLIENTS_JSON must contain a JSON object")
        return parsed
    return {}


def configured_sdk_client() -> tuple[str, dict[str, Any]]:
    """Resolve a tenant-scoped SDK client for one-time device pairing."""
    explicit = next(
        (
            (client_id, item)
            for client_id, item in platform_settings.clients.items()
            if "sdk" in set(item.get("roles", []))
        ),
        None,
    )
    if explicit:
        return explicit
    tenant_id = os.getenv("FUSION_DEFAULT_TENANT_ID", "").strip()
    if not tenant_id:
        raise RuntimeError("No tenant is configured for device pairing")
    return "pairing-sdk", {
        "roles": ["sdk"],
        "permissions": ["*"],
        "tenant_id": tenant_id,
        "app_id": os.getenv("FUSION_DEFAULT_APP_ID", "com.fusionbank.mobileapp"),
    }


@dataclass(frozen=True)
class PlatformSettings:
    environment: str = field(default_factory=lambda: os.getenv("FUSION_ENV", "development").lower())
    security_mode: str = field(
        default_factory=lambda: os.getenv("FUSION_SECURITY_MODE", "development").lower()
    )
    jwt_issuer: str = field(default_factory=lambda: os.getenv("JWT_ISSUER", "fusion-risk-os"))
    jwt_audience: str = field(default_factory=lambda: os.getenv("JWT_AUDIENCE", "fusion-platform"))
    jwt_ttl_seconds: int = field(default_factory=lambda: int(os.getenv("JWT_TTL_SECONDS", "900")))
    jwt_secret: str = field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET", "")
    )
    cors_origins: tuple[str, ...] = field(
        default_factory=lambda: _csv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
    )
    # Tenant/app scope applied to clients that don't declare their own. Every
    # authenticated route requires a tenant, so a client configured with only a
    # secret and roles would otherwise mint tokens that fail validation.
    default_tenant_id: str = field(
        default_factory=lambda: os.getenv("FUSION_DEFAULT_TENANT_ID", "TENANT_FUSB_001")
    )
    default_app_id: str = field(
        default_factory=lambda: os.getenv("FUSION_DEFAULT_APP_ID", "com.fusionbank.mobileapp")
    )
    neo4j_uri: str | None = field(default_factory=lambda: os.getenv("NEO4J_URI"))
    neo4j_username: str | None = field(default_factory=lambda: os.getenv("NEO4J_USERNAME"))
    neo4j_password: str | None = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD"))
    graph_fallback_enabled: bool = field(
        default_factory=lambda: os.getenv("GRAPH_FALLBACK_ENABLED", "true").lower() == "true"
    )
    clients: dict[str, dict[str, Any]] = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "clients", _clients(self.security_mode))
        if self.security_mode not in {"development", "production"}:
            raise RuntimeError("FUSION_SECURITY_MODE must be development or production")
        if self.security_mode == "production":
            if len(self.jwt_secret.encode("utf-8")) < 32:
                raise RuntimeError("JWT_SECRET_KEY must contain at least 32 bytes in production")
            if not self.clients:
                raise RuntimeError("FUSION_AUTH_CLIENTS_JSON is required in production")
            if not self.cors_origins:
                raise RuntimeError("CORS_ORIGINS is required in production")
            if any(origin == "*" for origin in self.cors_origins):
                raise RuntimeError("Wildcard CORS is forbidden in production")


def validate_environment() -> None:
    """Fail closed when security-critical runtime configuration is absent."""
    jwt_secret = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET", "")
    required_values = {
        "JWT_SECRET_KEY": jwt_secret,
        "DATABASE_URL": os.getenv("DATABASE_URL", ""),
        "FUSION_BANK_USERS_JSON": os.getenv("FUSION_BANK_USERS_JSON", ""),
    }
    missing = [name for name, value in required_values.items() if not value.strip()]
    if jwt_secret == "change_me_in_production":
        missing.append("JWT_SECRET_KEY must not use the default value")
    if jwt_secret and len(jwt_secret.encode("utf-8")) < 32:
        missing.append("JWT_SECRET_KEY must contain at least 32 bytes")
    try:
        users = json.loads(os.getenv("FUSION_BANK_USERS_JSON", "{}"))
        if not isinstance(users, (dict, list)) or not users:
            missing.append("FUSION_BANK_USERS_JSON must contain at least one user")
        else:
            values = users.values() if isinstance(users, dict) else users
            invalid = any(
                not isinstance(value, dict)
                or not str(value.get("password") or value.get("password_hash") or "").strip()
                or value.get("password") == "PLACEHOLDER"
                for value in values
            )
            if invalid:
                missing.append("FUSION_BANK_USERS_JSON contains a blank or placeholder password")
    except json.JSONDecodeError:
        missing.append("FUSION_BANK_USERS_JSON must be valid JSON")
    if missing:
        raise RuntimeError("Invalid security environment: " + "; ".join(missing))


platform_settings = PlatformSettings()
