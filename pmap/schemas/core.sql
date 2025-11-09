-- Minimal unified datastore (read-only ingestion)

CREATE TABLE IF NOT EXISTS properties (
  id SERIAL PRIMARY KEY,
  source_app TEXT NOT NULL,
  external_id TEXT NOT NULL,
  name TEXT,
  address TEXT,
  city TEXT,
  state TEXT,
  postal_code TEXT,
  active INTEGER DEFAULT 1,
  checksum TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  UNIQUE(source_app, external_id)
);

CREATE TABLE IF NOT EXISTS units (
  id SERIAL PRIMARY KEY,
  source_app TEXT NOT NULL,
  external_id TEXT NOT NULL,
  property_external_id TEXT NOT NULL,
  label TEXT,
  bedrooms INTEGER,
  bathrooms REAL,
  sqft INTEGER,
  status TEXT,
  checksum TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  UNIQUE(source_app, external_id)
);

CREATE TABLE IF NOT EXISTS tenants (
  id SERIAL PRIMARY KEY,
  source_app TEXT NOT NULL,
  external_id TEXT NOT NULL,
  full_name TEXT,
  email_hash TEXT,
  phone_hash TEXT,
  checksum TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  UNIQUE(source_app, external_id)
);

CREATE TABLE IF NOT EXISTS leases (
  id SERIAL PRIMARY KEY,
  source_app TEXT NOT NULL,
  external_id TEXT NOT NULL,
  unit_external_id TEXT NOT NULL,
  tenant_external_id TEXT NOT NULL,
  start_date TEXT,
  end_date TEXT,
  rent_cents INTEGER,
  status TEXT,
  checksum TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  UNIQUE(source_app, external_id)
);

CREATE TABLE IF NOT EXISTS payments (
  id SERIAL PRIMARY KEY,
  source_app TEXT NOT NULL,
  external_id TEXT NOT NULL,
  tenant_external_id TEXT NOT NULL,
  lease_external_id TEXT,
  amount_cents INTEGER,
  posted_date TEXT,
  method TEXT,
  checksum TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  UNIQUE(source_app, external_id)
);

CREATE TABLE IF NOT EXISTS raw_payloads (
  id SERIAL PRIMARY KEY,
  source_app TEXT NOT NULL,
  external_id TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
  id SERIAL PRIMARY KEY,
  ingest_id TEXT NOT NULL,
  source_app TEXT NOT NULL,
  event_type TEXT NOT NULL,
  external_id TEXT NOT NULL,
  actor TEXT NOT NULL,
  latency_ms INTEGER,
  cost_estimate_usd REAL,
  created_at TEXT NOT NULL,
  message TEXT
);
