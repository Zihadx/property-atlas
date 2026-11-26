# Dhaka Flat Market Snapshot 2026

An Excel-based analysis of asking prices for apartments for sale in five Dhaka neighbourhoods, built from 72 listings collected from two public property portals in November 2026.

The question behind it: how do asking prices per square foot differ across Mirpur, Uttara, Mohammadpur, Dhanmondi and Bashundhara R/A, and where is price information on listings thin enough that an agent or portal could add value?

This is a spreadsheet project. There is no application code, server or database; every figure is a formula inside the workbook.

## Overview

All 72 records are apartments for sale (no rentals), priced in BDT. The primary metric is asking price per sq ft, calculated as asking price divided by size and compared using medians, since a few high-end listings skew the averages. Every record keeps a link back to the portal page it came from, and records are marked by how well they could be verified.

The workbook covers:

- Median, quartile and range of price per sq ft by area, condition group, size band, bedroom count and source portal
- A comparison between the rate a portal prints on a listing and the rate recalculated from its total price and size
- Outlier detection with Tukey fences (flagged and kept, not removed)
- A price-transparency table showing how many unique listings per area showed a numeric price
- A dashboard with five charts

## Headline results

Medians of calculated price per sq ft (BDT), as computed in `03 Pricing Analysis`:

| Area | Listings | Median BDT/sq ft |
|---|---:|---:|
| Mohammadpur | 8 | 5,330 |
| Mirpur | 17 | 7,394 |
| Uttara | 17 | 8,926 |
| Bashundhara R/A | 21 | 10,202 |
| Dhanmondi | 9 | 10,536 |
| All areas | 72 | 8,913 |

Mohammadpur and Dhanmondi have fewer than 10 listings, and the workbook labels them "Indicative only". Treat those two medians with caution.

Of the 72 records, 33 have a listed rate within 2% of the recalculated rate, 24 differ by more than 2%, and 15 (all from Aabason) give a total price only. One record, DPM-049 (Dhanmondi, 22,020 BDT/sq ft), is flagged as an outlier.

## Workbook structure

`data/Dhaka_Flat_Market_Snapshot_2026.xlsx`

| Sheet | Contents |
|---|---|
| `01 Project Overview` | Business question, scope, collection period, sources, limitations |
| `02 Master Database` | 72 listings, 26 columns. Inputs are typed values; columns P to T are formulas |
| `03 Pricing Analysis` | Price-per-sq-ft statistics by area, condition, size band, bedrooms and portal; Tukey fences; correlations |
| `04 Market Segmentation` | Counts and shares by area, size band, condition and bedroom count; price-transparency table |
| `05 Dashboard` | Headline figures and five charts |
| `06 Source Register` | One row per record with source URL, source type, dates and verification status |

Column definitions are in [docs/data-dictionary.md](docs/data-dictionary.md).

## How the numbers are calculated

- **Calculated price per sq ft** (`P`): `Asking Price / Size`
- **Listed vs calculated gap** (`Q`): `Listed rate / Calculated rate - 1`, only where the portal printed a rate
- **Verification status** (`R`): "Consistent" if the gap is within 2%, "Discrepancy" if larger, "Total only" if no rate was printed
- **Size segment** (`S`): under 1,000, 1,000-1,499, 1,500-1,999, 2,000+ sq ft
- **Outlier flag** (`T`): outside Q1 - 1.5 x IQR or Q3 + 1.5 x IQR of calculated price per sq ft across all areas (fences of about 1,943 and 16,350 BDT/sq ft)
- **Per-area medians and quartiles** in `03 Pricing Analysis` are array formulas of the form `MEDIAN(IF(area_range = area, ppsf_range))`

All analysis formulas reference rows 2 to 73 of the master sheet. If you add records, extend those ranges.

## Data sources and collection

- **bdHousing**: 54 records, 53 from public search-results pages and 1 from an individual listing page
- **Aabason**: 18 records, 11 from individual listing pages and 7 from a results page

Overall, 12 records are Tier A (individual page checked) and 60 are Tier B (results page only). Listing dates run from 12 March to 26 November 2026, and per-record collection dates from 17 to 26 November 2026. The `Source Record Reference` column maps each record back to the earlier research files it was consolidated from.

## Opening the workbook

Open it in Microsoft Excel or LibreOffice Calc. Formulas are live, so the sheets recalculate if you edit the inputs. Blue font marks typed audit inputs and black marks formulas.

## Limitations

These come from the project's own overview sheet, plus issues found while preparing this repository.

- Prices are asking prices, not sale prices.
- 72 records is below the 110 originally targeted, and two areas have fewer than 10 listings.
- Only two portals are covered.
- 60 of 72 records come from results pages, not the individual listing pages, so seller availability was not independently confirmed.
- Listing volume does not indicate buyer demand.
- Where a portal-printed rate differs from the recalculated one, the workbook does not establish why (for example, whether the portal used a different size basis).

See [docs/audit-notes.md](docs/audit-notes.md) for known inconsistencies in the workbook.

## Repository layout

```
.
├── README.md
├── data/
│   └── Dhaka_Flat_Market_Snapshot_2026.xlsx
└── docs/
    ├── data-dictionary.md
    └── audit-notes.md
```
