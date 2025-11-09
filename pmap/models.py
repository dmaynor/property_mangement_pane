#!/usr/bin/env python3
"""
Pydantic models for normalized entities and audit events.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class PropertyIn(BaseModel):
    source_app: str = "appfolio"
    external_id: str
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    active: bool = True
    checksum: str
    fetched_at: str


class UnitIn(BaseModel):
    source_app: str = "appfolio"
    external_id: str
    property_external_id: str
    label: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    sqft: Optional[int] = None
    status: Optional[str] = None
    checksum: str
    fetched_at: str


class TenantIn(BaseModel):
    source_app: str = "appfolio"
    external_id: str
    full_name: Optional[str] = None
    email_hash: Optional[str] = None
    phone_hash: Optional[str] = None
    checksum: str
    fetched_at: str


class LeaseIn(BaseModel):
    source_app: str = "appfolio"
    external_id: str
    unit_external_id: str
    tenant_external_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    rent_cents: Optional[int] = None
    status: Optional[str] = None
    checksum: str
    fetched_at: str


class PaymentIn(BaseModel):
    source_app: str = "appfolio"
    external_id: str
    tenant_external_id: str
    lease_external_id: Optional[str] = None
    amount_cents: Optional[int] = None
    posted_date: Optional[str] = None
    method: Optional[str] = None
    checksum: str
    fetched_at: str


class AuditEvent(BaseModel):
    ingest_id: str
    source_app: str
    event_type: Literal[
        "PropertyUpserted","UnitUpserted","TenantUpserted","LeaseUpserted","PaymentRecorded",
        "Noop","Error"
    ]
    external_id: str
    actor: str = "connector@appfolio"
    latency_ms: int = 0
    cost_estimate_usd: float = 0.0
    created_at: str
    message: str = ""
