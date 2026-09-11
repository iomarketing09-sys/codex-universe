import json
import urllib.request
import urllib.error
import os
import sys
import re

# Add the current directory to the path so we can import universe_responder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from universe_responder import UniverseResponder, parse_publication_contexts_real

# Load the fixture contexts
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), '..', 'Coment_Responses_Universe', 'Publication_Contexts_Real_Universe.md')
contexts = parse_publication_contexts_real(FIXTURE_PATH)
# Create a mapping from post ID (extracted from postURL) to context
def extract_fbid(url):
    # Patterns: .../photo/?fbid=123... or .../photo?fbid=123... or .../reel/123...
    match = re.search(r'fbid=(\d+)', url)
    if match:
        return match.group(1)
    # For reel URLs like .../reel/123...
    match = re.search(r'/reel/(\d+)', url)
    if match:
        return match.group(1)
    return None

context_by_post_id = {}
for ctx in contexts:
    post_url = ctx.get('post_url')
    if post_url:
        fbid = extract_fbid(post_url)
        if fbid:
            # The full post ID is {page_id}_{fbid}
            # But we'll store the fbid and then construct the full ID when needed.
            context_by_post_id[fbid] = ctx

# Load user token from tenants/universe/.env
def load_meta_token():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    user_token = None
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('META_ACCESS_TOKEN='):
                user_token = line.split('=', 1)[1].strip()
                break
    if not user_token:
        raise ValueError('META_ACCESS_TOKEN not found in tenants/universe/.env')
    return user_token

user_token = load_meta_token()

# Get page access token
page_id = '1036844829507460'
url = f'https://graph.facebook.com/v26.0/{page_id}?fields=access_token&access_token={user_token}'
try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        page_token = data.get('access_token')
except Exception as e:
    print(f'Failed to get page token: {e}')
    exit(1)

if not page_token:
    print('No access token in response')
    exit(1)

# Base URL
base_url = 'https://graph.facebook.com/v26.0/'

# We'll collect comments until we have 20
collected_comments = []
responder = UniverseResponder()

# Iterate over the post IDs we have from the fixture
for fbid, ctx in context_by_post_id.items():
    if len(collected_comments) >= 20:
        break
    # Construct the full post ID as expected by the API: {page_id}_{fbid}
    post_id = f'{page_id}_{fbid}'
    # Get comments for this post
    comments_fields = 'id,from,created_time,message'
    comments_url = f'{base_url}{post_id}/comments?fields={comments_fields}&access_token={page_token}&limit=50'
    try:
        with urllib.request.urlopen(comments_url) as response:
            comments_data = json.loads(response.read().decode())
            comments = comments_data.get('data', [])
    except Exception as e:
        print(f'Error fetching comments for post {post_id}: {e}')
        continue

    for comment in comments:
        if len(collected_comments) >= 20:
            break
        # Skip empty messages
        message = comment.get('message')
        if not message:
            continue
        # Skip comments from the page itself (to avoid self-responses)
        from_info = comment.get('from', {})
        if from_info.get('id') == page_id:
            continue
        # Build publication_context dict as expected by the responder
        publication_context = {
            'publication_id': ctx.get('publication_id'),
            'published_at': ctx.get('published_at'),
            'asset_ref': ctx.get('asset_ref'),
            'post_url': ctx.get('post_url'),
            'character': ctx.get('character'),
            'visual_context': ctx.get('visual_context'),
            'meme_text': ctx.get('meme_text'),
            'caption': ctx.get('caption'),
        }
        # Run the responder
        result = responder.respond(publication_context, message)
        # Add the comment id and post id for reference
        result['comment_id'] = comment.get('id')
        result['publication_id_from_api'] = post_id
        result['comment_text'] = message
        collected_comments.append(result)

# Output the results as JSON
output_path = os.path.join(os.path.dirname(__file__), 'real_comments_evaluation.json')
with open(output_path, 'w') as f:
    json.dump(collected_comments, f, indent=2, ensure_ascii=False)

print(f'Evaluated {len(collected_comments)} real comments.')
print(f'Results saved to: {output_path}')
if collected_comments:
    print('First comment evaluation as preview:')
    print(json.dumps(collected_comments[0], indent=2, ensure_ascii=False))
else:
    print('No comments were collected. Check if the posts have comments or if we are being rate limited.')
