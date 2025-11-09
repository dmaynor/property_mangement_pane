#!/usr/bin/env python3
"""
AppFolio read-only adapter using a mock API server for testing.
"""
import os
import httpx
from typing import Dict, Any, Iterable, Tuple, List
from .adapter_base import Adapter

class AppFolioClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"X-API-KEY": self.api_key}

    def _get(self, endpoint: str) -> List[Dict[str, Any]]:
        with httpx.Client() as client:
            response = client.get(f"{self.base_url}/{endpoint}", headers=self.headers)
            response.raise_for_status()
            return response.json()

    def list_properties(self) -> List[Dict[str, Any]]:
        return self._get("properties")

    def list_units(self) -> List[Dict[str, Any]]:
        return self._get("units")

    def list_tenants(self) -> List[Dict[str, Any]]:
        return self._get("tenants")

    def list_leases(self) -> List[Dict[str, Any]]:
        return self._get("leases")

    def list_payments(self) -> List[Dict[str, Any]]:
        return self._get("payments")


class AppFolioAdapter(Adapter):
    source_app = "appfolio"

    def __init__(self):
        base_url = os.getenv("APPFOLIO_API_URL", "http://localhost:8001")
        api_key = os.getenv("APPFOLIO_API_KEY", "fake-appfolio-api-key")
        self.client = AppFolioClient(base_url, api_key)

    def discover(self) -> Dict[str, Any]:
        return {
            "source_app": self.source_app,
            "mode": "read_only",
            "resources": ["properties", "units", "tenants", "leases", "payments"],
            "webhook_supported": True,
            "version": "api-0.1"
        }

    def pull(self) -> Iterable[Tuple[str, Dict[str, Any]]]:
        for p in self.client.list_properties():
            yield "property", p
        for u in self.client.list_units():
            yield "unit", u
        for t in self.client.list_tenants():
            yield "tenant", t
        for lz in self.client.list_leases():
            yield "lease", lz
        for pay in self.client.list_payments():
            yield "payment", pay

    def webhook(self, payload: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
        et = payload.get("entity_type")
        data = payload.get("data", {})
        if et in {"property", "unit", "tenant", "lease", "payment"}:
            yield et, data
        else:
            return []

    def reconcile(self) -> Dict[str, Any]:
        counts = {
            "properties": len(self.client.list_properties()),
            "units": len(self.client.list_units()),
            "tenants": len(self.client.list_tenants()),
            "leases": len(self.client.list_leases()),
            "payments": len(self.client.list_payments())
        }
        return {"source_app": self.source_app, "snapshot_counts": counts}
