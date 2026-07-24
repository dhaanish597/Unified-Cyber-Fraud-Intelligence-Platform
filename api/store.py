import sqlite3
import os
import json
import threading

DB_PATH = os.environ.get("DB_PATH", "./finspark.db")

_lock = threading.Lock()
_conn = None

def get_conn():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _init_db()
    return _conn

def _init_db():
    with _conn:
        _conn.execute("""
            CREATE TABLE IF NOT EXISTS store (
                collection TEXT,
                key TEXT,
                value TEXT,
                PRIMARY KEY (collection, key)
            )
        """)

def put(collection: str, key: str, value: dict):
    with _lock:
        conn = get_conn()
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO store (collection, key, value) VALUES (?, ?, ?)",
                (collection, str(key), json.dumps(value))
            )

def get(collection: str, key: str) -> dict:
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT value FROM store WHERE collection = ? AND key = ?", (collection, str(key)))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return None

def list_all(collection: str) -> list:
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT value FROM store WHERE collection = ?", (collection,))
        return [json.loads(row[0]) for row in cur.fetchall()]

def put_raw(collection: str, key: str, value: str):
    with _lock:
        conn = get_conn()
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO store (collection, key, value) VALUES (?, ?, ?)",
                (collection, str(key), value)
            )

def get_raw(collection: str, key: str) -> str:
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT value FROM store WHERE collection = ? AND key = ?", (collection, str(key)))
        row = cur.fetchone()
        if row:
            return row[0]
        return None

def delete(collection: str, key: str) -> bool:
    with _lock:
        conn = get_conn()
        with conn:
            cursor = conn.execute(
                "DELETE FROM store WHERE collection = ? AND key = ?",
                (collection, str(key)),
            )
        return cursor.rowcount > 0
