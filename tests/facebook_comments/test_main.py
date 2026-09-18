"""
Tests for main functions in facebook_comment_response_pilot.
"""
import json
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.facebook_comments.main import create_approval_template, publish_approved


def test_create_approval_template():
    """Test creating an approval template from results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a sample results file
        results_file = Path(tmpdir) / "results.json"
        sample_results = [
            {
                "comment_id": "comment_1",
                "comment_text": "Test comment 1",
                "needs_response": True,
                "processed": True,
                "response_text": "Suggested response 1"
            },
            {
                "comment_id": "comment_2",
                "comment_text": "Test comment 2",
                "needs_response": False,
                "processed": True,
                "response_text": None
            },
            {
                "comment_id": "comment_3",
                "comment_text": "Test comment 3",
                "needs_response": True,
                "processed": True,
                "response_text": "Suggested response 3"
            }
        ]
        
        with open(results_file, 'w') as f:
            json.dump(sample_results, f)
        
        # Create approval template
        output_file = Path(tmpdir) / "approval_template.json"
        result = create_approval_template(str(results_file), str(output_file))
        
        assert result == 0
        assert output_file.exists()
        
        # Check the template content
        with open(output_file, 'r') as f:
            template = json.load(f)
        
        assert "generated_at" in template
        assert "instructions" in template
        assert "approvals" in template
        assert len(template["approvals"]) == 2  # Only the ones needing response
        
        # Check that the approvals have the correct structure
        for approval in template["approvals"]:
            assert "comment_id" in approval
            assert "comment_text" in approval
            assert "approved_response" in approval
            assert "approved" in approval
            assert approval["approved_response"] == ""  # Initially empty
            assert approval["approved"] == False  # Initially not approved
        
        print("✓ Create approval template test passed")


def test_publish_approved():
    """Test the publish approved function (should be disabled for safety)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an approval file
        approval_file = Path(tmpdir) / "approval.json"
        approval_data = {
            "generated_at": "2026-09-10T10:00:00+0000Z",
            "instructions": "Test instructions",
            "approvals": [
                {
                    "comment_id": "comment_1",
                    "comment_text": "Test comment 1",
                    "approved_response": "Test response 1",
                    "approved": True
                },
                {
                    "comment_id": "comment_2",
                    "comment_text": "Test comment 2",
                    "approved_response": "Test response 2",
                    "approved": False
                },
                {
                    "comment_id": "comment_3",
                    "comment_text": "Test comment 3",
                    "approved_response": "Test response 3",
                    "approved": True
                }
            ]
        }
        
        with open(approval_file, 'w') as f:
            json.dump(approval_data, f)
        
        # Test publish_approved (should return 0 but not actually publish)
        # Note: We're not passing --live flag, so it should still return 0 but warn about safety
        result = publish_approved(str(approval_file))
        assert result == 0
        
        print("✓ Publish approved test passed")


if __name__ == "__main__":
    test_create_approval_template()
    test_publish_approved()
    print("\n✅ All main tests passed!")
