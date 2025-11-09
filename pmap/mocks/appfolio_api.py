#!/usr/bin/env python3
"""
A mock AppFolio API server using FastAPI to simulate the vendor's API.
"""
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from typing import List, Dict, Any

app = FastAPI(title="Mock AppFolio API", version="0.1")

API_KEY = "fake-appfolio-api-key"
API_KEY_NAME = "X-API-KEY"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.get("/properties", response_model=List[Dict[str, Any]])
def list_properties(api_key: str = Depends(get_api_key)):
    return [
        {"id": "prop_1001", "name": "Riverside Arms", "address": "12 River St",
         "city": "Austin", "state": "TX", "postal_code": "73301", "active": True}
    ]

@app.get("/units", response_model=List[Dict[str, Any]])
def list_units(api_key: str = Depends(get_api_key)):
    return [
        {"id": "unit_2001", "property_id": "prop_1001", "label": "Unit 2B",
         "bedrooms": 2, "bathrooms": 1.5, "sqft": 900, "status": "occupied"}
    ]

@app.get("/tenants", response_model=List[Dict[str, Any]])
def list_tenants(api_key: str = Depends(get_api_key)):
    return [
        {"id": "ten_3001", "full_name": "Alex Smith",
         "email": "alex@example.com", "phone": "+15550000001"}
    ]

@app.get("/leases", response_model=List[Dict[str, Any]])
def list_leases(api_key: str = Depends(get_api_key)):
    return [
        {"id": "lea_4001", "unit_id": "unit_2001", "tenant_id": "ten_3001",
         "start_date": "2025-01-01", "end_date": "2025-12-31",
         "rent_cents": 175000, "status": "active"}
    ]

@app.get("/payments", response_model=List[Dict[str, Any]])
def list_payments(api_key: str = Depends(get_api_key)):
    return [
        {"id": "pay_5001", "tenant_id": "ten_3001", "lease_id": "lea_4001",
         "amount_cents": 175000, "posted_date": "2025-11-01", "method": "ach"}
    ]
