"""
Fixtures for Growth OS tests.
"""

import pytest
from src.ids import (
    generate_publication_id,
    generate_snapshot_id,
    generate_experiment_id,
    generate_hypothesis_id
)
from src.validate import validate_publication, validate_metric_snapshot, validate_publication_and_snapshots
from src.normalize import normalize_publication, normalize_metric_snapshot
from src.windows import calculate_window_type, validate_window_type


@pytest.fixture
def valid_publication():
    """Fixture for a valid publication."""
    return {
        "publication_id": "pub_test123",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published",
        "experiment_id": "exp_test456",
        "hypothesis_id": "hyp_test789",
        "meta_post_id": "meta_post_001"
    }


@pytest.fixture
def valid_e0_snapshot():
    """Fixture for a valid E0 snapshot."""
    return {
        "snapshot_id": "snap_e0_test",
        "publication_id": "pub_test123",
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


@pytest.fixture
def valid_e24_snapshot():
    """Fixture for a valid E24 snapshot."""
    return {
        "snapshot_id": "snap_e24_test",
        "publication_id": "pub_test123",
        "captured_at_utc": "2026-09-09T12:00:00Z",
        "window_type": "E24",
        "impressions": 200,
        "reach": 150,
        "views": 100,
        "interactions": 20,
        "reactions": 10,
        "comments": 5,
        "shares": 3,
        "saves": 2,
        "clicks": 2,
        "raw_source": "api_response_002",
        "source_version": "1.0",
        "quality_status": "observed"
    }


@pytest.fixture
def valid_e72_snapshot():
    """Fixture for a valid E72 snapshot."""
    return {
        "snapshot_id": "snap_e72_test",
        "publication_id": "pub_test123",
        "captured_at_utc": "2026-09-11T12:00:00Z",
        "window_type": "E72",
        "impressions": 500,
        "reach": 400,
        "views": 300,
        "interactions": 50,
        "reactions": 25,
        "comments": 10,
        "shares": 8,
        "saves": 5,
        "clicks": 5,
        "raw_source": "api_response_003",
        "source_version": "1.0",
        "quality_status": "observed"
    }


@pytest.fixture
def valid_lifetime_snapshot():
    """Fixture for a valid lifetime snapshot."""
    return {
        "snapshot_id": "snap_lifetime_test",
        "publication_id": "pub_test123",
        "captured_at_utc": "2026-09-15T12:00:00Z",
        "window_type": "lifetime",
        "impressions": 1000,
        "reach": 800,
        "views": 600,
        "interactions": 100,
        "reactions": 50,
        "comments": 20,
        "shares": 15,
        "saves": 10,
        "clicks": 10,
        "raw_source": "api_response_004",
        "source_version": "1.0",
        "quality_status": "observed"
    }


@pytest.fixture
def id_generators():
    """Fixture providing ID generation functions."""
    return {
        "generate_publication_id": generate_publication_id,
        "generate_snapshot_id": generate_snapshot_id,
        "generate_experiment_id": generate_experiment_id,
        "generate_hypothesis_id": generate_hypothesis_id
    }


@pytest.fixture
def validation_functions():
    """Fixture providing validation functions."""
    return {
        "validate_publication": validate_publication,
        "validate_metric_snapshot": validate_metric_snapshot,
        "validate_publication_and_snapshots": validate_publication_and_snapshots
    }


@pytest.fixture
def normalization_functions():
    """Fixture providing normalization functions."""
    return {
        "normalize_publication": normalize_publication,
        "normalize_metric_snapshot": normalize_metric_snapshot
    }


@pytest.fixture
def window_functions():
    """Fixture providing window calculation functions."""
    return {
        "calculate_window_type": calculate_window_type,
        "validate_window_type": validate_window_type
    }
