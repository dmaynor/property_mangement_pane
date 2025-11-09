#!/usr/bin/env python3
"""
Event normalization pipeline: map vendor → unified tables, emit audit.
"""
import hashlib
from typing import Dict, Any, Tuple
from .storage import checksum_of, now_iso, write_audit, write_raw, upsert


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize(entity_type: str, record: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    # Map minimal fields. Real field shapes are vendor-specific [u ❓].
    fetched_at = now_iso()
    if entity_type == "property":
        ext = record["id"]
        unified = {
            "source_app": "appfolio",
            "external_id": ext,
            "name": record.get("name"),
            "address": record.get("address"),
            "city": record.get("city"),
            "state": record.get("state"),
            "postal_code": record.get("postal_code"),
            "active": 1 if record.get("active", True) else 0,
            "checksum": checksum_of(record),
            "fetched_at": fetched_at
        }
        return "properties", unified

    if entity_type == "unit":
        unified = {
            "source_app": "appfolio",
            "external_id": record["id"],
            "property_external_id": record["property_id"],
            "label": record.get("label"),
            "bedrooms": record.get("bedrooms"),
            "bathrooms": record.get("bathrooms"),
            "sqft": record.get("sqft"),
            "status": record.get("status"),
            "checksum": checksum_of(record),
            "fetched_at": fetched_at
        }
        return "units", unified

    if entity_type == "tenant":
        unified = {
            "source_app": "appfolio",
            "external_id": record["id"],
            "full_name": record.get("full_name"),
            "email_hash": _hash(record["email"]) if record.get("email") else None,
            "phone_hash": _hash(record["phone"]) if record.get("phone") else None,
            "checksum": checksum_of(record),
            "fetched_at": fetched_at
        }
        return "tenants", unified

    if entity_type == "lease":
        unified = {
            "source_app": "appfolio",
            "external_id": record["id"],
            "unit_external_id": record["unit_id"],
            "tenant_external_id": record["tenant_id"],
            "start_date": record.get("start_date"),
            "end_date": record.get("end_date"),
            "rent_cents": record.get("rent_cents"),
            "status": record.get("status"),
            "checksum": checksum_of(record),
            "fetched_at": fetched_at
        }
        return "leases", unified

    if entity_type == "payment":
        unified = {
            "source_app": "appfolio",
            "external_id": record["id"],
            "tenant_external_id": record["tenant_id"],
            "lease_external_id": record.get("lease_id"),
            "amount_cents": record.get("amount_cents"),
            "posted_date": record.get("posted_date"),
            "method": record.get("method"),
            "checksum": checksum_of(record),
            "fetched_at": fetched_at
        }
        return "payments", unified

    raise ValueError(f"Unsupported entity_type: {entity_type}")


def process_tuple(conn, ingest_id: str, entity_type: str, record: Dict[str, Any]) -> Dict[str, Any]:
    table, unified = normalize(entity_type, record)

    # Persist raw
    write_raw(conn, {
        "source_app": "appfolio",
        "external_id": unified["external_id"],
        "entity_type": table,
        "payload_json": record,
        "fetched_at": unified["fetched_at"],
    })

    # Upsert
    changed = upsert(
        conn, table,
        unique_keys=("source_app", "external_id"),
        data=unified
    )

    # Audit
    event_type_map = {
        "properties": "PropertyUpserted",
        "units": "UnitUpserted",
        "tenants": "TenantUpserted",
        "leases": "LeaseUpserted",
        "payments": "PaymentRecorded"
    }
    write_audit(conn, {
        "ingest_id": ingest_id,
        "source_app": "appfolio",
        "event_type": event_type_map[table] if changed else "Noop",
        "external_id": unified["external_id"],
        "actor": "connector@appfolio",
        "latency_ms": 0,
        "cost_estimate_usd": 0.0001,
        "created_at": now_iso(),
        "message": f"{'upsert' if changed else 'noop'}:{table}"
    })
    return {"table": table, "external_id": unified["external_id"], "changed": changed}
