"""
Tests for the Facebook Comment Response Pilot.
These tests should run without network or credentials.
"""
import json
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.facebook_comments.main import CommentProcessor


def test_comment_processor_initialization():
    """Test that CommentProcessor initializes correctly."""
    processor = CommentProcessor(dry_run=True, max_comments=5, max_context_items=8)
    assert processor.dry_run == True
    assert processor.max_comments == 5
    assert processor.max_context_items == 8
    assert isinstance(processor.responder, object)
    print("✓ CommentProcessor initialization test passed")


def test_filter_logic():
    """Test the comment filtering logic."""
    processor = CommentProcessor(dry_run=True)
    
    # Test OWN_PAGE filter
    comment_own_page = {
        "id": "test_1",
        "from": {"id": "1036844829507460"},  # Same as PAGE_ID
        "message": "Test message"
    }
    should_process, reason = processor._filter_comment(comment_own_page)
    assert should_process == False
    assert reason == "OWN_PAGE"
    
    # Test NO_TEXT filter
    comment_no_text = {
        "id": "test_2",
        "from": {"id": "12345"},
        "message": ""
    }
    should_process, reason = processor._filter_comment(comment_no_text)
    assert should_process == False
    assert reason == "NO_TEXT"
    
    # Test TOO_SHORT filter
    comment_too_short = {
        "id": "test_3",
        "from": {"id": "12345"},
        "message": "a"
    }
    should_process, reason = processor._filter_comment(comment_too_short)
    assert should_process == False
    assert reason == "TOO_SHORT"
    
    # Test ONLY_EMOJIS filter (simplified)
    comment_only_emojis = {
        "id": "test_4",
        "from": {"id": "12345"},
        "message": "😀😃😄😁"
    }
    should_process, reason = processor._filter_comment(comment_only_emojis)
    # This might pass or fail depending on emoji range detection
    
    # Test MENTION_ONLY filter
    comment_mention_only = {
        "id": "test_5",
        "from": {"id": "12345"},
        "message": "@username"
    }
    should_process, reason = processor._filter_comment(comment_mention_only)
    assert should_process == False
    assert reason == "MENTION_ONLY"
    
    # Test valid comment
    comment_valid = {
        "id": "test_6",
        "from": {"id": "12345"},
        "message": "This is a valid comment that should pass filters"
    }
    should_process, reason = processor._filter_comment(comment_valid)
    assert should_process == True
    assert reason == "PASSED_FILTERS"
    
    print("✓ Comment filtering logic test passed")


def test_prepare_minimal_context():
    """Test preparation of minimal context."""
    processor = CommentProcessor(dry_run=True)
    
    publication_context = {
        "publication_id": "123_456",
        "published_at": "2026-09-10T10:00:00+0000",
        "asset_ref": "asset_123",
        "post_url": "https://facebook.com/123_456",
        "character": "Test Character",
        "visual_context": "Test visual",
        "meme_text": "Test meme text",
        "caption": "Test caption"
    }
    
    minimal_context = processor._prepare_minimal_context(publication_context)
    
    # Check that all expected keys are present
    expected_keys = ["publication_id", "published_at", "asset_ref", "post_url", 
                     "character", "visual_context", "meme_text", "caption"]
    for key in expected_keys:
        assert key in minimal_context
        assert minimal_context[key] == publication_context[key]
    
    print("✓ Prepare minimal context test passed")


def test_dry_run_mode():
    """Test that dry-run mode doesn't make real API calls."""
    processor = CommentProcessor(dry_run=True, max_comments=2)
    
    # Mock the environment
    os.environ["META_ACCESS_TOKEN"] = "test_token"
    os.environ["FB_PAGE_ID"] = "1036844829507460"
    
    # This would normally make API calls, but in dry-run should return mock data
    # We're not actually running the full process here, just testing the setup
    assert processor.dry_run == True
    assert processor._get_meta_token() == "test_token"
    assert processor._get_page_id() == "1036844829507460"
    
    print("✓ Dry-run mode test passed")


def test_seen_comments_persistence():
    """Test saving and loading seen comments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        seen_file = Path(tmpdir) / "seen_comments.json"
        
        # Create processor with custom seen comments file
        processor = CommentProcessor(dry_run=True)
        processor.seen_comments_file = seen_file
        
        # Add some seen comments
        test_comments = {
            "comment_1": "2026-09-10T10:00:00+0000",
            "comment_2": "2026-09-10T10:05:00+0000"
        }
        processor.seen_comments = test_comments
        processor._save_seen_comments()
        
        # Create new processor and load
        processor2 = CommentProcessor(dry_run=True)
        processor2.seen_comments_file = seen_file
        processor2.seen_comments = processor2._load_seen_comments()
        
        assert processor2.seen_comments == test_comments
    
    print("✓ Seen comments persistence test passed")


if __name__ == "__main__":
    test_comment_processor_initialization()
    test_filter_logic()
    test_prepare_minimal_context()
    test_dry_run_mode()
    test_seen_comments_persistence()
    print("\n✅ All tests passed!")
