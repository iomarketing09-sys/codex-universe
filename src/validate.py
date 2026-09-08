"""
Validation logic for Growth OS entities.

This module validates publications and metric snapshots according to the contract.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple, Optional, Set

from jsonschema import validate, ValidationError

try:
    from .windows import validate_window_type
except ImportError:  # direct script execution
    from windows import validate_window_type

# We'll load the schemas from the schemas directory
import os

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), '..', 'schemas')

def load_schema(schema_name: str) -> Dict[str, Any]:
    """Load a JSON schema from the schemas directory."""
    with open(os.path.join(SCHEMA_DIR, f"{schema_name}.schema.json"), 'r') as f:
        return json.load(f)

# Load schemas once at module level
PUBLICATION_SCHEMA = load_schema("publication")
EXPERIMENT_SCHEMA = load_schema("experiment")
METRIC_SNAPSHOT_SCHEMA = load_schema("metric_snapshot")
HYPOTHESIS_SCHEMA = load_schema("hypothesis")


def validate_publication(pub: Dict[str, Any], existing_publication_ids: Optional[Set[str]] = None) -> Tuple[bool, List[str]]:
    """
    Validate a publication against the publication schema and additional business rules.
    
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # 1. Validate against JSON schema
    try:
        validate(instance=pub, schema=PUBLICATION_SCHEMA)
    except ValidationError as e:
        errors.append(f"Publication schema validation: {e.message}")
    
    # 2. Additional business rules:
    #    - publication_id must be unique (if existing_publication_ids is provided)
    pub_id = pub.get("publication_id")
    if pub_id and existing_publication_ids is not None:
        if pub_id in existing_publication_ids:
            errors.append(f"Duplicate publication_id: {pub_id}")
    
    # 3. Check that the status is one of the allowed ones (already in schema).
    # 4. Check that if hypothesis_id is present, it must be a string (already in schema).
    # 5. Check that if experiment_id is present, it must be a string (already in schema).
    
    # 6. Check that the published_at_utc is a valid ISO format (schema format check).
    
    if errors:
        return False, errors
    
    return True, []


