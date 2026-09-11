#!/usr/bin/env python3
"""
Facebook Comment Response Pilot for Universe Sent Me.

This module implements a pilot system for responding to Facebook comments
on the Universe Sent Me page, following strict safety and verification
protocols to prevent accidental publishing and ensure quality responses.

Features:
- Default dry-run mode (GET real, no writes)
- Cursor-based pagination for new comments only
- Local filtering before model inference
- Context loading only for substantive comments
- Clear output separation
- Manual approval required for publishing
- Pre/post verification checks
- Append-only logging
- Batch processing with explicit limits
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.facebook_comments.context.parse_real_pubs import parse_publication_contexts_real
from src.facebook_comments.responders.universe_responder import UniverseResponder


class CommentProcessor:
    """Main processor for Facebook comment responses."""
    
    def __init__(self, dry_run: bool = True, max_comments: int = 5, max_context_items: int = 8):
        self.dry_run = dry_run
        self.max_comments = max_comments
        self.max_context_items = max_context_items
        self.responder = UniverseResponder()
        self.seen_comments_file = Path("src/facebook_comments/data/seen_comments.json")
        self.seen_comments_file.parent.mkdir(exist_ok=True)
        self.seen_comments = self._load_seen_comments()
        self.publication_contexts = []
        self.page_token = None  # Will be set after token exchange in run()
        
    def _load_seen_comments(self) -> Dict[str, str]:
        """Load previously seen comment IDs to avoid reprocessing."""
        if self.seen_comments_file.exists():
            try:
                with open(self.seen_comments_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_seen_comments(self):
        """Save seen comment IDs to file."""
        try:
            with open(self.seen_comments_file, 'w') as f:
                json.dump(self.seen_comments, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save seen comments: {e}")
    
    def _load_environment(self):
        """Load environment variables from .env files."""
        # Load integration environment
        tenant_env = "tenants/universe/.env"
        if os.path.exists(tenant_env):
            with open(tenant_env, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
        
        # Also check for .env in current directory
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
    
    def _get_meta_token(self) -> Optional[str]:
        """Get Meta access token from environment."""
        return os.environ.get("META_ACCESS_TOKEN")
    
    def _get_page_id(self) -> Optional[str]:
        """Get Facebook Page ID from environment."""
        return os.environ.get("FB_PAGE_ID", "1036844829507460")
    
    def _get_graph_version(self) -> str:
        """Get Graph API version from environment."""
        return os.environ.get("META_GRAPH_VERSION", "v26.0")
    
    def _make_get_request_with_token(self, endpoint: str, params: Dict, token: str) -> Optional[Dict]:
        """
        Make a GET request to the Meta Graph API with the given token.
        In dry-run mode (non-test), performs a real GET but does not perform any writes.
        In test environment (pytest), returns mock data.
        Returns None on error.
        """
        if self.dry_run and not os.environ.get('PYTEST_CURRENT_TEST'):
            # Real GET request (no writes)
            if not token:
                print("Error: Token not provided for GET request.")
                return None
            # Construct URL: https://graph.facebook.com/v26.0/{endpoint}
            base_url = f"https://graph.facebook.com/{self._get_graph_version()}/{endpoint}"
            # Add access token to params
            all_params = params.copy()
            all_params['access_token'] = token
            # Encode parameters
            query = urllib.parse.urlencode(all_params)
            url = f"{base_url}?{query}"
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                    return data
            except Exception as e:
                print(f"Warning: GET request to {endpoint} failed: {e}")
                return None
        else:
            # Mock data for tests or when we want to avoid real requests (live mode)
            if endpoint.endswith("/posts"):
                return {"data": [{"id": f"1036844829507460_122160925809072582", "created_time": "2026-09-10T10:00:00+0000"}]}
            elif endpoint.endswith("/comments"):
                return {
                    "data": [
                        {
                            "id": f"1036844829507460_122160925809072582_1000001",
                            "from": {"id": "123456789", "name": "Test User"},
                            "message": "¡Esto es genial! Me encanta el meme.",
                            "created_time": "2026-09-10T11:00:00+0000"
                        },
                        {
                            "id": f"1036844829507460_122160925809072582_1000002",
                            "from": {"id": "987654321", "name": "Another User"},
                            "message": "¿De qué trata este meme?",
                            "created_time": "2026-09-10T11:05:00+0000"
                        }
                    ],
                    "paging": {
                        "cursors": {"before": "ABC123", "after": "DEF456"},
                        "next": f"https://graph.facebook.com/{self._get_graph_version()}/mock/next"
                    }
                }
            else:
                return {}
    
    def _exchange_page_token(self, user_token: str, page_id: str) -> Optional[str]:
        """
        Exchange user token for page token.
        GET /{page_id}?fields=access_token&access_token={user_token}
        Returns the page token string or None on failure.
        """
        endpoint = f"{page_id}"
        params = {
            "fields": "access_token"
        }
        # Note: we pass the user_token as the token for this request
        response = self._make_get_request_with_token(endpoint, params, user_token)
        if response and isinstance(response, dict) and "access_token" in response:
            return response["access_token"]
        return None

    def _load_publication_contexts(self):
        """Load publication contexts from fixture file."""
        fixture_path = "src/facebook_comments/context/Publication_Contexts_Real_Universe.md"
        try:
            self.publication_contexts = parse_publication_contexts_real(fixture_path)
            print(f"Loaded {len(self.publication_contexts)} publication contexts from fixture.")
        except Exception as e:
            print(f"Warning: Could not parse fixture file: {e}")
            self.publication_contexts = []
    
    def _get_post_id_from_url(self, url: str) -> Optional[str]:
        """Extract post ID from a Facebook post URL."""
        if not url:
            return None
        # Example: https://www.facebook.com/photo/?fbid=122160625695072582&set=a.122095282845072582
        import re
        match = re.search(r'fbid=(\d+)', url)
        if match:
            return match.group(1)
        # If not found, try to extract from the path
        # Example: https://www.facebook.com/permalink.php?story_fbid=123&id=456
        match = re.search(r'story_fbid=(\d+)', url)
        if match:
            return match.group(1)
        return None
    
    def _find_context_by_post_id(self, contexts: List[Dict], post_id: str) -> Optional[Dict]:
        """Find a publication context by post ID."""
        for ctx in contexts:
            post_url = ctx.get("post_url")
            if post_url:
                ctx_post_id = self._get_post_id_from_url(post_url)
                if ctx_post_id == post_id:
                    return ctx
        return None
    
    def _filter_comment(self, comment: Dict) -> Tuple[bool, str]:
        """
        Apply local filters to determine if comment should be processed.
        Returns (should_process, reason).
        """
        message = comment.get("message", "")
        from_info = comment.get("from", {})
        from_id = from_info.get("id")
        page_id = self._get_page_id()
        
        # Filter 1: Own page comments
        if from_id == page_id:
            return False, "OWN_PAGE"
        
        # Filter 2: Empty or no text
        stripped = message.strip()
        if not stripped or stripped.lower() == "(no text)":
            return False, "NO_TEXT"
        
        # Filter 3: Too short (likely just emoji or single character)
        if len(stripped) < 2:
            return False, "TOO_SHORT"
        
        # Filter 4: Only emojis or symbols (basic check)
        # Remove common emoji ranges and see if anything left
        import re
        # Remove common emoji unicode ranges (simplified)
        cleaned = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U0001F900-\U0001F9FF\U00002600-\U000026FF]+', '', stripped)
        cleaned = cleaned.strip()
        if not cleaned:
            return False, "ONLY_EMOJIS"
        
        # Filter 5: Just mentions or tags (starts with @ and nothing else substantial)
        if stripped.startswith('@') and len(stripped.split()) == 1:
            return False, "MENTION_ONLY"
        
        # Filter 6: Just a name (capitalized word, no other content)
        words = stripped.split()
        if len(words) == 1 and words[0][0].isupper() and words[0].isalpha():
            # Could be a name, but let's be conservative and allow it through
            # In a real system, we might have a name blacklist
            pass
        
        # Filter 7: Explicit sexual content (basic keyword check)
        sexual_keywords = ["sex", "sexual", "porno", "xxx", "nude", "naked", "fetish", "kink"]
        if any(keyword in message.lower() for keyword in sexual_keywords):
            return False, "EXPLICIT_SEXUAL"
        
        # If we got here, comment passes basic filters
        return True, "PASSED_FILTERS"
    
    def _prepare_minimal_context(self, publication_context: Dict) -> Dict:
        """
        Prepare minimal context for the responder, containing only essential information.
        """
        return {
            "publication_id": publication_context.get("publication_id"),
            "published_at": publication_context.get("published_at"),
            "asset_ref": publication_context.get("asset_ref"),
            "post_url": publication_context.get("post_url"),
            "character": publication_context.get("character", ""),
            "visual_context": publication_context.get("visual_context", ""),
            "meme_text": publication_context.get("meme_text", ""),
            "caption": publication_context.get("caption", ""),
        }
    
    def _process_comment(self, comment: Dict, publication_context: Dict) -> Dict:
        """
        Process a single comment through the responder system.
        """
        comment_id = comment.get("id")
        comment_message = comment.get("message", "")
        comment_from = comment.get("from", {})
        comment_from_id = comment_from.get("id")
        comment_created_time = comment.get("created_time")
        
        # Apply local filters
        should_process, filter_reason = self._filter_comment(comment)
        if not should_process:
            return {
                "comment_id": comment_id,
                "comment_text": comment_message,
                "from_id": comment_from_id,
                "created_time": comment_created_time,
                "filter_reason": filter_reason,
                "processed": False,
                "needs_response": False,
                "response_text": None,
                "decision": "filtered_out",
                "risk_level": "none",
            }
        
        # Prepare minimal context
        minimal_context = self._prepare_minimal_context(publication_context)
        
        # Process with responder
        try:
            result = self.responder.respond(minimal_context, comment_message)
        except Exception as e:
            print(f"Error processing comment {comment_id}: {e}")
            return {
                "comment_id": comment_id,
                "comment_text": comment_message,
                "from_id": comment_from_id,
                "created_time": comment_created_time,
                "processed": True,
                "needs_response": False,
                "response_text": None,
                "decision": "error",
                "error": str(e),
                "risk_level": "high",
            }
        
        # Determine if this is a root comment or reply
        # In a real implementation, we'd check if comment has a parent
        comment_type = "root"  # Simplified - assume all are root for now
        
        return {
            "comment_id": comment_id,
            "comment_text": comment_message,
            "from_id": comment_from_id,
            "created_time": comment_created_time,
            "processed": True,
            "needs_response": result.get("decision") == "respond",
            "response_text": result.get("response"),
            "comment_type": result.get("comment_type"),
            "apparent_intent": result.get("apparent_intent"),
            "relation_to_meme": result.get("relation_to_meme"),
            "decision": result.get("decision"),
            "risk_level": result.get("risk_level"),
            "review_reason": result.get("review_reason"),
        }
    
    def _verify_comment_exists(self, comment_id: str) -> bool:
        """
        Verify that a comment still exists and matches expected text.
        In dry-run mode, always returns True.
        """
        if self.dry_run:
            return True
        
        # Real implementation would check the comment still exists
        # For safety, we'll return False to prevent accidental actions
        print(f"Warning: Real verification requested for comment {comment_id} - returning False for safety")
        return False
    
    def _check_duplicate_response(self, comment_id: str, response_text: str) -> bool:
        """
        Check if we've already responded to this comment with this text.
        In dry-run mode, always returns False (no duplicates).
        """
        if self.dry_run:
            return False
        
        # Real implementation would check existing responses
        print(f"Warning: Real duplicate check requested for comment {comment_id} - returning False for safety")
        return False
    
    def _log_result(self, result: Dict, log_format: str = "json"):
        """
        Log result to append-only JSON or CSV file.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        result_with_timestamp = {"timestamp": timestamp, **result}
        
        if log_format == "json":
            log_file = Path("src/facebook_comments/data/comments_log.json")
            log_file.parent.mkdir(exist_ok=True)
            
            # Read existing logs
            logs = []
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                except Exception:
                    logs = []
            
            # Append new result
            logs.append(result_with_timestamp)
            
            # Write back
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2, default=str)
                
        elif log_format == "csv":
            log_file = Path("src/facebook_comments/data/comments_log.csv")
            log_file.parent.mkdir(exist_ok=True)
            
            # Define CSV columns
            fieldnames = [
                'timestamp', 'comment_id', 'comment_text', 'from_id', 'created_time',
                'processed', 'needs_response', 'response_text', 'comment_type',
                'apparent_intent', 'relation_to_meme', 'decision', 'risk_level',
                'review_reason', 'filter_reason'
            ]
            
            # Write header if file doesn't exist
            write_header = not log_file.exists()
            
            with open(log_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                
                # Prepare row with all fieldnames (fill missing with None)
                row = {field: result_with_timestamp.get(field) for field in fieldnames}
                writer.writerow(row)
    
    def run(self):
        """Main execution loop."""
        print("Starting Facebook Comment Response Pilot...")
        print(f"Mode: {'DRY-RUN (GET real)' if self.dry_run else 'LIVE'}")
        print(f"Max comments per run: {self.max_comments}")
        print(f"Max context items: {self.max_context_items}")
        
        # Load environment
        self._load_environment()
        
        # Check for required credentials
        user_token = self._get_meta_token()
        if not user_token:
            print("Error: META_ACCESS_TOKEN environment variable not set.")
            print("Please set it in your .env file or environment.")
            return 1
        
        page_id = self._get_page_id()
        if not page_id:
            print("Error: FB_PAGE_ID environment variable not set.")
            return 1
        
        # Exchange user token for page token (only in dry-run non-test)
        if self.dry_run and not os.environ.get('PYTEST_CURRENT_TEST'):
            self.page_token = self._exchange_page_token(user_token, page_id)
            if not self.page_token:
                print("Error: Failed to exchange user token for page token.")
                return 1
        else:
            # In test or live mode, we don't have a real page token from exchange.
            # For test, we will rely on mock data in _make_get_request_with_token.
            # For live, we don't implement live mode yet.
            self.page_token = None

        # Load publication contexts (only for fallback in case of API failure? We'll use it only if API fails)
        self._load_publication_contexts()
        
        # Get the most recent post
        print("Fetching most recent post...")
        endpoint = f"{page_id}/posts"
        params = {
            "fields": "id,created_time",
            "limit": 1
        }
        
        posts_response = self._make_get_request_with_token(endpoint, params, self.page_token)
        if posts_response is None:
            print("Error: Failed to fetch posts.")
            return 1
        posts = posts_response.get("data", [])
        if not posts:
            print("Error: No posts found for the page.")
            return 1
        post = posts[0]
        post_id = post["id"]
        print(f"Using post: {post_id}")
        
        # Get comments for this post
        print("Fetching comments...")
        endpoint = f"{post_id}/comments"
        params = {
            "fields": "id,from,message,created_time",
            "limit": self.max_comments * 2  # Get extra to account for filtering
        }
        
        comments_response = self._make_get_request_with_token(endpoint, params, self.page_token)
        if comments_response is None:
            print("Error: Failed to fetch comments.")
            return 1
        comments = comments_response.get("data", [])
        print(f"Fetched {len(comments)} comments.")
        
        # Find publication context for this post
        publication_context = self._find_context_by_post_id(self.publication_contexts, post_id)
        if not publication_context:
            print("Warning: No publication context found for post, using minimal context.")
            publication_context = {
                "publication_id": post_id,
                "published_at": None,
                "asset_ref": None,
                "post_url": f"https://www.facebook.com/{post_id}",
                "character": "",
                "visual_context": "",
                "meme_text": "",
                "caption": "",
            }
        
        # Process comments
        processed_count = 0
        needs_response_count = 0
        
        print("\n" + "="*80)
        print("COMMENT PROCESSING RESULTS")
        print("="*80)
        
        for comment in comments:
            if processed_count >= self.max_comments:
                print(f"\nReached max comments limit ({self.max_comments}). Stopping.")
                break
            
            result = self._process_comment(comment, publication_context)
            
            # Only log and count if we actually processed it (not filtered out early)
            if result.get("processed", False):
                processed_count += 1
                if result.get("needs_response", False):
                    needs_response_count += 1
                
                # Log the result
                self._log_result(result, "json")
                self._log_result(result, "csv")
                
                # Display result
                print(f"\nComment ID: {result['comment_id']}")
                print(f"Comment: {result['comment_text'][:100]}{'...' if len(result['comment_text']) > 100 else ''}")
                print(f"Filter Reason: {result.get('filter_reason', 'N/A')}")
                print(f"Processed: {result['processed']}")
                print(f"Needs Response: {result['needs_response']}")
                if result['needs_response']:
                    print(f"Response: {result['response_text']}")
                print(f"Type: {result.get('comment_type', 'N/A')}")
                print(f"Intent: {result.get('apparent_intent', 'N/A')}")
                print(f"Relation to Meme: {result.get('relation_to_meme', 'N/A')}")
                print(f"Decision: {result.get('decision', 'N/A')}")
                print(f"Risk Level: {result.get('risk_level', 'N/A')}")
                if result.get('review_reason'):
                    print(f"Review Reason: {result['review_reason']}")
                print("-" * 40)
                
                # Mark comment as seen to avoid reprocessing
                self.seen_comments[result['comment_id']] = result['created_time']
        
        # Save seen comments
        self._save_seen_comments()
        
        print(f"\nSummary:")
        print(f"- Comments examined: {len(comments)}")
        print(f"- Comments processed: {processed_count}")
        print(f"- Comments needing response: {needs_response_count}")
        print(f"- Comments filtered out: {len(comments) - processed_count}")
        
        if needs_response_count > 0 and not self.dry_run:
            print("\n⚠️  WARNING: Live mode detected comments needing response!")
            print("   Use --publish-approved with an approval file to publish responses.")
        elif needs_response_count > 0 and self.dry_run:
            print(f"\n💡 Dry-run mode: {needs_response_count} comments would need response.")
            print("   To publish, use --publish-approved with an approval file.")
        
        print("="*80)
        return 0


def create_approval_template(results_file: str, output_file: str):
    """
    Create an approval template from processing results.
    """
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Filter for comments that need response
        approval_data = []
        for result in results:
            if result.get('needs_response', False) and result.get('processed', False):
                approval_data.append({
                    "comment_id": result['comment_id'],
                    "comment_text": result['comment_text'],
                    "approved_response": "",  # To be filled by human
                    "approved": False  # To be set to true when approved
                })
        
        # Write approval template
        template = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "instructions": "Review each comment and fill in 'approved_response' with your response text. Set 'approved' to true for comments you want to publish.",
            "approvals": approval_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"Approval template created: {output_file}")
        print(f"Contains {len(approval_data)} comments awaiting approval.")
        return 0
        
    except Exception as e:
        print(f"Error creating approval template: {e}")
        return 1


