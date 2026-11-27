# Methodology

## Scope

Residential apartments for sale in five Dhaka areas: Mirpur, Uttara, Mohammadpur, Dhanmondi and Bashundhara R/A. Rentals are excluded. Prices are asking prices in BDT.

## Collection

- Sources: bdHousing (public search-results pages and some individual pages) and Aabason (individual listing pages and one results page).
- Listings displayed between 12 March and 26 November 2026. 59 of the 72 records carry a listing date from October or November 2026; 7 have no displayed listing date.
- Three research files were consolidated and de-duplicated into a pool of 139 unique listings. 79 had a numeric price and 72 qualified for the pricing analysis. These pool counts are hardcoded inputs in sheet 04 of the workbook. The pool itself is not part of this repository, so those three numbers cannot be reproduced here.
- Source URLs are exactly as recorded in the research files.

## Metrics

| Metric | Definition |
|---|---|
| Calculated price per sq ft | Asking price (BDT) ÷ size (sq ft). Used for every comparison. |
| Listed price per sq ft | The rate the portal shows, when it shows one. Kept for comparison only. |
| Gap | Listed rate ÷ calculated rate − 1. |
| Verification status | Consistent if the absolute gap is 2% or less; Discrepancy if above; Total only if no listed rate. |
| Size segment | Under 1,000 / 1,000 to 1,499 / 1,500 to 1,999 / 2,000+ sq ft. |
| Median, Q1, Q3 | Medians are the primary comparison. Quartiles use linear interpolation, equivalent to Excel's `QUARTILE`. |
| Outlier flag | Tukey fences on calculated price per sq ft across all listings: below Q1 − 1.5·IQR or above Q3 + 1.5·IQR. With the current data the upper fence is 16,350 and one listing is flagged. |
| Small sample | An area with fewer than 10 listings is labelled "indicative only". |

Flagged listings are kept and reported, not removed.

## Evidence tiers

- **Tier A:** the individual listing page was checked (12 records).
- **Tier B:** the record rests on the search-results card (60 records). Seller availability was not independently confirmed for any record.

## Reproducing the analysis

`scripts/analyze.py` rebuilds the area, condition, size-segment, bedroom and platform tables, the Tukey fences and the correlations from `data/listings.csv`, then compares them with the values stored in the workbook. See the README for how to run it.

## Reading the results

- Area medians mix in apartment size. Larger flats have higher price per sq ft in this sample (correlation between size and price per sq ft is 0.47), and the areas have different size mixes: 11 of Bashundhara R/A's 21 listings are 2,000+ sq ft, while Mohammadpur has no listing that large. A size-adjusted comparison has not been done.
- Condition groups are small once split (Used n = 5, Not stated n = 10) and should not be over-read.
- Listing counts per area reflect what the two portals display, not market size or demand.
