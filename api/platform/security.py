from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, Request, WebSocket, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from .config import PlatformSettings, platform_settings


PUBLIC_PATHS = {
    "/health/live",
    "/health/ready",
    "/auth/token",
    "/gateway/webhook",
}


ROLE_POLICIES: tuple[tuple[str, frozenset[str]], ...] = (
    ("/sdk/", frozenset({"sdk", "developer", "admin"})),
    ("/synthetic/", frozenset({"developer", "admin"})),
    ("/response/", frozenset({"operator", "admin"})),
    ("/playbook", frozenset({"operator", "admin"})),
    ("/incident/", frozenset({"operator", "admin"})),
    ("/evidence/", frozenset({"analyst", "operator", "admin"})),
    ("/audit/", frozenset({"analyst", "operator", "admin"})),
    ("/trust/", frozenset({"analyst", "operator", "sdk", "admin"})),
    ("/sessions", frozenset({"analyst", "operator", "sdk", "admin"})),
    ("/threats", frozenset({"analyst", "operator", "developer", "sdk", "admin"})),
    ("/graph/", frozenset({"analyst", "operator", "developer", "admin"})),
    ("/platform/", frozenset({"analyst", "operator", "developer", "admin"})),
)
DEFAULT_ROLES = frozenset({"analyst", "operator", "developer", "admin"})


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


@dataclass(frozen=True)
class AuthContext:
    subject: str
    client_id: str
    roles: frozenset[str]
    tenant_id: str | None
    app_id: str | None
    token_id: str
    expires_at: int

    def has_any_role(self, required: frozenset[str]) -> bool:
        return bool(self.roles.intersection(required))


def create_access_token(
    client_id: str,
    client: dict[str, Any],
    settings: PlatformSettings = platform_settings,
) -> tuple[str, int]:
    now = int(time.time())
    expires_at = now + settings.jwt_ttl_seconds
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "sub": client_id,
        "client_id": client_id,
        "roles": client.get("roles", []),
        "tenant_id": client.get("tenant_id"),
        "app_id": client.get("app_id"),
        "iat": now,
        "nbf": now - 5,
        "exp": expires_at,
        "jti": uuid.uuid4().hex,
    }
    encoded_header = _b64encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _b64encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = hmac.new(settings.jwt_secret.encode(), signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64encode(signature)}", expires_at


def validate_access_token(
    token: str,
    settings: PlatformSettings = platform_settings,
) -> AuthContext:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
        header = json.loads(_b64decode(encoded_header))
        payload = json.loads(_b64decode(encoded_payload))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=401, detail="Malformed access token") from exc
    if header.get("alg") != "HS256" or header.get("typ") != "JWT":
        raise HTTPException(status_code=401, detail="Unsupported access token")
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    expected = hmac.new(settings.jwt_secret.encode(), signing_input, hashlib.sha256).digest()
    try:
        supplied = _b64decode(encoded_signature)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Malformed access token signature") from exc
    if not hmac.compare_digest(expected, supplied):
        raise HTTPException(status_code=401, detail="Invalid access token signature")

    now = int(time.time())
    if payload.get("iss") != settings.jwt_issuer or payload.get("aud") != settings.jwt_audience:
        raise HTTPException(status_code=401, detail="Invalid access token audience")
    if int(payload.get("nbf", 0)) > now or int(payload.get("exp", 0)) <= now:
        raise HTTPException(status_code=401, detail="Access token expired or not active")
    roles = payload.get("roles")
    if not isinstance(roles, list) or not all(isinstance(role, str) for role in roles):
        raise HTTPException(status_code=401, detail="Invalid access token roles")
    return AuthContext(
        subject=str(payload.get("sub", "")),
        client_id=str(payload.get("client_id", "")),
        roles=frozenset(roles),
        tenant_id=payload.get("tenant_id"),
        app_id=payload.get("app_id"),
        token_id=str(payload.get("jti", "")),
        expires_at=int(payload["exp"]),
    )


def required_roles(path: str) -> frozenset[str]:
    for prefix, roles in ROLE_POLICIES:
        if path.startswith(prefix):
            return roles
    return DEFAULT_ROLES


def _bearer(value: str | None) -> str:
    if not value or not value.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer access token required")
    return value[7:].strip()


class PlatformSecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: PlatformSettings = platform_settings):
        super().__init__(app)
        self.settings = settings

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path
        if request.method == "OPTIONS" or path in PUBLIC_PATHS:
            return await call_next(request)
        try:
            context = validate_access_token(
                _bearer(request.headers.get("authorization")),
                self.settings,
            )
            allowed = required_roles(path)
            if not context.has_any_role(allowed):
                raise HTTPException(status_code=403, detail="Role is not authorized for this endpoint")
            request.state.auth = context
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": "AUTHORIZATION_FAILED",
                        "message": exc.detail,
                        "request_id": getattr(request.state, "request_id", None),
                    }
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await call_next(request)


def authenticate_websocket(websocket: WebSocket) -> AuthContext:
    header = websocket.headers.get("authorization")
    query_token = websocket.query_params.get("access_token")
    token = query_token or (_bearer(header) if header else "")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token required")
    context = validate_access_token(token)
    if not context.has_any_role(frozenset({"sdk", "analyst", "operator", "developer", "admin"})):
        raise HTTPException(status_code=403, detail="Role is not authorized for WebSocket")
    return context
