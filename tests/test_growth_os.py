"""
Mandatory test cases for Growth OS contract compliance.
"""

import pytest
from datetime import datetime, timezone
from src.ids import (
    generate_publication_id,
    generate_snapshot_id,
    generate_experiment_id,
    generate_hypothesis_id
)
from src.validate import (
    validate_publication,
    validate_metric_snapshot,
    validate_publication_and_snapshots
)
from src.normalize import normalize_publication, normalize_metric_snapshot
from src.windows import calculate_window_type, validate_window_type
import json
import os
from jsonschema import validate as json_validate, ValidationError


def load_schema(schema_name: str):
    """Load a JSON schema from the schemas directory."""
    schema_dir = os.path.join(os.path.dirname(__file__), '..', 'schemas')
    with open(os.path.join(schema_dir, f"{schema_name}.schema.json"), 'r') as f:
        return json.load(f)


def validate_experiment(exp: dict):
    """Validate an experiment against the experiment schema."""
    experiment_schema = load_schema("experiment")
    errors = []
    try:
        json_validate(instance=exp, schema=experiment_schema)
    except ValidationError as e:
        errors.append(f"Experiment schema validation: {e.message}")
    return len(errors) == 0, errors


def test_valid_publication():
    """Test 1: Publicación válida."""
    publication = {
        "publication_id": "pub_valid_123",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published",
        "experiment_id": "exp_test_456",
        "hypothesis_id": "hyp_test_789"
    }
    
    is_valid, errors = validate_publication(publication)
    assert is_valid, f"Publication should be valid. Errors: {errors}"
    assert len(errors) == 0


