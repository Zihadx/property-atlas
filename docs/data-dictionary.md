# Data dictionary

## data/listings.csv

One row per qualified listing (72 rows). Exported from sheet `02 Master Database`. Text such as "Not stated" is kept where the source did not provide a value.

| Column | Description |
|---|---|
| `record_id` | Identifier, `DPM-001` to `DPM-072` |
| `listing_summary` | Listing title as recorded |
| `area` | One of the five study areas |
| `specific_location` | Sub-area or landmark from the listing, or "Not stated" |
| `source_platform` | `bdHousing` or `Aabason` |
| `listing_url` | Page the record was taken from |
| `size_sqft` | Apartment size in sq ft |
| `bedrooms`, `bathrooms` | Counts from the structured fields |
| `condition` | Standardised condition (Ready, Brand new, Almost ready, Under construction, Used, Not stated, and one "Brand new (future handover)") |
| `condition_group` | Four groups used in the analysis: Ready or Brand new; Almost Ready or Under Construction; Used; Not stated |
| `floor` | Floor as stated, or "Not stated" |
| `parking_spaces` | Count, or "Not stated". A recorded 0 means the listing explicitly says no parking |
| `asking_price_bdt` | Total asking price in BDT |
| `listed_ppsf_bdt` | Per-sq-ft rate shown by the portal. Blank where the portal gives none |
| `calculated_ppsf_bdt` | `asking_price_bdt / size_sqft` (formula in the workbook) |
| `listed_vs_calculated_gap` | Listed ÷ calculated − 1. Blank where there is no listed rate |
| `pricing_verification_status` | Consistent (within 2%), Discrepancy, or Total only |
| `size_segment` | Size band, derived from `size_sqft` |
| `outlier_flag` | `Outlier` or `Normal` (Tukey fences) |
| `listing_date` | Date shown on the portal, or "Not stated" |
| `research_collection_date` | Collection date recorded in the master sheet (see known issue 2) |
| `evidence_level`, `data_quality_tier` | Results page only (Tier B) or individual page checked (Tier A) |
| `source_record_reference` | Research file and row the record came from |
| `research_notes` | Free-text notes on the record |

## data/source_register.csv

One row per record (72 rows). Exported from sheet `06 Source Register`.

| Column | Description |
|---|---|
| `record_id` | Matches `listings.csv` |
| `source_platform`, `source_url` | Portal and page |
| `source_information` | Type of page (results card or individual page) |
| `collection_date` | Collection date recorded in the register |
| `listing_date` | Date shown on the portal |
| `verification_status` | What was and was not verified |
| `research_notes` | Free-text notes |

## outputs/

Written by `scripts/analyze.py`: `area_summary.csv`, `condition_summary.csv`, `size_segment_summary.csv`, `bedroom_summary.csv`, `platform_summary.csv`, `overall_metrics.csv` and `data_checks.csv`.
