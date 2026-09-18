#!/usr/bin/env python3
"""
Fetch real comments from Facebook Graph API for Universe Sent Me page,
process them with UniverseResponder, and output proposed responses for review.
"""
import os
import sys
import re

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.facebook_comments.context.parse_real_pubs import parse_publication_contexts_real
from src.facebook_comments.responders.universe_responder import UniverseResponder

# Import from growth-os modules (these would need to be adapted or replaced)
# For now, we'll create simplified versions that don't depend on growth-os internals
def load_integration_env():
    """Simplified version - loads tenant .env"""
    tenant_env = "tenants/universe/.env"
    if os.path.exists(tenant_env):
        with open(tenant_env, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

def get_page_token(user_token, page_id):
    """Simplified version - gets page access token"""
    # In a real implementation, this would call the Meta API
    # For dry-run mode, we'll return a mock token or None
    if os.environ.get("META_DRY_RUN", "false").lower() == "true":
        return "mock_page_token_for_dry_run"
    # For now, return None to force dry-run or mock
    return None

def api_get(token, endpoint, params):
    """Simplified version - makes API GET request"""
    # In dry-run mode, return mock data
    if os.environ.get("META_DRY_RUN", "false").lower() == "true":
        if endpoint.endswith("/posts"):
            return {"data": [{"id": "1036844829507460_122160925809072582", "created_time": "2026-09-10T10:00:00+0000"}]}
        elif endpoint.endswith("/comments"):
            return {"data": []}
    # For real implementation, this would make actual HTTP requests
    return {"data": []}

def load_env():
    """Load integration environment from tenant's .env."""
    tenant_env = "tenants/universe/.env"
    if os.path.exists(tenant_env):
        with open(tenant_env, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
    # Also load integration env (which loads .env and tenant .env)
    load_integration_env()

def get_post_id_from_url(url):
    """Extract post ID from a Facebook post URL."""
    if not url:
        return None
    # Example: https://www.facebook.com/photo/?fbid=122160625695072582&set=a.122095282845072582
    match = re.search(r'fbid=(\d+)', url)
    if match:
        return match.group(1)
    # If not found, try to extract from the path
    # Example: https://www.facebook.com/permalink.php?story_fbid=123&id=456
    match = re.search(r'story_fbid=(\d+)', url)
    if match:
        return match.group(1)
    return None

def get_publication_contexts(fixture_path):
    """Parse the fixture file to get publication contexts."""
    try:
        return parse_publication_contexts_real(fixture_path)
    except Exception as e:
        print(f"Warning: Could not parse fixture file: {e}")
        return []

def find_context_by_post_id(contexts, post_id):
    """Find a publication context by post ID."""
    for ctx in contexts:
        post_url = ctx.get("post_url")
        if post_url:
            ctx_post_id = get_post_id_from_url(post_url)
            if ctx_post_id == post_id:
                return ctx
    return None

def main():
    load_env()
    user_token = os.environ.get("META_ACCESS_TOKEN")
    if not user_token:
        print("Error: META_ACCESS_TOKEN environment variable not set.")
        sys.exit(1)
    page_id = os.environ.get("FB_PAGE_ID") or os.environ.get("PAGE_ID")
    if not page_id:
        print("Error: FB_PAGE_ID or PAGE_ID environment variable not set.")
        sys.exit(1)
    
    # Get page access token
    page_token = get_page_token(user_token, page_id)
    if not page_token:
        print("Error: Could not obtain page access token.")
        sys.exit(1)
    
    # Initialize responder
    responder = UniverseResponder()
    
    # Load fixture contexts (optional, for context)
    fixture_path = "src/facebook_comments/context/Publication_Contexts_Real_Universe.md"
    contexts = get_publication_contexts(fixture_path)
    if contexts:
        print(f"Loaded {len(contexts)} publication contexts from fixture.")
    else:
        print("Warning: No publication contexts loaded from fixture.")
    
    # We'll get comments from the most recent post of the page.
    # Get the most recent post
    endpoint = f"{page_id}/posts"
    params = {
        "fields": "id,created_time",
        "limit": 1
    }
    try:
        posts_response = api_get(page_token, endpoint, params)
        posts = posts_response.get("data", [])
        if not posts:
            print("Error: No posts found for the page.")
            sys.exit(1)
        post = posts[0]
        post_id = post["id"]
        print(f"Using most recent post: {post_id}")
    except Exception as e:
        print(f"Error fetching posts: {e}")
        # Fallback: use the first post from the fixture
        if contexts:
            first_ctx = contexts[0]
            post_url = first_ctx.get("post_url")
            if post_url:
                post_id = get_post_id_from_url(post_url)
                if post_id:
                    print(f"Using post ID from fixture: {post_id}")
                else:
                    print("Error: Could not extract post ID from fixture and failed to fetch posts.")
                    sys.exit(1)
            else:
                print("Error: No post URL in fixture and failed to fetch posts.")
                sys.exit(1)
        else:
            print("Error: No contexts in fixture and failed to fetch posts.")
            sys.exit(1)
    
    # Get comments for this post
    endpoint = f"{post_id}/comments"
    params = {
        "fields": "id,from,message,created_time",
        "limit": 100  # Get up to 100 comments
    }
    try:
        comments_response = api_get(page_token, endpoint, params)
        comments = comments_response.get("data", [])
        print(f"Fetched {len(comments)} comments.")
    except Exception as e:
        print(f"Error fetching comments: {e}")
        sys.exit(1)
    
    # Process each comment
    processed = 0
    for comment in comments:
        comment_id = comment.get("id")
        comment_from = comment.get("from", {})
        comment_from_id = comment_from.get("id")
        comment_message = comment.get("message", "")
        comment_created_time = comment.get("created_time")
        
        # Check OWN_PAGE: if comment.from.id == PAGE_ID
        if comment_from_id == page_id:
            # Uncomment the following lines to see why it's excluded
            # print(f"\nComment ID: {comment_id}")
            # print(f"Comment: {comment_message}")
            # print(f"From ID: {comment_from_id}")
            # print("-> OWN_PAGE (excluded)")
            continue
        
        # Check NO_TEXT: if message is empty or exactly "(No text)" ignoring spaces
        stripped = comment_message.strip()
        if stripped == "" or stripped.lower() == "(no text)":
            # Uncomment to see
            # print(f"\nComment ID: {comment_id}")
            # print(f"Comment: {comment_message}")
            # print("-> NO_TEXT (excluded)")
            continue
        
        # Find publication context for this post (from fixture)
        context = find_context_by_post_id(contexts, post_id)
        if not context:
            # If not found in fixture, use a minimal context (could be empty)
            context = {
                "publication_id": post_id,
                "published_at": None,
                "asset_ref": None,
                "post_url": f"https://www.facebook.com/{post_id}",
                "character": "",
                "visual_context": "",
                "meme_text": "",
                "caption": ""
            }
        
        # Call the responder
        try:
            result = responder.respond(context, comment_message)
        except Exception as e:
            print(f"\nComment ID: {comment_id}")
            print(f"Comment: {comment_message}")
            print(f"-> Error processing comment: {e}")
            continue
        
        # Output the result
        print("\n" + "="*60)
        print(f"Comment ID: {comment_id}")
        print(f"Comment: {comment_message}")
        print(f"Published at: {comment_created_time}")
        print(f"Publication ID: {result.get('publication_id')}")
        print(f"Comment Type: {result.get('comment_type')}")
        print(f"Relation to Meme: {result.get('relation_to_meme')}")
        print(f"Apparent Intent: {result.get('apparent_intent')}")
        print(f"Decision: {result.get('decision')}")
        print(f"Response: {result.get('response')}")
        print(f"Risk Level: {result.get('risk_level')}")
        if "review_reason" in result:
            print(f"Review Reason: {result.get('review_reason')}")
        print("="*60)
        processed += 1
    
    print(f"\nProcessed {processed} comments (after exclusions).")

if __name__ == "__main__":
    main()
