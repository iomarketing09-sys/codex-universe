# codex-universe

Operational repository for Codex implementation of the Growth OS metrics contract.

## Purpose

This repository contains two distinct but related systems:

1. **Growth OS Metrics** (Original):  
   Implements the deterministic, verifiable data and metrics layer for the Growth OS system. It implements the minimum viable schemas, validation, normalization, window calculations, and ID generation as defined in the [Contrato Codex–Growth OS: estructura mínima de métricas](./docs/CONTRACT.md).

2. **Facebook Comment Response Pilot** (New):  
   A pilot system for responding to Facebook comments on the Universe Sent Me page, following strict safety and verification protocols to prevent accidental publishing and ensure quality responses.

## Separation of Responsibilities

### Growth OS Metrics (in the `universe-sent-me-growth-os` repository):
- Defines what to measure, why to measure it, hypotheses, decision criteria, and permanent business documentation.

### Codex (this repository):
- **Growth OS Metrics**: Implements how to record, validate, calculate, and return reproducible data. Does not modify the narrative canon or emit strategic conclusions.
- **Facebook Comment Response Pilot**: Implements a safe, verifiable system for generating comment responses with manual approval required for any publishing.

## Current Scope

### Growth OS Metrics:
- JSON schemas for Publication, Experiment, Metric Snapshot, and Hypothesis.
- Validation of required fields, uniqueness, temporal consistency, and quality status.
- Calculation of E0, E24, E72, and lifetime windows.
- Generation of stable IDs from deterministic inputs.
- Synthetic data fixtures for testing.
- Automated tests covering all mandatory test cases from the contract.
- Reproducible export to CSV and JSON.

### Facebook Comment Response Pilot:
- Safe comment fetching with dry-run default mode
- Local filtering before model inference (empty comments, emojis, mentions, etc.)
- Context loading only for substantive comments
- Manual approval required for publishing (--publish-approved flag)
- Pre/post verification checks to prevent duplicate responses
- Append-only logging in JSON and CSV formats
- Batch processing with explicit limits (--max-comments, --max-context-items)
- Comprehensive test suite that runs without credentials

## How to Run Tests

### Growth OS Metrics Tests:
```bash
# Install dependencies (if any)
pip install -r requirements.txt  # Note: we currently have no external dependencies

# Run the test suite
python -m pytest tests/ -v
```

### Facebook Comment Response Pilot Tests:
```bash
# Run Facebook comment tests specifically
python -m pytest tests/facebook_comments/ -v
```

## Facebook Comment Response Pilot Usage

### Default Dry-Run Mode (Safe):
```bash
# Process comments in dry-run mode (no API writes)
python -m src.facebook_comments.main --max-comments 5
```

### Create Approval Template:
```bash
# Create a template for manual approval from last run
python -m src.facebook_comments.main --create-template approval_template.json
```

### Publish Approved Comments (Requires Explicit Live Mode):
```bash
# ONLY use after reviewing and filling in approval_template.json
# WARNING: This would make actual API calls - use with extreme caution
python -m src.facebook_comments.main --live --publish-approved approval_template.json
```

## Deliberately Out of Scope

### For Both Systems:
- Automatic publishing to social media platforms without manual approval.
- Scheduling of publications.
- Recommendation engines.
- Attribution models.
- Strategic analysis or autonomous actions on external accounts.
- Real data ingestion without explicit authorization and safety review.

### For Facebook Comment Response Pilot Specifically:
- Real-time streaming of comments.
- Sentiment analysis beyond basic classification.
- Automated engagement boosting.
- Cross-platform comment responses.

## Security

- No secrets, credentials, or tokens are stored in fixtures, logs, or source code.
- The `.gitignore` file excludes local artifacts and potential secret files.
- All tests run without network or credentials.
- Facebook Comment Response Pilot defaults to dry-run mode and requires explicit flags for any live operations.
- Publishing requires manual approval via --publish-approved with pre-verified comment-text matches.

## Documentation

- [Growth OS Metrics Contract](./docs/CONTRACT.md)
- [Facebook Comment Response Pilot Documentation](./docs/facebook-comments/README.md) (to be created)

