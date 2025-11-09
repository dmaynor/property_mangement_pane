#!/usr/bin/env python3
"""
API integration tests with TestClient.
"""
import os
from fastapi.testclient import TestClient
from ..storage import init_schema
from .. import api

def setup_module():
    init_schema()

client = TestClient(api.app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_discover():
    r = client.get("/connectors/appfolio/discover")
    assert r.status_code == 200
    body = r.json()
    assert body["source_app"] == "appfolio"
    assert "resources" in body

def test_pull_and_events():
    r = client.post("/connectors/appfolio/pull")
    assert r.status_code == 200
    body = r.json()
    assert "ingest_id" in body
    assert len(body["results"]) >= 5

    ev = client.get("/events?limit=10")
    assert ev.status_code == 200
    assert len(ev.json()["events"]) > 0

def test_webhook_path():
    payload = {
        "entity_type": "tenant",
        "data": {"id": "ten_9999", "full_name": "Casey Wave", "email": "c@x.com", "phone": "+15551112222"}
    }
    r = client.post("/connectors/appfolio/webhook", json=payload)
    assert r.status_code == 200
    assert r.json()["results"][0]["table"] == "tenants"
