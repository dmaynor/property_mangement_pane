#!/usr/bin/env python3
"""
FastAPI app exposing read-only connector operations for AppFolio.
"""
import os
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from psycopg2.extras import DictCursor
from .adapter_base import Adapter
from .appfolio_adapter import AppFolioAdapter
from .storage import connect, init_schema, now_iso
from .event_bus import process_tuple

app = FastAPI(title="PMAP Read-Only Connector", version="0.1")

ADAPTERS: dict[str, Adapter] = {"appfolio": AppFolioAdapter()}


@app.get("/health")
def health():
    return {"status": "ok", "time": now_iso()}


@app.get("/connectors/{name}/discover")
def discover(name: str):
    adapter = ADAPTERS.get(name)
    if not adapter:
        raise HTTPException(404, f"unknown connector {name}")
    return adapter.discover()


@app.post("/connectors/{name}/pull")
def pull(name: str):
    adapter = ADAPTERS.get(name)
    if not adapter:
        raise HTTPException(404, f"unknown connector {name}")
    conn = connect()
    ingest_id = str(uuid.uuid4())
    results = []
    try:
        for et, rec in adapter.pull():
            results.append(process_tuple(conn, ingest_id, et, rec))
        conn.commit()
    finally:
        conn.close()
    return {"ingest_id": ingest_id, "results": results}


@app.post("/connectors/{name}/webhook")
async def webhook(name: str, request: Request):
    adapter = ADAPTERS.get(name)
    if not adapter:
        raise HTTPException(404, f"unknown connector {name}")
    payload = await request.json()
    conn = connect()
    ingest_id = str(uuid.uuid4())
    results = []
    try:
        for et, rec in adapter.webhook(payload):
            results.append(process_tuple(conn, ingest_id, et, rec))
        conn.commit()
    finally:
        conn.close()
    return {"ingest_id": ingest_id, "results": results}


@app.get("/connectors/{name}/reconcile")
def reconcile(name: str):
    adapter = ADAPTERS.get(name)
    if not adapter:
        raise HTTPException(404, f"unknown connector {name}")
    return adapter.reconcile()


@app.get("/events")
def events(limit: int = 50):
    conn = connect()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                "SELECT * FROM audit_events ORDER BY id DESC LIMIT %s", (limit,)
            )
            rows = [dict(r) for r in cur.fetchall()]
            return {"events": rows}
    finally:
        conn.close()
