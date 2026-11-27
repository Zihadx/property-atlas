# Known issues

Found while checking the workbook against its own data. The original workbook in `data/` has **not** been edited, so every figure in it is as originally produced. Each issue below says what is affected and how to fix it in the workbook.

## 1. "Median absolute gap" in 03 Pricing Analysis is understated

**Where:** `03 Pricing Analysis`, cell B59 (row "Median absolute gap, listed vs calculated").

**What happens:** The formula is `MEDIAN(ABS(IF(ISNUMBER(Q2:Q73), Q2:Q73)))`. For the 15 listings with no listed rate, `IF` returns FALSE, `ABS(FALSE)` is 0, and those 15 zeros are included in the median. The row sits next to "Listings with both listed and calculated rate = 57", so it reads as a median over 57 listings.

**Effect:** The workbook shows 0.067%. Over the 57 listings that actually have both rates it is 0.19%. `scripts/analyze.py` reproduces the workbook's 0.067% by treating the 15 as zeros, and reports the 0.19% figure separately. Nothing else in the workbook depends on this cell.

**Fix:** Use `=MEDIAN(IF(ISNUMBER(Q2:Q73),ABS(Q2:Q73)))` entered as an array formula, so non-numeric rows are skipped.

## 2. Collection dates disagree between sheets

**Where:** `02 Master Database` column V versus `06 Source Register` column E, and the Dashboard subtitle.

**What happens:** The master sheet holds collection dates from 17 to 26 November 2026 (6 to 11 records per day). The source register records 26 November 2026 for all 72 records, and the dashboard says "collected 26 Nov 2026". 64 of 72 records differ between the two sheets.

**Effect:** None of the price figures change, but the record of when each listing was seen is unreliable until one version is confirmed.

**Fix:** Decide which is correct and align the other sheet. If all records were captured on 26 November, the master sheet column is wrong; if collection ran over ten days, the register and dashboard text are wrong.

## 3. DPM-019 bedroom count conflicts with its title

**Where:** `02 Master Database`, row DPM-019 (Uttara, 3,152 sq ft).

**What happens:** The listing title says "5 Beds"; the structured fields say 6 bedrooms and 6 bathrooms. The research note says "No issues noted".

**Effect:** Small. The bedroom table groups it as "5+" either way. It is counted once in that group.

**Fix:** Check the source page and record the correct count, or add a note.

## 4. Dashboard chart 1 has no category labels

**Where:** `05 Dashboard`, "Median Asking Price per sq ft by Area (BDT)".

**What happens:** The chart's data series points at `03 Pricing Analysis!C5:C9` but the chart definition contains no category range. The x-axis therefore shows no area names (some viewers show 1 to 5). A screenshot of the chart in Excel is in `docs/images/dashboard/01-median-ppsf-by-area.png`. The other four charts do have category ranges.

**Fix:** In the chart's data settings, set the horizontal axis labels to `'03 Pricing Analysis'!$A$5:$A$9`. This repository's `docs/images/analysis/median_ppsf_by_area.png` shows the intended chart.

## 5. Reference to a sheet that is not in the file

**Where:** Footnote under the transparency table in `04 Market Segmentation`.

**What happens:** The footnote says the blue counts come from "03 Data Quality". The workbook has no such sheet (sheets are 01, 02, 03 Pricing Analysis, 04, 05, 06).

**Effect:** The pool counts (139 unique listings, 79 with a numeric price) are hardcoded inputs with no supporting sheet or file, so they cannot be reproduced from this repository.

**Fix:** Add the audit sheet back, or reword the footnote to say where the counts came from.

## 6. Missing listing dates and unusual availability dates

**Where:** DPM-052 to DPM-058 (all Aabason results-page records in Bashundhara R/A).

**What happens:** None of the seven shows a listing date. Their notes give "available from" dates ranging from 12 August 2026 to 31 December 2027 (DPM-053). It is not clear what these dates mean for a flat offered for sale.

**Effect:** These records cannot be placed in the "mostly October to November 2026" listing window, and they are also among the 10 records with condition "Not stated". They are included in all price statistics.

## Data limitations that are not errors

- Mohammadpur (n = 8) and Dhanmondi (n = 9) are below the workbook's own threshold of 10 for comparison.
- 60 of 72 records come from results pages only; seller availability was not confirmed for any record.
- Area comparisons are not adjusted for apartment size (see `docs/methodology.md`).
