# Module 7 Effective-Date Sync Design

## Goal

From the next successful daily run, publish a current Module 7 opportunity-radar snapshot to its existing Notion page and dashboard payload without backfilling or rewriting pre-2026-08-23 historical content.

## Boundary

- Existing 7A-7I page framework remains intact.
- The system manages only a delimited snapshot on the existing Module 7 parent page.
- Candidates with incomplete data remain grey and are not converted into investment actions.
- The system derives the snapshot solely from already-audited daily payload fields: top-10 industries, market gate, data health, and configured fund holdings.
- Business date is the run date; underlying market dates remain separately displayed, so a weekend run does not claim a nonexistent trading-day quote.

## Data Contract

`data["v2"]["moduleCoverage"]["7"]` is the share of the four required upstream components present: market gate, industry top-10, fund holdings, and finance-news status. The new `data["opportunityRadar"]` contains the business date, market gate, data health, upstream source dates, selected industry rows, and fund rows. Its `executionStatus` is always `灰灯` unless an existing validated execution model supplies a non-grey status; this change introduces no buy/sell signal.

## Publication

The existing visible-page publisher receives page `7`, writes the delimited snapshot to `3c44b7e3bb7081f9be70c52f4b8a9a5f`, verifies the marker and batch identifier, then removes only the previous managed snapshot. Child pages 7A-7I and pre-existing content remain untouched.

## Verification

Unit tests prove that the page-7 blocks include the business date and preserve grey execution status, and that the v2 contract includes module 7. The workflow asserts the module-7 contract and radar payload. A local dry run checks JSON plus test output; deployment verification is limited to the next scheduled run and reads the resulting Notion page back.
