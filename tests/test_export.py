"""
Test export functionality.
"""

import json
import csv
import os
import tempfile
from src.export import export_to_json, export_to_csv


def test_export_to_json():
    """Test exporting to JSON format."""
    publication = {
        "publication_id": "pub_test_001",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published",
        "experiment_id": "exp_test_001",
        "hypothesis_id": "hyp_test_001",
        "meta_post_id": "meta_post_test_001"
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "test_publication.json")
        export_to_json([publication], json_path, "publication")
        
        # Check that the file was created
        assert os.path.exists(json_path)
        
        # Check the content
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]["publication_id"] == "pub_test_001"
        assert data[0]["platform"] == "instagram"
        assert data[0]["status"] == "published"


def test_export_to_csv():
    """Test exporting to CSV format."""
    publication = {
        "publication_id": "pub_test_002",
        "platform": "facebook",
        "account_id": "account_002",
        "asset_ref": "asset_002",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "image",
        "character": "hero",
        "circle": "fitness",
        "status": "published",
        "experiment_id": "exp_test_002",
        "hypothesis_id": "hyp_test_002",
        "meta_post_id": "meta_post_test_002"
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test_publication.csv")
        export_to_csv([publication], csv_path, "publication")
        
        # Check that the file was created
        assert os.path.exists(csv_path)
        
        # Check the content
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 1
        assert rows[0]["publication_id"] == "pub_test_002"
        assert rows[0]["platform"] == "facebook"
        assert rows[0]["status"] == "published"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
