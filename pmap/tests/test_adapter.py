#!/usr/bin/env python3
"""
Unit tests for adapter + normalizer.
"""
import os
from ..storage import init_schema, connect
from ..appfolio_adapter import AppFolioAdapter
from ..event_bus import process_tuple

def setup_module():
    init_schema()

def test_pull_and_upsert_idempotent():
    ad = AppFolioAdapter()
    conn = connect()
    ingest = "test-ingest"
    count_changed = 0
    for et, rec in ad.pull():
        res = process_tuple(conn, ingest, et, rec)
        if res["changed"]:
            count_changed += 1
    conn.commit()

    # Running again should be all no-ops
    count_noop = 0
    for et, rec in ad.pull():
        res = process_tuple(conn, ingest, et, rec)
        if not res["changed"]:
            count_noop += 1
    conn.commit()
    conn.close()

    assert count_changed > 0
    assert count_noop >= 5  # 5 sample entities