def test_valid_e0_snapshot():
    """Test 2: Snapshot E0 válido."""
    publication = {
        "publication_id": "pub_e0_test",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published"
    }
    
    snapshot = {
        "snapshot_id": "snap_e0_valid",
        "publication_id": "pub_e0_test",
        "captured_at_utc": "2026-09-08T12:30:00Z",  # 30 minutes after
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
    
    # Validate snapshot alone
    is_valid, errors = validate_metric_snapshot(snapshot)
    assert is_valid, f"E0 snapshot should be valid. Errors: {errors}"
    
    # Validate publication and snapshot together
    is_valid, errors = validate_publication_and_snapshots(publication, [snapshot])
    assert is_valid, f"Publication with E0 snapshot should be valid. Errors: {errors}"


def test_valid_e24_snapshot():
    """Test 3: Snapshot E24 válido."""
    publication = {
        "publication_id": "pub_e24_test",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published"
    }
    
    # First create a valid E0 snapshot (required for E24)
    e0_snapshot = {
        "snapshot_id": "snap_e0_for_e24",
        "publication_id": "pub_e24_test",
        "captured_at_utc": "2026-09-08T12:30:00Z",
        "window_type": "E0",
        "impressions": 50,
        "reach": 40,
        "views": 25,
        "interactions": 5,
        "reactions": 3,
        "comments": 1,
        "shares": 0,
        "saves": 0,
        "clicks": 1,
        "raw_source": "api_response_001",
        "source_version": "1.0",
        "quality_status": "observed"
    }
    
    # Then the E24 snapshot
    e24_snapshot = {
        "snapshot_id": "snap_e24_valid",
        "publication_id": "pub_e24_test",
        "captured_at_utc": "2026-09-09T12:00:00Z",  # 24 hours after
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
    
    # Validate both snapshots together with publication
    is_valid, errors = validate_publication_and_snapshots(
        publication, [e0_snapshot, e24_snapshot]
    )
    assert is_valid, f"Publication with E0 and E24 snapshots should be valid. Errors: {errors}"


def test_valid_e72_snapshot():
    """Test 4: Snapshot E72 válido."""
    publication = {
        "publication_id": "pub_e72_test",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published"
    }
    
    # Create required E0 snapshot
    e0_snapshot = {
        "snapshot_id": "snap_e0_for_e72",
        "publication_id": "pub_e72_test",
        "captured_at_utc": "2026-09-08T12:30:00Z",
        "window_type": "E0",
        "impressions": 50,
        "reach": 40,
        "views": 25,
        "interactions": 5,
        "reactions": 3,
        "comments": 1,
        "shares": 0,
        "saves": 0,
        "clicks": 1,
        "raw_source": "api_response_001",
        "source_version": "1.0",
        "quality_status": "observed"
    }
    
    # Create the E72 snapshot
    e72_snapshot = {
        "snapshot_id": "snap_e72_valid",
        "publication_id": "pub_e72_test",
        "captured_at_utc": "2026-09-11T12:00:00Z",  # 72 hours after
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
    
    # Validate all together
    is_valid, errors = validate_publication_and_snapshots(
        publication, [e0_snapshot, e72_snapshot]
    )
    assert is_valid, f"Publication with E0 and E72 snapshots should be valid. Errors: {errors}"


def test_duplicate_snapshot():
    """Test 5: Snapshot duplicado."""
    publication = {
        "publication_id": "pub_dup_test",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published"
    }
    
    snapshot1 = {
        "snapshot_id": "snap_duplicate_id",
        "publication_id": "pub_dup_test",
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
    
    snapshot2 = {
        "snapshot_id": "snap_duplicate_id",  # Same ID as snapshot1
        "publication_id": "pub_dup_test",
        "captured_at_utc": "2026-09-08T13:00:00Z",
        "window_type": "E0",
        "impressions": 150,
        "reach": 120,
        "views": 75,
        "interactions": 15,
        "reactions": 8,
        "comments": 5,
        "shares": 2,
        "saves": 1,
        "clicks": 2,
        "raw_source": "api_response_002",
        "source_version": "1.0",
        "quality_status": "observed"
    }
    
    # Should fail due to duplicate snapshot_id
    is_valid, errors = validate_publication_and_snapshots(
        publication, [snapshot1, snapshot2]
    )
    assert not is_valid, "Should fail due to duplicate snapshot_id"
    assert any("Duplicate snapshot_id" in error for error in errors)


def test_missing_metric():
    """Test 6: Métrica faltante (should be null, not zero)."""
    publication = {
        "publication_id": "pub_missing_test",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published"
    }
    
    snapshot = {
        "snapshot_id": "snap_missing_metric",
        "publication_id": "pub_missing_test",
        "captured_at_utc": "2026-09-08T12:30:00Z",
        "window_type": "E0",
        "impressions": 100,
        "reach": None,  # Missing metric should be null, not zero
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
    
    # This should be valid because null is allowed
    is_valid, errors = validate_metric_snapshot(snapshot)
    assert is_valid, f"Snapshot with null metric should be valid. Errors: {errors}"


def test_negative_metric():
    """Test 7: Métrica negativa."""
    publication = {
        "publication_id": "pub_neg_test",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published"
    }
    
    snapshot = {
        "snapshot_id": "snap_negative_metric",
        "publication_id": "pub_neg_test",
        "captured_at_utc": "2026-09-08T12:30:00Z",
        "window_type": "E0",
        "impressions": -10,  # Negative metric should be invalid
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
    
    # Should fail due to negative impressions
    is_valid, errors = validate_metric_snapshot(snapshot)
    assert not is_valid, "Should fail due to negative metric"
    assert any("minimum" in error.lower() for error in errors)


def test_incorrect_timestamp():
    """Test 8: Timestamp incorrecto (captured before published)."""
    publication = {
        "publication_id": "pub_timestamp_test",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published"
    }
    
    snapshot = {
        "snapshot_id": "snap_bad_timestamp",
        "publication_id": "pub_timestamp_test",
        "captured_at_utc": "2026-09-08T11:00:00Z",  # 1 hour BEFORE publication
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
    
    # Should fail because captured_at_utc is before published_at_utc
    is_valid, errors = validate_publication_and_snapshots(publication, [snapshot])
    assert not is_valid, "Should fail due to timestamp incorrecto"
    assert any("before publication" in error for error in errors)


def test_publication_without_hypothesis_id():
    """Test 9: Publicación sin hypothesis_id."""
    publication = {
        "publication_id": "pub_no_hyp_test",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published"
        # Note: hypothesis_id is intentionally omitted
        # experiment_id is also omitted
    }
    
    snapshot = {
        "snapshot_id": "snap_no_hyp",
        "publication_id": "pub_no_hyp_test",
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
    
    # Should be valid because hypothesis_id and experiment_id are optional
    is_valid, errors = validate_publication_and_snapshots(publication, [snapshot])
    assert is_valid, f"Publication without hypothesis_id should be valid. Errors: {errors}"


def test_experiment_with_insufficient_data():
    """Test 10: Experimento con muestra insuficiente."""
    experiment = {
        "experiment_id": "exp_insufficient_test",
        "status": "insufficient_data"
    }
    
    is_valid, errors = validate_experiment(experiment)
    assert is_valid, f"Experiment with insufficient_data status should be valid. Errors: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
