"""
Normalization logic for Growth OS entities.

This module normalizes data to ensure consistency in formatting and values.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

def normalize_publication(pub: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a publication dictionary.
    
    Ensures consistent formatting and handles missing optional fields.
    
    Args:
        pub: Publication dictionary to normalize
        
    Returns:
        Normalized publication dictionary
    """
    # Create a copy to avoid modifying the original
    normalized = pub.copy()
    
    # Ensure optional fields are present as None if not provided
    optional_fields = ['meta_post_id', 'experiment_id', 'hypothesis_id']
    for field in optional_fields:
        if field not in normalized:
            normalized[field] = None
        # If the field is present but empty string, convert to None
        elif normalized[field] == "":
            normalized[field] = None
    
    # Ensure string fields are stripped (but be careful with IDs that might have meaning in whitespace)
    # We'll only strip certain fields that are known to have no semantic whitespace
    string_fields = ['platform', 'account_id', 'asset_ref', 'format', 'character', 'circle']
    for field in string_fields:
        if field in normalized and isinstance(normalized[field], str):
            normalized[field] = normalized[field].strip()
    
    # Ensure timestamp is in proper ISO format with Z suffix if it doesn't have timezone
    if 'published_at_utc' in normalized and isinstance(normalized['published_at_utc'], str):
        timestamp = normalized['published_at_utc']
        # If it doesn't end with Z and doesn't have a timezone offset, add Z (assuming UTC)
        if not (timestamp.endswith('Z') or '+' in timestamp or '-' in timestamp[-6:]):
            # Assume it's UTC and add Z
            normalized['published_at_utc'] = timestamp + 'Z'
    
    return normalized


def normalize_metric_snapshot(snap: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a metric snapshot dictionary.
    
    Ensures consistent formatting and handles missing optional fields.
    
    Args:
        snap: Metric snapshot dictionary to normalize
        
    Returns:
        Normalized metric snapshot dictionary
    """
    # Create a copy to avoid modifying the original
    normalized = snap.copy()
    
    # All fields in our schema are required except we could consider some metrics optional?
    # According to the contract, all metrics are required but can be null.
    # So we don't need to add missing fields as they are all required by schema.
    
    # Ensure string fields are stripped where appropriate
    string_fields = ['publication_id', 'raw_source', 'source_version']
    for field in string_fields:
        if field in normalized and isinstance(normalized[field], str):
            normalized[field] = normalized[field].strip()
    
    # Ensure timestamp is in proper ISO format with Z suffix if it doesn't have timezone
    if 'captured_at_utc' in normalized and isinstance(normalized['captured_at_utc'], str):
        timestamp = normalized['captured_at_utc']
        # If it doesn't end with Z and doesn't have a timezone offset, add Z (assuming UTC)
        if not (timestamp.endswith('Z') or '+' in timestamp or '-' in timestamp[-6:]):
            # Assume it's UTC and add Z
            normalized['captured_at_utc'] = timestamp + 'Z'
    
    # Ensure window_type is uppercase
    if 'window_type' in normalized and isinstance(normalized['window_type'], str):
        normalized['window_type'] = normalized['window_type'].upper()
    
    # Ensure quality_status is lowercase (as per our enum)
    if 'quality_status' in normalized and isinstance(normalized['quality_status'], str):
        normalized['quality_status'] = normalized['quality_status'].lower()
    
    # Ensure numeric fields are integers if they are not None
    metric_fields = ['impressions', 'reach', 'views', 'interactions', 'reactions', 'comments', 'shares', 'saves', 'clicks']
    for field in metric_fields:
        if field in normalized and normalized[field] is not None:
            # Try to convert to integer
            try:
                normalized[field] = int(normalized[field])
            except (ValueError, TypeError):
                # If conversion fails, leave as is (validation will catch it)
                pass
    
    return normalized


def normalize_identifier(entity_type: str, identifier: str) -> str:
    """
    Normalize an identifier string.
    
    Args:
        entity_type: Type of entity (for logging or different rules per type)
        identifier: Identifier string to normalize
        
    Returns:
        Normalized identifier string
    """
    if not isinstance(identifier, str):
        return identifier
    
    # Strip whitespace
    normalized = identifier.strip()
    
    # Convert to lowercase? No, IDs should preserve case as they might be case-sensitive.
    # We'll just strip whitespace.
    
    return normalized
