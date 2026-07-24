from __future__ import annotations

import asyncio
from dataclasses import dataclass
from uuid import uuid4


@dataclass
class Subscription:
    subscription_id: str
    queue: asyncio.Queue
    session_id: str | None


class TrustUpdateBroker:
    """Process-local fan-out broker for live WebSocket trust envelopes."""

    def __init__(self):
        self._subscriptions: dict[str, Subscription] = {}
        self._lock = asyncio.Lock()
        self._recent: list[dict] = []

    async def subscribe(self, session_id: str | None = None) -> Subscription:
        subscription = Subscription(
            subscription_id=uuid4().hex,
            queue=asyncio.Queue(maxsize=100),
            session_id=session_id,
        )
        async with self._lock:
            self._subscriptions[subscription.subscription_id] = subscription
        return subscription

    async def unsubscribe(self, subscription_id: str) -> None:
        async with self._lock:
            self._subscriptions.pop(subscription_id, None)

    async def publish(self, envelope: dict) -> None:
        self._recent = ([envelope] + self._recent)[:100]
        async with self._lock:
            subscriptions = list(self._subscriptions.values())
        for subscription in subscriptions:
            if subscription.session_id and envelope.get("session_id") != subscription.session_id:
                continue
            if subscription.queue.full():
                try:
                    subscription.queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            subscription.queue.put_nowait(envelope)

    def recent(self, session_id: str | None = None, limit: int = 50) -> list[dict]:
        rows = self._recent
        if session_id:
            rows = [row for row in rows if row.get("session_id") == session_id]
        return rows[: max(1, min(limit, 100))]


trust_update_broker = TrustUpdateBroker()
