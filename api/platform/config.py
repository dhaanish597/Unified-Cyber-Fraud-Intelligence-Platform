from __future__ import annotations

import json
import os
import secrets
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
    if mode == "production":
        return {}
    return {
        "fusion-dashboard-dev": {
            "secret": "fusion-dashboard-local-only",
            "roles": ["analyst", "operator", "developer"],
        },
        "fusion-android-dev": {
            "secret": "fusion-android-local-only",
            "roles": ["sdk"],
            "tenant_id": "TENANT_FUSB_001",
            "app_id": "com.fusionbank.mobileapp",
        },
        "fusion-test": {
            "secret": "fusion-test-local-only",
            "roles": ["admin", "analyst", "operator", "developer", "sdk"],
        },
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
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET") or secrets.token_urlsafe(48))
    cors_origins: tuple[str, ...] = field(
        default_factory=lambda: _csv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
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
                raise RuntimeError("JWT_SECRET must contain at least 32 bytes in production")
            if not self.clients:
                raise RuntimeError("FUSION_AUTH_CLIENTS_JSON is required in production")
            if not self.cors_origins:
                raise RuntimeError("CORS_ORIGINS is required in production")
            if any(origin == "*" for origin in self.cors_origins):
                raise RuntimeError("Wildcard CORS is forbidden in production")


platform_settings = PlatformSettings()
