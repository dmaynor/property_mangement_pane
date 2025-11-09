#!/usr/bin/env python3
"""
Base connector contract for vendor adapters.
"""
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Tuple, Any


class Adapter(ABC):
    """Abstract base adapter with read-only contract."""

    source_app: str = "unknown"

    @abstractmethod
    def discover(self) -> Dict[str, Any]:
        """Return capabilities, resource collections, version. Read-only."""
        raise NotImplementedError

    @abstractmethod
    def pull(self) -> Iterable[Tuple[str, Dict[str, Any]]]:
        """
        Yield tuples of (entity_type, vendor_record_dict) for snapshot sync.
        entity_type ∈ {"property","unit","tenant","lease","payment"}.
        """
        raise NotImplementedError

    @abstractmethod
    def webhook(self, payload: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
        """
        Ingest a single vendor event payload, yielding normalized entity tuples
        (entity_type, vendor_record_dict) suitable for the normalizer.
        """
        raise NotImplementedError

    @abstractmethod
    def reconcile(self) -> Dict[str, Any]:
        """
        Return summary of diffs between vendor snapshot and local rows.
        Read-only: compute and report; do not change vendor or local state.
        """
        raise NotImplementedError
