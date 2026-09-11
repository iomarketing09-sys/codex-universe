import json
import os
import sys

def sanitize_snapshot(input_path, output_path):
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    # Extract required fields
    post_id = data.get('id')
    is_published = data.get('is_published')
    created_time = data.get('created_time')
    permalink_url = data.get('permalink_url')
    
    # Reactions total
    reactions = data.get('reactions')
    reactions_total = None
    if isinstance(reactions, dict):
        reactions_total = reactions.get('summary', {}).get('total_count')
    
    # Comments total
    comments = data.get('comments')
    comments_total = None
    if isinstance(comments, dict):
        comments_total = comments.get('summary', {}).get('total_count')
    
    # Shares total
    shares = data.get('shares')
    shares_total = None
    if isinstance(shares, dict):
        shares_total = shares.get('summary', {}).get('total_count')
    elif isinstance(shares, (int, float)):
        shares_total = shares
    
    # Build sanitized data
    sanitized = {
        'id': post_id,
        'is_published': is_published,
        'reactions_total': reactions_total,
        'comments_total': comments_total,
        'shares_total': shares_total,
        'created_time': created_time,
        'permalink_url': permalink_url,
        'quality_status': 'observed'
    }
    
    # Remove any keys that are None
    sanitized = {k: v for k, v in sanitized.items() if v is not None}
    
    with open(output_path, 'w') as f:
        json.dump(sanitized, f, indent=2)

def main():
    snapshot_dir = 'snapshots'
    if not os.path.isdir(snapshot_dir):
        print(f"Directory {snapshot_dir} does not exist")
        sys.exit(1)
    
    for filename in os.listdir(snapshot_dir):
        if filename.endswith('.json'):
            input_path = os.path.join(snapshot_dir, filename)
            output_path = os.path.join(snapshot_dir, filename)
            sanitize_snapshot(input_path, output_path)
            print(f"Sanitized {filename}")

if __name__ == '__main__':
    main()
