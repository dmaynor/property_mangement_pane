#!/usr/bin/env python3
"""
PostgreSQL storage helpers: apply schema, upsert normalized rows, write audit, store raw payloads.
"""
import hashlib
import json
import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from typing import Dict, Any, Tuple

def connect():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "pmap"),
        user=os.getenv("DB_USER", "pmap"),
        password=os.getenv("DB_PASS", "pmap"),
        port=os.getenv("DB_PORT", "5432")
    )


def init_schema() -> None:
    conn = connect()
    schema_path = os.path.join(os.path.dirname(__file__), "schemas", "core.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        with conn.cursor() as cur:
            cur.execute(f.read())
    conn.commit()
    conn.close()


def checksum_of(obj: Dict[str, Any]) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def upsert(conn, table: str, unique_keys: Tuple[str, ...], data: Dict[str, Any]) -> bool:
    """
    Generic upsert based on unique key columns.
    Returns True if inserted or changed, False if no-op (same checksum).
    """
    with conn.cursor(cursor_factory=DictCursor) as cur:
        where = " AND ".join([f"{k}=%s" for k in unique_keys])
        cur.execute(f"SELECT checksum FROM {table} WHERE {where}", tuple(data[k] for k in unique_keys))
        row = cur.fetchone()

        if row and row["checksum"] == data["checksum"]:
            return False  # idempotent noop

        cols = ", ".join(data.keys())
        excluded = ", ".join([f"EXCLUDED.{k}" for k in data.keys()])
        conflict = ", ".join(unique_keys)

        sql = f"INSERT INTO {table} ({cols}) VALUES %s ON CONFLICT ({conflict}) DO UPDATE SET ({cols}) = ({excluded});"

        from psycopg2.extras import execute_values
        execute_values(cur, sql, [tuple(data.values())])

    return True



def write_audit(conn, event: Dict[str, Any]) -> None:
    with conn.cursor() as cur:
        cols = ", ".join(event.keys())
        ph = ", ".join(["%s"] * len(event))
        cur.execute(f"INSERT INTO audit_events ({cols}) VALUES ({ph})", tuple(event.values()))


def write_raw(conn, payload: Dict[str, Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO raw_payloads (source_app, external_id, entity_type, payload_json, fetched_at) VALUES (%s,%s,%s,%s,%s)",
            (
                payload["source_app"], payload["external_id"], payload["entity_type"],
                json.dumps(payload["payload_json"], separators=(",", ":"), sort_keys=True),
                payload["fetched_at"]
            )
        )
