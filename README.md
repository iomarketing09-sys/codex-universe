# codex-universe

Operational repository for Codex implementation of the Growth OS metrics contract.

## Purpose

This repository contains the deterministic, verifiable data and metrics layer for the Growth OS system. It implements the minimum viable schemas, validation, normalization, window calculations, and ID generation as defined in the [Contrato Codex–Growth OS: estructura mínima de métricas](./docs/CONTRACT.md).

## Separation of Responsibilities

- **Growth OS** (in the `universe-sent-me-growth-os` repository):  
  Defines what to measure, why to measure it, hypotheses, decision criteria, and permanent business documentation.

- **Codex** (this repository):  
  Implements how to record, validate, calculate, and return reproducible data.  
  Does not modify the narrative canon or emit strategic conclusions.

## Current Scope

- JSON schemas for Publication, Experiment, Metric Snapshot, and Hypothesis.
- Validation of required fields, uniqueness, temporal consistency, and quality status.
- Calculation of E0, E24, E72, and lifetime windows.
- Generation of stable IDs from deterministic inputs.
- Synthetic data fixtures for testing.
- Automated tests covering all mandatory test cases from the contract.
- Reproducible export to CSV and JSON.

## How to Run Tests

Assuming you have Python 3.8+ installed:

```bash
# Install dependencies (if any)
pip install -r requirements.txt  # Note: we currently have no external dependencies

# Run the test suite
python -m pytest tests/ -v
```

## Deliberately Out of Scope

- Automatic publishing to social media platforms.
- Scheduling of publications.
- Scraping or real-time API connections to Meta, Instagram, Facebook, etc.
- Recommendation engines.
- Attribution models.
- Strategic analysis or autonomous actions on external accounts.
- Real data ingestion until explicit authorization and a low-risk pilot.

## Security

- No secrets, credentials, or tokens are stored in fixtures, logs, or source code.
- The `.gitignore` file excludes local artifacts and potential secret files.
- All tests run without network or credentials.

