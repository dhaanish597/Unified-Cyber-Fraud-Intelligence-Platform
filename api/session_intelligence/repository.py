from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import (
    SessionContext,
    SessionLifecycle,
    SessionSummary,
    TrustDelta,
    TrustPassport,
    TrustSnapshot,
)


class SessionTrustRepository:
    """Additive SQLite repository for Phase 3 session and trust state."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = str(db_path or os.environ.get("DB_PATH", "./finspark.db"))
        self._lock = threading.RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _initialize(self) -> None:
        with self._lock, self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS session_registry (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    trust REAL NOT NULL,
                    confidence REAL NOT NULL,
                    threat_count INTEGER NOT NULL,
                    last_activity TEXT NOT NULL,
                    current_state TEXT NOT NULL,
                    current_device TEXT NOT NULL,
                    location TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    closed_at TEXT,
                    trust_trend TEXT NOT NULL,
                    context_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_session_user_state
                    ON session_registry(user_id, current_state);
                CREATE INDEX IF NOT EXISTS idx_session_activity
                    ON session_registry(last_activity);

                CREATE TABLE IF NOT EXISTS trust_passports (
                    session_id TEXT PRIMARY KEY,
                    passport_id TEXT NOT NULL,
                    updated_time TEXT NOT NULL,
                    version TEXT NOT NULL,
                    passport_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS trust_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    current_trust REAL NOT NULL,
                    snapshot_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_snapshot_session_time
                    ON trust_snapshots(session_id, timestamp);

                CREATE TABLE IF NOT EXISTS trust_deltas (
                    delta_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    difference REAL NOT NULL,
                    is_recovery INTEGER NOT NULL,
                    delta_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_delta_session_time
                    ON trust_deltas(session_id, timestamp);

                CREATE TABLE IF NOT EXISTS trust_recovery_events (
                    delta_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    recovery_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_recovery_session_time
                    ON trust_recovery_events(session_id, timestamp);
                """
            )

    @staticmethod
    def _json(model) -> str:
        return model.model_dump_json()

    def save_state(
        self,
        context: SessionContext,
        passport: TrustPassport,
        snapshot: TrustSnapshot,
        deltas: Iterable[TrustDelta],
    ) -> None:
        delta_list = list(deltas)
        closed_at = (
            context.last_activity.isoformat()
            if context.lifecycle == SessionLifecycle.CLOSED
            else None
        )
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO session_registry (
                    session_id, user_id, trust, confidence, threat_count,
                    last_activity, current_state, current_device, location,
                    created_at, closed_at, trust_trend, context_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    user_id=excluded.user_id,
                    trust=excluded.trust,
                    confidence=excluded.confidence,
                    threat_count=excluded.threat_count,
                    last_activity=excluded.last_activity,
                    current_state=excluded.current_state,
                    current_device=excluded.current_device,
                    location=excluded.location,
                    closed_at=excluded.closed_at,
                    trust_trend=excluded.trust_trend,
                    context_json=excluded.context_json
                """,
                (
                    context.session_id,
                    context.user_id,
                    passport.overall_trust,
                    passport.confidence,
                    context.threat_count,
                    context.last_activity.isoformat(),
                    context.lifecycle.value,
                    context.device_id,
                    context.location,
                    context.created_at.isoformat(),
                    closed_at,
                    passport.trust_trend.value,
                    self._json(context),
                ),
            )
            conn.execute(
                """
                INSERT INTO trust_passports (
                    session_id, passport_id, updated_time, version, passport_json
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    passport_id=excluded.passport_id,
                    updated_time=excluded.updated_time,
                    version=excluded.version,
                    passport_json=excluded.passport_json
                """,
                (
                    passport.session_id,
                    passport.passport_id,
                    passport.updated_time.isoformat(),
                    passport.version,
                    self._json(passport),
                ),
            )
            conn.execute(
                """
                INSERT INTO trust_snapshots (
                    snapshot_id, session_id, timestamp, event_type,
                    current_trust, snapshot_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.snapshot_id,
                    snapshot.session_id,
                    snapshot.timestamp.isoformat(),
                    snapshot.event_type,
                    snapshot.current_trust,
                    self._json(snapshot),
                ),
            )
            for delta in delta_list:
                conn.execute(
                    """
                    INSERT INTO trust_deltas (
                        delta_id, session_id, timestamp, component,
                        difference, is_recovery, delta_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        delta.delta_id,
                        delta.session_id,
                        delta.timestamp.isoformat(),
                        delta.component,
                        delta.difference,
                        int(delta.is_recovery),
                        self._json(delta),
                    ),
                )
                if delta.is_recovery:
                    conn.execute(
                        """
                        INSERT INTO trust_recovery_events (
                            delta_id, session_id, timestamp, recovery_json
                        ) VALUES (?, ?, ?, ?)
                        """,
                        (
                            delta.delta_id,
                            delta.session_id,
                            delta.timestamp.isoformat(),
                            self._json(delta),
                        ),
                    )

    def get_context(self, session_id: str) -> SessionContext | None:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT context_json FROM session_registry WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return SessionContext.model_validate_json(row["context_json"]) if row else None

    def get_passport(self, session_id: str) -> TrustPassport | None:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT passport_json FROM trust_passports WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return TrustPassport.model_validate_json(row["passport_json"]) if row else None

    def get_latest_passport(self) -> TrustPassport | None:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT passport_json FROM trust_passports ORDER BY updated_time DESC LIMIT 1"
            ).fetchone()
        return TrustPassport.model_validate_json(row["passport_json"]) if row else None

    def list_sessions(
        self,
        state: SessionLifecycle | None = None,
        search: str | None = None,
        include_closed: bool = True,
        limit: int = 200,
    ) -> list[SessionSummary]:
        clauses: list[str] = []
        params: list[object] = []
        if state:
            clauses.append("current_state = ?")
            params.append(state.value)
        elif not include_closed:
            clauses.append("current_state != 'CLOSED'")
        if search:
            clauses.append("(session_id LIKE ? OR user_id LIKE ? OR current_device LIKE ?)")
            token = f"%{search}%"
            params.extend([token, token, token])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(max(1, min(limit, 1000)))
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT session_id, user_id, trust, confidence, threat_count,
                       last_activity, current_state, current_device, location,
                       created_at, closed_at, trust_trend
                FROM session_registry
                {where}
                ORDER BY last_activity DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
        return [
            SessionSummary(
                session_id=row["session_id"],
                user_id=row["user_id"],
                trust=row["trust"],
                confidence=row["confidence"],
                threat_count=row["threat_count"],
                last_activity=row["last_activity"],
                current_state=row["current_state"],
                current_device=row["current_device"],
                location=row["location"],
                created_at=row["created_at"],
                closed_at=row["closed_at"],
                trust_trend=row["trust_trend"],
            )
            for row in rows
        ]

    def get_snapshots(
        self,
        session_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 1000,
    ) -> list[TrustSnapshot]:
        clauses = ["session_id = ?"]
        params: list[object] = [session_id]
        if start:
            clauses.append("timestamp >= ?")
            params.append(start.isoformat())
        if end:
            clauses.append("timestamp <= ?")
            params.append(end.isoformat())
        params.append(max(1, min(limit, 5000)))
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT snapshot_json FROM trust_snapshots
                WHERE {' AND '.join(clauses)}
                ORDER BY timestamp ASC
                LIMIT ?
                """,
                params,
            ).fetchall()
        return [TrustSnapshot.model_validate_json(row["snapshot_json"]) for row in rows]

    def get_deltas(self, session_id: str, limit: int = 500) -> list[TrustDelta]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT delta_json FROM trust_deltas
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (session_id, max(1, min(limit, 5000))),
            ).fetchall()
        return [TrustDelta.model_validate_json(row["delta_json"]) for row in rows]

    def get_recovery_events(self, session_id: str, limit: int = 200) -> list[TrustDelta]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT recovery_json FROM trust_recovery_events
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (session_id, max(1, min(limit, 1000))),
            ).fetchall()
        return [TrustDelta.model_validate_json(row["recovery_json"]) for row in rows]
