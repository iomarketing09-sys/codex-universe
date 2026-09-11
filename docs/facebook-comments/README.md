# Facebook Comment Response Pilot

This directory contains documentation for the Facebook Comment Response Pilot system, a safe and verifiable system for generating responses to Facebook comments on the Universe Sent Me page.

## Overview

The Facebook Comment Response Pilot is designed to:
1. Fetch comments from Facebook Graph API (in dry-run mode by default)
2. Apply local filters to remove low-quality or inappropriate comments
3. Process substantive comments through a responder system
4. Generate proposed responses for manual review
5. Require explicit approval before any publishing occurs
6. Verify comments still exist and haven't changed before publishing
7. Prevent duplicate responses
8. Log all activities for auditability

## Safety Features

- **Default Dry-Run Mode**: The system runs in dry-run mode by default, making zero API writes
- **Explicit Opt-In for Publishing**: Requires `--live` flag AND `--publish-approved` with pre-approved content
- **Manual Approval Process**: Humans must review and approve each response before publishing
- **Pre-Publish Verification**: System verifies comment still exists and text matches before publishing
- **Duplicate Prevention**: Checks for existing responses to prevent duplicates
- **No Credentials in Code**: All secrets must be provided via environment variables
- **Local Filtering**: Inappropriate content is filtered out before reaching the AI model

## Components

### Main Entry Point
- `src/facebook_comments/main.py`: Primary interface with argparse for controlling behavior

### Core Modules
- `src/facebook_comments/fetch_comments.py`: Fetches comments and processes them through the pipeline
- `src/facebook_comments/responders/universe_responder.py`: Generates responses based on comment classification
- `src/facebook_comments/context/parse_real_pubs.py`: Parses publication context from markdown fixture

### Data
- `src/facebook_comments/context/Publication_Contexts_Real_Universe.md`: Fixture file with post contexts
- `src/facebook_comments/snapshots/`: Historical comment data for reference/testing
- `src/facebook_comments/data/`: Generated logs and state (JSON/CSV append-only)

### Tests
- `tests/facebook_comments/`: Test suite verifying functionality without credentials

## Usage

### Processing Comments (Dry-Run - Default)
```bash
# Process up to 5 comments in safe dry-run mode
python -m src.facebook_comments.main --max-comments 5

# Process with different limits
python -m src.facebook_comments.main --max-comments 10 --max-context-items 5
```

### Creating Approval Template
```bash
# Generate a template for manual approval from last run
python -m src.facebook_comments.main --create-template approval_template.json

# Then edit approval_template.json to:
# 1. Fill in "approved_response" for each comment you want to publish
# 2. Set "approved": true for those same comments
# 3. Leave "approved": false for comments you don't want to publish
```

### Publishing Approved Comments (Requires Explicit Live Mode)
```bash
# ONLY use after carefully reviewing and completing approval_template.json
# WARNING: This will make actual API calls to Facebook
python -m src.facebook_comments.main --live --publish-approved approval_template.json
```

## Response Format

When processing comments, the system outputs information about each comment:

```
Comment ID: 12345_67890_1000001
Comment: ¡Esto es genial! Me encanta el meme.
Filter Reason: PASSED_FILTERS
Processed: True
Needs Response: True
Response: ¡Gracias! Me alegra que te guste. 😊
Type: humor
Intent: affection
Relation to Meme: direct
Decision: respond
Risk Level: low
```

## Configuration

Environment variables should be set in a `.env` file (never commit this file):

```
META_ACCESS_TOKEN=your_actual_meta_access_token_here
FB_PAGE_ID=1036844829507460
META_GRAPH_VERSION=v26.0
```

See `.env.example` for the template.

## Implementation Details

### Comment Filtering
Before a comment reaches the AI responder, it passes through these filters:
1. **OWN_PAGE**: Comments from the Universe Sent Me page itself are ignored
2. **NO_TEXT**: Empty comments or those with only "(no text)" are ignored
3. **TOO_SHORT**: Comments with less than 2 characters are ignored
4. **ONLY_EMOJIS**: Comments consisting only of emojis are ignored
5. **MENTION_ONLY**: Comments that are only a username mention (e.g., "@username") are ignored
6. **EXPLICIT_SEXUAL**: Comments containing explicit sexual keywords are ignored

### Response Generation
The `UniverseResponder` class classifies comments into types (humor, identification, question, etc.) and generates appropriate responses based on:
- Comment classification
- Meme context from the publication
- Editorial rules from the Universe Sent Me brand guidelines

### Logging
All processed comments are logged to:
- `src/facebook_comments/data/comments_log.json` (JSON array)
- `src/facebook_comments/data/comments_log.csv` (CSV with headers)

Each log entry includes:
- Timestamp
- Comment ID and text
- Processing results (classification, decision, suggested response, etc.)
- Filtering information
- Verification status

## Development

### Running Tests
```bash
# Run only Facebook comment tests
python -m pytest tests/facebook_comments/ -v

# Run all tests (including Growth OS metrics)
python -m pytest tests/ -v
```

### Adding New Features
1. Maintain strict separation from Growth OS metrics code
2. Keep all Facebook comment code under `src/facebook_comments/`
3. Ensure tests run without network or credentials
4. Document any new safety mechanisms
5. Update this README as needed

## Safety Reminders

1. **NEVER** commit `.env` files or any credentials
2. **ALWAYS** review approval templates carefully before using `--publish-approved`
3. **ALWAYS** use `--dry-run` (default) for testing and development
4. **NEVER** use `--live` without explicit intention to publish
5. The system is designed to err on the side of safety - when in doubt, it blocks action

