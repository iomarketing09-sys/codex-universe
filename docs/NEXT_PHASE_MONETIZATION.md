# Next Phase: Monetization Experiment

This document outlines the monetization experiment phase for the Universe Sent Me tenant.

## Experiment Details

- **Experiment ID**: `EXP-2026-09-WILFRED-MON-01`
- **Hypothesis ID**: `H-WILFRED-MON-01`
- **Status**: `insufficient_data` (requires 3 Wilfred posts and 3 control posts)

## Monetization Tracking

The following fields are tracked for monetization purposes:

- `monetization_active`: Boolean indicating if monetization is active
- `monetization_source`: Source of monetization data (e.g., user_reported)
- `manual_publication`: Boolean indicating if publication was manually published

## Revenue Attribution

Revenue is tracked in two distinct ways:

- `account_total`: Total revenue in the account (not attributed to any specific post)
- `post_attributed_revenue`: Revenue attributed to a specific post

## Revenue Data Fields

When revenue data is available:

- `revenue_amount`: Numerical value of revenue
- `currency`: Currency code (e.g., USD)
- `window`: Time window for the revenue (e.g., lifetime, 24h)
- `source`: Source of revenue data (user_reported or meta_reported)

## Experiment Roles

Publications in the experiment are assigned roles:

- `test`: Publications using the Wilfred treatment
- `control`: Publications using the baseline approach

## Synthetic Data Fixtures

For development and testing, the following synthetic data is provided:

### Observed Posts from September 5
Two posts observed on September 5 with missing metrics set to `null`.

### Revenue Data
- **User-reported revenue**: USD 1.48 (never treated as meta-reported)
- **Account total**: USD 2.25 (not attributed to any specific post)

## Validation Rules

1. No revenue data should be invented or estimated
2. `null` values indicate unavailable data and must not be converted to zero
3. `account_total` must never be attributed to individual publications
4. `user_reported` and `meta_reported` sources must remain strictly separated
5. Experiment remains in `insufficient_data` state until 3 Wilfred + 3 control posts are available
6. No new Meta API calls should be made
7. No permission changes should be requested
8. Publications must not be automated
9. No recommendations should be generated
10. No recurring capture should be implemented

## Implementation Notes

The monetization layer has been added as a minimal extension to the existing schema:
- Experiment schema now includes monetization fields
- Publication schema now includes revenue attribution and role fields
- All existing validation and normalization logic has been preserved
- New tests verify the monetization-specific constraints