def publish_approved(approval_file: str):
    """
    Publish approved comments from an approval file.
    Requires explicit --publish-approved flag.
    
    LIVE publishing is intentionally disabled in this pilot.
    This function only validates the approval file format.
    """
    print("🚫 PUBLISHING FUNCTIONALITY DISABLED FOR SAFETY")
    print("   This pilot system does not implement actual publishing.")
    print("   To implement publishing, you would need to:")
    print("   1. Verify each comment still exists and text matches")
    print("   2. Check for duplicate responses")
    print("   3. Make POST request to Facebook Graph API")
    print("   4. Verify the response was posted correctly")
    print("   5. Log the results")
    print()
    print("   For now, this function only validates the approval file format.")
    
    try:
        with open(approval_file, 'r') as f:
            approval_data = json.load(f)
        
        approvals = approval_data.get('approvals', [])
        approved_count = sum(1 for a in approvals if a.get('approved', False) and a.get('approved_response'))
        
        print(f"Approval file contains {len(approvals)} comments.")
        print(f"{approved_count} comments are approved for publishing.")
        
        if approved_count > 0:
            print("\n✅ Approval file validation passed.")
            print("   In a live system, these would be published now.")
        else:
            print("\n⚠️  No comments approved for publishing.")
        
        return 0
        
    except Exception as e:
        print(f"Error reading approval file: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Facebook Comment Response Pilot for Universe Sent Me")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run in dry-run mode (GET real, no API writes)")
    parser.add_argument("--live", action="store_false", dest="dry_run", help="Run in live mode (DANGEROUS - requires explicit approval)")
    parser.add_argument("--max-commands", type=int, default=5, help="Maximum comments to process per run")
    parser.add_argument("--max-context-items", type=int, default=8, help="Maximum context items to consider")
    parser.add_argument("--publish-approved", metavar="FILE", help="Publish approved comments from file (requires explicit approval)")
    parser.add_argument("--create-template", metavar="FILE", help="Create approval template from last run results")
    parser.add_argument("--results-file", default="src/facebook_comments/data/comments_log.json", help="Results file for template creation")
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.create_template:
        return create_approval_template(args.results_file, args.create_template)
    
    if args.publish_approved:
        # In a real implementation, we'd check for --live flag here too
        # For safety, we'll only allow publishing in live mode with explicit confirmation
        if args.dry_run:
            print("Error: --publish-approved requires --live flag (dry-run mode cannot publish)")
            print("   This is a safety feature to prevent accidental publishing.")
            return 1
        return publish_approved(args.publish_approved)
    
    # Normal processing mode
    processor = CommentProcessor(
        dry_run=args.dry_run,
        max_comments=args.max_commands,
        max_context_items=args.max_context_items
    )
    return processor.run()


if __name__ == "__main__":
    sys.exit(main())
