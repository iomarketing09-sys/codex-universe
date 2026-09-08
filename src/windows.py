"""
Window calculation and validation for Growth OS metrics.

This module provides functions to calculate and validate window types (E0, E24, E72, lifetime)
based on publication and capture timestamps.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Tuple


def _parse_iso_timestamp(timestamp_str: str) -> datetime:
    """
    Parse an ISO timestamp string to a timezone-aware datetime in UTC.
    
    Args:
        timestamp_str: ISO format timestamp string (may end with Z or have timezone offset)
        
    Returns:
        Timezone-aware datetime in UTC
    """
    # Replace Z with +00:00 for fromisoformat
    if timestamp_str.endswith('Z'):
        timestamp_str = timestamp_str[:-1] + '+00:00'
    
    dt = datetime.fromisoformat(timestamp_str)
    
    # If the datetime is naive (no timezone), assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC
        dt = dt.astimezone(timezone.utc)
    
    return dt


def calculate_window_type(published_at_utc: str, captured_at_utc: str) -> str:
    """
    Calculate the window type based on the time difference between captured and published timestamps.
    
    Windows are defined as:
    - E0: 0 <= delta < 1 hour
    - E24: 24 <= delta < 25 hours
    - E72: 72 <= delta < 73 hours
    - lifetime: delta >= 0 hours (any time after publication)
    
    Args:
        published_at_utc: Publication timestamp in ISO format (UTC)
        captured_at_utc: Capture timestamp in ISO format (UTC)
        
    Returns:
        One of: "E0", "E24", "E72", "lifetime"
        
    Raises:
        ValueError: If timestamps are invalid or captured_at_utc is before published_at_utc
    """
    pub_time = _parse_iso_timestamp(published_at_utc)
    cap_time = _parse_iso_timestamp(captured_at_utc)
    
    # Calculate difference in hours as a float
    delta_seconds = (cap_time - pub_time).total_seconds()
    delta_hours = delta_seconds / 3600.0
    
    if delta_hours < 0:
        raise ValueError(f"captured_at_utc ({captured_at_utc}) must be after or equal to published_at_utc ({published_at_utc})")
    
    # Define windows with inclusive lower bound, exclusive upper bound
    if 0 <= delta_hours < 1:
        return "E0"
    elif 24 <= delta_hours < 25:
        return "E24"
    elif 72 <= delta_hours < 73:
        return "E72"
    else:
        return "lifetime"


def validate_window_type(published_at_utc: str, captured_at_utc: str, window_type: str) -> bool:
    """
    Validate that the given window_type is correct for the publication and capture timestamps.
    
    Args:
        published_at_utc: Publication timestamp in ISO format (UTC)
        captured_at_utc: Capture timestamp in ISO format (UTC)
        window_type: Window type to validate (expected: "E0", "E24", "E72", "lifetime")
        
    Returns:
        True if window_type is correct, False otherwise
    """
    try:
        expected = calculate_window_type(published_at_utc, captured_at_utc)
        return expected == window_type.lower()
    except ValueError:
        return False


def get_time_delta_hours(published_at_utc: str, captured_at_utc: str) -> float:
    """
    Get the time difference in hours between captured and published timestamps.
    
    Args:
        published_at_utc: Publication timestamp in ISO format (UTC)
        captured_at_utc: Capture timestamp in ISO format (UTC)
        
    Returns:
        Time difference in hours (can be negative if captured is before published)
        
    Raises:
        ValueError: If timestamps are invalid
    """
    pub_time = _parse_iso_timestamp(published_at_utc)
    cap_time = _parse_iso_timestamp(captured_at_utc)
    
    delta_seconds = (cap_time - pub_time).total_seconds()
    return delta_seconds / 3600.0


if __name__ == "__main__":
    # Simple self-test
    import sys
    
    # Test cases
    test_cases = [
        # (published, captured, expected_window)
        ("2026-09-08T12:00:00Z", "2026-09-08T12:30:00Z", "E0"),
        ("2026-09-08T12:00:00Z", "2026-09-09T12:00:00Z", "E24"),
        ("2026-09-08T12:00:00Z", "2026-09-11T12:00:00Z", "E72"),
        ("2026-09-08T12:00:00Z", "2026-09-12T12:00:00Z", "lifetime"),
        ("2026-09-08T12:00:00Z", "2026-09-08T12:00:00Z", "E0"),  # exact match
        ("2026-09-08T12:00:00Z", "2026-09-08T13:00:00Z", "lifetime"),  # 1 hour exactly -> lifetime (since E0 is <1 hour)
        ("2026-09-08T12:00:00Z", "2026-09-09T11:59:59Z", "lifetime"),  # 23h59m59s -> lifetime
        ("2026-09-08T12:00:00Z", "2026-09-09T12:00:01Z", "lifetime"),  # 24h00s01s -> lifetime (since E24 is <25 hours)
    ]
    
    all_passed = True
    for published, captured, expected in test_cases:
        try:
            window = calculate_window_type(published, captured)
            if window != expected:
                print(f"FAIL: {published} -> {captured} got {window}, expected {expected}")
                all_passed = False
            else:
                print(f"PASS: {published} -> {captured} = {window}")
        except Exception as e:
            print(f"ERROR: {published} -> {captured} raised {e}")
            all_passed = False
    
    # Test invalid case (captured before published)
    try:
        calculate_window_type("2026-09-08T12:00:00Z", "2026-09-08T11:00:00Z")
        print("FAIL: Should have raised ValueError for captured before published")
        all_passed = False
    except ValueError:
        print("PASS: Correctly raised ValueError for captured before published")
    
    sys.exit(0 if all_passed else 1)
