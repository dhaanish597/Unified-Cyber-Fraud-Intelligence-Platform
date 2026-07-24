from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class PlatformSubscription:
    subscription_id: str
    queue: asyncio.Queue[dict[str, Any]]
    session_id: str | None


class PlatformEventBroker:
    """Process-local fan-out for completed authoritative pipeline results."""

    def __init__(self, queue_size: int = 256, history_size: int = 500):
        self.queue_size = queue_size
        self.history_size = history_size
        self._subscriptions: dict[str, PlatformSubscription] = {}
        self._history: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def subscribe(self, session_id: str | None = None) -> PlatformSubscription:
        subscription = PlatformSubscription(
            subscription_id=uuid.uuid4().hex,
            queue=asyncio.Queue(maxsize=self.queue_size),
            session_id=session_id,
        )
        async with self._lock:
            self._subscriptions[subscription.subscription_id] = subscription
        return subscription

    async def unsubscribe(self, subscription_id: str) -> None:
        async with self._lock:
            self._subscriptions.pop(subscription_id, None)

    async def publish(self, event: dict[str, Any]) -> None:
        self._history = (self._history + [event])[-self.history_size :]
        async with self._lock:
            subscriptions = tuple(self._subscriptions.values())
        event_session = event.get("session_id")
        for subscription in subscriptions:
            if subscription.session_id and subscription.session_id != event_session:
                continue
            if subscription.queue.full():
                try:
                    subscription.queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            subscription.queue.put_nowait(event)

    def recent(self, *, session_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        values = (
            [item for item in self._history if item.get("session_id") == session_id]
            if session_id
            else self._history
        )
        return values[-max(0, min(limit, 500)) :]


platform_event_broker = PlatformEventBroker()
