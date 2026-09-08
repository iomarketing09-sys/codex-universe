# Technical Report: Universe Sent Me Tenant Identity and Data Availability

## Tenant Identification
- **Tenant Name**: Universe Sent Me
- **Facebook Page ID**: `1036844829507460`
- **Instagram Business Account ID**: `17841462696378190`

## Sources of Identification
1. **Configuration File**: `/home/universe-sent-me/growth-os/tenants/universe/.env`
   - Contains `FB_PAGE_ID=1036844829507460`
   - Contains `META_ACCESS_TOKEN` (administrative token from iO Marketing)
2. **Meta Graph API Verification** (using the administrative token):
   - `/me/accounts` endpoint returned a page with `id=1036844829507460` and `name="Universe Sent Me"`
   - `/1036844829507460?fields=instagram_business_account` returned `instagram_business_account.id=17841462696378190`
   - `/1036844829507460/feed?limit=1` returned a post ID confirming page accessibility

## Available Permissions (from `/me/permissions`)
Granted permissions relevant to Universe data access:
- `pages_show_list`
- `business_management`
- `instagram_basic`
- `instagram_manage_comments`
- `instagram_content_publish`
- `pages_read_engagement`
- `pages_read_user_content`
- `pages_manage_posts`
- `pages_manage_engagement`
- `read_audience_network_insights`
- `public_profile`

## Data Obtained (Observed)
The following data points were successfully retrieved and verified:
- Facebook Page ID: `1036844829507460` (observed via `.env` and API)
- Instagram Business Account ID: `17841462696378190` (observed via API)
- Page access token for Universe (derived from admin token)
- Confirmation that the page name is "Universe Sent Me"
- Confirmation that the Instagram account is linked to the page

## Metrics Not Available (Missing)
Due to missing permissions, the following metrics could not be obtained:
- **Facebook Page Insights** (requires `pages_read_insights` permission, not granted)
- **Instagram Business Account Insights** (requires `instagram_manage_insights` or similar, not granted)
- Any metric requiring the `read_insights` permission for either platform

## Limitation Explanation
The administrative token provided by iO Marketing does **not** include the `read_insights` permission for pages or Instagram. Therefore:
- No insights data (engagement, reach, impressions, etc.) could be collected.
- All insight-related fields in the expected schema are intentionally left as `null`.
- The quality of missing insight metrics is marked as `missing` (not zero or estimated).
- This limitation is explicitly documented to avoid misinterpretation of absent data.

## Data Quality Summary
| Data Point                    | Value                            | Quality    | Source                     |
|-------------------------------|----------------------------------|------------|----------------------------|
| Facebook Page ID              | 1036844829507460                 | observed   | `.env` + API verification  |
| Instagram Business Account ID | 17841462696378190                | observed   | API verification           |
| Page Access Token             | (derived, not logged)            | observed   | API exchange               |
| Facebook Page Name            | Universe Sent Me                 | observed   | `/me/accounts`             |
| Instagram Linked              | Yes                              | observed   | API field                  |
| Facebook Page Insights        | null                             | missing    | Permission missing         |
| Instagram Insights            | null                             | missing    | Permission missing         |

## Technical Details
- **API Version Used**: v20.0 (as specified in `.env`)
- **Date/Time of Capture**: 2026-09-08T17:20:00-05:00 (America/Matamoros)
- **External API Calls Made for This Task**:
  1. `/me/accounts` (to list pages and get page token)
  2. `/PAGE_ID?fields=instagram_business_account` (to get IG ID)
  3. `/PAGE_ID/feed?limit=1` (to verify post access)
  4. `/me/permissions` (to check granted permissions)
  **Total**: 4 calls

## Conclusion
The identity of the Universe Sent Me tenant has been conclusively verified using the administrative token of iO Marketing. The Facebook Page ID and Instagram Business Account ID are confirmed and isolated from the Firma Bordados tenant. While basic entity information is accessible, the lack of `read_insights` permission prevents collection of any performance metrics. This report delivers the verified identifiers and documents the data gap honestly, allowing downstream processes to handle missing insight fields appropriately without blocking the current phase.

---
*Report generated as part of the Codex CLI agent task. No tokens or secrets were stored in outputs or commits.*
