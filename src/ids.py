"""
Stable ID generation for Growth OS entities.

This module provides deterministic ID generation based on input parameters.
The same input will always produce the same ID, ensuring stability across
different runs and environments.
"""

import hashlib
import json
from typing import Any, Dict, Union


def generate_id(*args: Any, prefix: str = "") -> str:
    """
    Generate a stable ID from the given arguments.
    
    Args:
        *args: Values to include in the ID generation
        prefix: Optional prefix for the ID (e.g., "pub_", "exp_", "snap_", "hyp_")
    
    Returns:
        A stable string ID
    """
    # Convert all arguments to strings and join them with a delimiter
    # Using JSON dumps with sort_keys=True ensures consistent ordering for dicts
    serialized = []
    for arg in args:
        if isinstance(arg, dict):
            serialized.append(json.dumps(arg, sort_keys=True))
        else:
            serialized.append(str(arg))
    
    # Join with a delimiter that won't appear in normal data
    combined = "|".join(serialized)
    
    # Create a SHA-256 hash and take first 12 characters for reasonable length
    hash_object = hashlib.sha256(combined.encode('utf-8'))
    hash_hex = hash_object.hexdigest()[:12]
    
    if prefix:
        return f"{prefix}{hash_hex}"
    return hash_hex


def generate_publication_id(
    platform: str,
    account_id: str,
    asset_ref: str,
    published_at_utc: str,
    format: str,
    character: str,
    circle: str
) -> str:
    """Generate a publication ID from its core attributes."""
    return generate_id(
        platform, account_id, asset_ref, published_at_utc,
        format, character, circle,
        prefix="pub_"
    )


def generate_snapshot_id(
    publication_id: str,
    captured_at_utc: str,
    window_type: str
) -> str:
    """Generate a snapshot ID from publication ID, capture time, and window type."""
    return generate_id(
        publication_id, captured_at_utc, window_type,
        prefix="snap_"
    )


def generate_experiment_id(
    name: str,
    start_date_utc: str,
    hypothesis_ids: list[str]
) -> str:
    """Generate an experiment ID from its core attributes."""
    return generate_id(
        name, start_date_utc, json.dumps(sorted(hypothesis_ids)),
        prefix="exp_"
    )


def generate_hypothesis_id(
    statement: str,
    variables: list[str],
    expected_direction: str
) -> str:
    """Generate a hypothesis ID from its core attributes."""
    return generate_id(
        statement, json.dumps(sorted(variables)), expected_direction,
        prefix="hyp_"
    )
