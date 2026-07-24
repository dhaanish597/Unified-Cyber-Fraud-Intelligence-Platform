from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from api.store import list_all, put

NOTIFICATION_COLLECTION = "security_notifications"


class NotificationService:
    def create(self, *, user_id: str, kind: str, message: str, session_id: str | None = None, device_id: str | None = None, severity: str = "INFO", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        notification = {
            "notification_id": f"NOTIF_{uuid.uuid4().hex[:12].upper()}",
            "user_id": user_id,
            "kind": kind,
            "severity": severity,
            "message": message,
            "session_id": session_id,
            "device_id": device_id,
            "status": "RECORDED",
            "channel": "IN_APP",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        put(NOTIFICATION_COLLECTION, notification["notification_id"], notification)
        return notification

    def list_for_user(self, user_id: str, limit: int = 100) -> list[dict[str, Any]]:
        rows = [row for row in list_all(NOTIFICATION_COLLECTION) if row.get("user_id") == user_id]
        return rows[-max(1, min(limit, 500)):][::-1]


notification_service = NotificationService()
