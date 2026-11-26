# Audit notes

Checks made on `Dhaka_Flat_Market_Snapshot_2026.xlsx` while preparing this repository. The workbook was not modified. Network access was unavailable, so listing URLs were not re-checked against the live portals and source data was not independently verified.

## Verified

- Record count is 72 and IDs are unique (`DPM-001` to `DPM-072`).
- Recalculating asking price / size in Python matches column P for all 72 rows.
- Recalculated area medians match `03 Pricing Analysis` (for example Mirpur 7,394, Uttara 8,926, Mohammadpur 5,330, Dhanmondi 10,536, Bashundhara R/A 10,202; overall 8,913).
- Platform split is 54 bdHousing / 18 Aabason; evidence split is 60 results-page / 12 individual-page.
- No record has a listing date later than its collection date.
- No duplicate records on URL + size + price.

## Inconsistencies in the workbook

1. **Dashboard chart 1 has no category labels.** "Median Asking Price per sq ft by Area" references values only (`'03 Pricing Analysis'!C5:C9`), so the x-axis shows 1-5 instead of area names in LibreOffice. Adding `A5:A9` as the category range would fix it.
2. **Collection dates disagree between sheets.** Every row in `06 Source Register` shows collection date 2026-11-26, but `02 Master Database` has per-record dates from 2026-11-17 to 2026-11-26.
3. **Overview wording.** `01 Project Overview` says listings were displayed up to 25 November 2026, but DPM-050 carries a listing date of 2026-11-26, and the dashboard says "collected 26 Nov 2026".
4. **DPM-019 bedroom mismatch.** Title says 5 beds; the structured Bedrooms field says 6. The structured value is used in the analysis.
5. **Hardcoded transparency counts.** The price-transparency table in `04 Market Segmentation` (rows 51-55) uses typed counts (unique listings in pool, listings with numeric price) taken from a "03 Data Quality" audit that is not part of this workbook, so those two columns cannot be reproduced from this file.
6. **Odd availability notes.** Notes on DPM-052 and DPM-053 quote "available from" dates of 10 Dec 2026 and 31 Dec 2027, which are copied from the portal summary and not interpreted.
7. **Floor conflicts.** DPM-034 and DPM-042 have floor values that conflict between the structured field and the description; the notes column records both.

## Not done

- No screenshots are included. A LibreOffice render of the dashboard splits across pages and mislabels chart 1 (see item 1), so it would not be an accurate picture of the dashboard in Excel.
- No licence file is included, because licensing terms have not been stated. Add one before publishing if you want others to reuse the data.
- The data's right to be redistributed was not assessed; it was collected from public pages of the two portals, so check their terms before publishing.