def validate_metric_snapshot(snap: Dict[str, Any], existing_snapshot_ids: Optional[Set[str]] = None) -> Tuple[bool, List[str]]:
    """
    Validate a metric snapshot against the metric snapshot schema and additional business rules.
    
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # 1. Validate against JSON schema
    try:
        validate(instance=snap, schema=METRIC_SNAPSHOT_SCHEMA)
    except ValidationError as e:
        errors.append(f"Metric snapshot schema validation: {e.message}")
    
    # 2. Additional business rules:
    #    - snapshot_id must be unique (if existing_snapshot_ids is provided)
    snap_id = snap.get("snapshot_id")
    if snap_id and existing_snapshot_ids is not None:
        if snap_id in existing_snapshot_ids:
            errors.append(f"Duplicate snapshot_id: {snap_id}")
    
    # 3. E24 cannot exist without a valid E0 (we cannot check this without a database of snapshots for the same publication)
    #    We'll handle this in the publication and snapshots validation function.
    
    # 4. captured_at_utc must be after the publication's published_at_utc (we don't have the publication here)
    #    We'll handle this in the publication and snapshots validation function.
    
    # 5. Metrics cannot be negative (schema has minimum 0 for integers, and null is allowed)
    
    # 6. The source_version and raw_source are required (already in schema)
    
    # 7. quality_status must be one of the allowed values (already in schema)
    
    # 8. We'll also check that the window_type is one of the allowed ones (already in schema).
    
    if errors:
        return False, errors
    
    return True, []


def validate_publication_and_snapshots(
    publication: Dict[str, Any],
    snapshots: List[Dict[str, Any]],
    existing_publication_ids: Optional[Set[str]] = None,
    existing_snapshot_ids: Optional[Set[str]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate a publication and its snapshots together, checking cross-cutting rules.
    
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # First, validate the publication itself
    pub_valid, pub_errors = validate_publication(publication, existing_publication_ids)
    if not pub_valid:
        errors.extend(pub_errors)
    
    # Validate each snapshot
    # Also check for duplicate snapshot IDs within the provided snapshots list
    snapshot_ids_seen = set()
    for i, snap in enumerate(snapshots):
        snap_valid, snap_errors = validate_metric_snapshot(snap, existing_snapshot_ids)
        if not snap_valid:
            errors.extend([f"Snapshot {i}: {e}" for e in snap_errors])
        else:
            # Check for duplicate within the list
            snap_id = snap.get("snapshot_id")
            if snap_id:
                if snap_id in snapshot_ids_seen:
                    errors.append(f"Duplicate snapshot_id within the provided snapshots: {snap_id}")
                else:
                    snapshot_ids_seen.add(snap_id)
    
    # Now, check cross-cutting rules that require both publication and snapshots:
    
    publication_id = publication.get("publication_id")
    if publication_id:
        # Group snapshots by window_type
        snapshots_by_window = {}
        for snap in snapshots:
            window_type = snap.get("window_type")
            if window_type not in snapshots_by_window:
                snapshots_by_window[window_type] = []
            snapshots_by_window[window_type].append(snap)
        
        # Check for E24 without E0
        if "E24" in snapshots_by_window and "E0" not in snapshots_by_window:
            errors.append("Publication has an E24 snapshot but no E0 snapshot. E24 requires a valid E0.")
        
        # Rule: captured_at_utc must be after published_at_utc for each snapshot.
        pub_time_str = publication.get("published_at_utc")
        if pub_time_str:
            try:
                pub_time = datetime.fromisoformat(pub_time_str.replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"Invalid published_at_utc format: {pub_time_str}")
            else:
                for snap in snapshots:
                    snap_time_str = snap.get("captured_at_utc")
                    if snap_time_str:
                        try:
                            snap_time = datetime.fromisoformat(snap_time_str.replace('Z', '+00:00'))
                        except ValueError:
                            errors.append(f"Invalid captured_at_utc format in snapshot: {snap_time_str}")
                        else:
                            if snap_time < pub_time:
                                errors.append(
                                    f"Snapshot captured_at_utc {snap_time_str} is before publication published_at_utc {pub_time_str}"
                                )
                            elif not validate_window_type(pub_time_str, snap_time_str, snap.get("window_type", "")):
                                errors.append(
                                    f"Snapshot window_type {snap.get('window_type')} does not match publication/capture timestamps"
                                )
        
        # Additionally, check that each snapshot's publication_id matches the publication's publication_id
        for snap in snapshots:
            if snap.get("publication_id") != publication_id:
                errors.append(f"Snapshot publication_id {snap.get('publication_id')} does not match publication publication_id {publication_id}")
    
    if errors:
        return False, errors
    
    return True, []


if __name__ == "__main__":
    # Simple self-test
    import sys
    
    # Example publication
    example_pub = {
        "publication_id": "pub_abc123",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published"
    }
    
    # Example snapshot
    example_snap = {
        "snapshot_id": "snap_def456",
        "publication_id": "pub_abc123",
        "captured_at_utc": "2026-09-08T12:30:00Z",
        "window_type": "E0",
        "impressions": 100,
        "reach": 80,
        "views": 50,
        "interactions": 10,
        "reactions": 5,
        "comments": 3,
        "shares": 1,
        "saves": 0,
        "clicks": 1,
        "raw_source": "api_response_001",
        "source_version": "1.0",
        "quality_status": "observed"
    }
    
    pub_valid, pub_errs = validate_publication(example_pub)
    print(f"Publication valid: {pub_valid}")
    if not pub_valid:
        print("Errors:", pub_errs)
    
    snap_valid, snap_errs = validate_metric_snapshot(example_snap)
    print(f"Snapshot valid: {snap_valid}")
    if not snap_valid:
        print("Errors:", snap_errs)
    
    both_valid, both_errs = validate_publication_and_snapshots(example_pub, [example_snap])
    print(f"Both valid: {both_valid}")
    if not both_valid:
        print("Errors:", both_errs)
    
    sys.exit(0 if both_valid else 1)
