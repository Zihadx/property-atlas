"""Export the Master Database and Source Register sheets of the workbook to CSV.

The workbook is the primary record. This script only reshapes it into flat files
that are easy to load with pandas. Formula columns are exported as the values
cached in the workbook; analyze.py recomputes them independently as a check.

Usage (from the repository root):
    python scripts/export_data.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "data" / "Dhaka_Flat_Market_Snapshot_2026.xlsx"

MASTER_COLUMNS = {
    "Record ID": "record_id",
    "Listing Summary": "listing_summary",
    "Area": "area",
    "Specific Location": "specific_location",
    "Source Platform": "source_platform",
    "Original Listing URL": "listing_url",
    "Size (sq ft)": "size_sqft",
    "Bedrooms": "bedrooms",
    "Bathrooms": "bathrooms",
    "Condition (Standardized)": "condition",
    "Condition Group": "condition_group",
    "Floor": "floor",
    "Parking Spaces": "parking_spaces",
    "Asking Price (BDT)": "asking_price_bdt",
    "Listed Price per sq ft (BDT)": "listed_ppsf_bdt",
    "Calculated Price per sq ft (BDT)": "calculated_ppsf_bdt",
    "Listed vs Calculated Gap (%)": "listed_vs_calculated_gap",
    "Pricing Verification Status": "pricing_verification_status",
    "Size Segment": "size_segment",
    "Outlier Flag": "outlier_flag",
    "Listing Date": "listing_date",
    "Research Collection Date": "research_collection_date",
    "Evidence Level": "evidence_level",
    "Data Quality Tier": "data_quality_tier",
    "Source Record Reference": "source_record_reference",
    "Research Notes": "research_notes",
}

REGISTER_COLUMNS = {
    "Record ID": "record_id",
    "Source Platform": "source_platform",
    "Source URL": "source_url",
    "Source Information": "source_information",
    "Collection Date": "collection_date",
    "Listing Date": "listing_date",
    "Verification Status": "verification_status",
    "Research Notes": "research_notes",
}


def main() -> None:
    master = pd.read_excel(WORKBOOK, sheet_name="02 Master Database", nrows=72)
    master = master.dropna(how="all").rename(columns=MASTER_COLUMNS)
    # "Not listed" / "n/a" become blank so the numeric columns load as numbers.
    master["listed_ppsf_bdt"] = pd.to_numeric(master["listed_ppsf_bdt"], errors="coerce")
    master["listed_vs_calculated_gap"] = pd.to_numeric(
        master["listed_vs_calculated_gap"], errors="coerce"
    )
    master["research_collection_date"] = pd.to_datetime(
        master["research_collection_date"]
    ).dt.strftime("%Y-%m-%d")
    master.to_csv(ROOT / "data" / "listings.csv", index=False)

    # The register has title rows above the header, so find the header row first.
    raw = pd.read_excel(WORKBOOK, sheet_name="06 Source Register", header=None)
    header_row = raw.index[raw[0] == "Record ID"][0]
    register = pd.read_excel(WORKBOOK, sheet_name="06 Source Register", header=header_row)
    register = register.dropna(how="all").rename(columns=REGISTER_COLUMNS)
    register = register[register["record_id"].astype(str).str.startswith("DPM-")]
    register.to_csv(ROOT / "data" / "source_register.csv", index=False)

    print(f"listings.csv: {len(master)} rows, source_register.csv: {len(register)} rows")


if __name__ == "__main__":
    main()
