"""
Export functionality for Growth OS entities.

This module provides functions to export publications and metric snapshots
to CSV and JSON formats.
"""

import csv
import json
from typing import List, Dict, Any, Union
import os


def _flatten_publication(pub: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a publication dictionary for export.
    We'll keep it as is, but ensure all fields are present.
    """
    # Define the order and fields we want to export
    fields = [
        "publication_id", "platform", "account_id", "meta_post_id",
        "asset_ref", "published_at_utc", "format", "character",
        "circle", "experiment_id", "hypothesis_id", "status"
    ]
    
    # Create a flattened dict with all fields, using None for missing
    flattened = {}
    for field in fields:
        flattened[field] = pub.get(field)
    
    return flattened


def _flatten_snapshot(snap: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a metric snapshot dictionary for export.
    """
    fields = [
        "snapshot_id", "publication_id", "captured_at_utc", "window_type",
        "impressions", "reach", "views", "interactions", "reactions",
        "comments", "shares", "saves", "clicks", "raw_source",
        "source_version", "quality_status"
    ]
    
    flattened = {}
    for field in fields:
        flattened[field] = snap.get(field)
    
    return flattened


def export_to_json(
    data: List[Dict[str, Any]],
    filepath: Union[str, os.PathLike],
    data_type: str = "snapshot"
) -> None:
    """
    Export a list of publications or snapshots to a JSON file.
    
    Args:
        data: List of publication or snapshot dictionaries
        filepath: Path to the output JSON file
        data_type: Either "publication" or "snapshot"
    """
    if data_type == "publication":
        flattened_data = [_flatten_publication(item) for item in data]
    elif data_type == "snapshot":
        flattened_data = [_flatten_snapshot(item) for item in data]
    else:
        raise ValueError("data_type must be either 'publication' or 'snapshot'")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(flattened_data, f, indent=2, ensure_ascii=False)


def export_to_csv(
    data: List[Dict[str, Any]],
    filepath: Union[str, os.PathLike],
    data_type: str = "snapshot"
) -> None:
    """
    Export a list of publications or snapshots to a CSV file.
    
    Args:
        data: List of publication or snapshot dictionaries
        filepath: Path to the output CSV file
        data_type: Either "publication" or "snapshot"
    """
    if data_type == "publication":
        flattened_data = [_flatten_publication(item) for item in data]
        fieldnames = [
            "publication_id", "platform", "account_id", "meta_post_id",
            "asset_ref", "published_at_utc", "format", "character",
            "circle", "experiment_id", "hypothesis_id", "status"
        ]
    elif data_type == "snapshot":
        flattened_data = [_flatten_snapshot(item) for item in data]
        fieldnames = [
            "snapshot_id", "publication_id", "captured_at_utc", "window_type",
            "impressions", "reach", "views", "interactions", "reactions",
            "comments", "shares", "saves", "clicks", "raw_source",
            "source_version", "quality_status"
        ]
    else:
        raise ValueError("data_type must be either 'publication' or 'snapshot'")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in flattened_data:
            writer.writerow(row)


if __name__ == "__main__":
    # Example usage
    example_publication = {
        "publication_id": "pub_example_001",
        "platform": "instagram",
        "account_id": "account_001",
        "asset_ref": "asset_001",
        "published_at_utc": "2026-09-08T12:00:00Z",
        "format": "video",
        "character": "hero",
        "circle": "fitness",
        "status": "published",
        "experiment_id": "exp_example_001",
        "hypothesis_id": "hyp_example_001",
        "meta_post_id": "meta_post_example_001"
    }
    
    example_snapshot = {
        "snapshot_id": "snap_example_001",
        "publication_id": "pub_example_001",
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
        "raw_source": "api_response_example_001",
        "source_version": "1.0",
        "quality_status": "observed"
    }
    
    # Export to JSON
    export_to_json([example_publication], "outputs/example_publication.json", "publication")
    export_to_json([example_snapshot], "outputs/example_snapshot.json", "snapshot")
    
    # Export to CSV
    export_to_csv([example_publication], "outputs/example_publication.csv", "publication")
    export_to_csv([example_snapshot], "outputs/example_snapshot.csv", "snapshot")
    
    print("Example exports created in the outputs/ directory.")
