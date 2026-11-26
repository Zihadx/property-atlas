# Data dictionary: `02 Master Database`

72 rows, record IDs `DPM-001` to `DPM-072`. Columns A-O and U-Z are typed values; P-T are formulas.

| Col | Field | Description |
|---|---|---|
| A | Record ID | Unique ID (`DPM-nnn`); also the key in `06 Source Register` |
| B | Listing Summary | Title as shown on the portal, lightly normalised |
| C | Area | One of Mirpur, Uttara, Mohammadpur, Dhanmondi, Bashundhara R/A |
| D | Specific Location | Sub-area where stated, otherwise "Not stated" |
| E | Source Platform | bdHousing or Aabason |
| F | Original Listing URL | Page the record was taken from. For results-page records this is the shared results page, not a unique listing URL |
| G | Size (sq ft) | Apartment size |
| H | Bedrooms | As in the portal's structured field |
| I | Bathrooms | As in the portal's structured field |
| J | Condition (Standardized) | Ready, Brand new, Brand new (future handover), Almost ready, Under construction, Used, or Not stated |
| K | Condition Group | Ready or Brand new / Almost Ready or Under Construction / Used / Not stated |
| L | Floor | As stated, otherwise "Not stated" |
| M | Parking Spaces | As stated, otherwise "Not stated". A stated 0 is a real value |
| N | Asking Price (BDT) | Total asking price |
| O | Listed Price per sq ft (BDT) | Rate printed by the portal, or "Not listed" |
| P | Calculated Price per sq ft (BDT) | Formula `=N/G` |
| Q | Listed vs Calculated Gap (%) | Formula; "n/a" when no listed rate |
| R | Pricing Verification Status | Formula: Consistent (within 2%) / Discrepancy / Total only |
| S | Size Segment | Formula: size band |
| T | Outlier Flag | Formula: Tukey fences from `03 Pricing Analysis` C29:C30 |
| U | Listing Date | Date shown by the portal, or "Not stated" |
| V | Research Collection Date | Date the record was collected |
| W | Evidence Level | Results page only / Individual listing page checked |
| X | Data Quality Tier | Tier A (individual page) or Tier B (results page only) |
| Y | Source Record Reference | ID in the earlier research file the record came from |
| Z | Research Notes | Source caveats and flags, free text |

The sheet's used range extends to row 1000 but data ends at row 73.
