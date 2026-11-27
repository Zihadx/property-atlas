"""Recompute the workbook's pricing analysis from data/listings.csv.

What it does
1. Recomputes the summary tables from 03 Pricing Analysis (area, condition group,
   size segment, bedrooms, platform, Tukey fences, correlations) and writes them
   to outputs/.
2. Compares each recomputed figure with the value cached in the workbook and
   reports any mismatch (--no-verify skips this).
3. Runs consistency checks on the listing data itself and writes the findings
   to outputs/data_checks.csv.
4. Draws three charts into docs/images/analysis/ (--no-charts skips this).

Usage (from the repository root):
    python scripts/analyze.py
"""
import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "data" / "Dhaka_Flat_Market_Snapshot_2026.xlsx"
LISTINGS = ROOT / "data" / "listings.csv"
OUT = ROOT / "outputs"
IMAGES = ROOT / "docs" / "images" / "analysis"

AREA_ORDER = ["Mirpur", "Uttara", "Mohammadpur", "Dhanmondi", "Bashundhara R/A"]
SIZE_ORDER = ["Under 1,000", "1,000-1,499", "1,500-1,999", "2,000+"]
CONDITION_ORDER = [
    "Ready or Brand new",
    "Almost Ready or Under Construction",
    "Used",
    "Not stated",
]
SMALL_SAMPLE = 10  # the workbook treats n < 10 as "indicative only"


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def load_listings() -> pd.DataFrame:
    df = pd.read_csv(LISTINGS)
    # Recomputed independently of the workbook's formula columns.
    df["ppsf"] = df["asking_price_bdt"] / df["size_sqft"]
    return df


# --------------------------------------------------------------------------- #
# Summary tables
# --------------------------------------------------------------------------- #
def ppsf_stats(group: pd.DataFrame) -> pd.Series:
    p = group["ppsf"]
    return pd.Series(
        {
            "listings": len(group),
            "median_ppsf": p.median(),
            "average_ppsf": p.mean(),
            "min_ppsf": p.min(),
            "max_ppsf": p.max(),
            "q1_ppsf": p.quantile(0.25),  # linear interpolation = Excel QUARTILE
            "q3_ppsf": p.quantile(0.75),
            "median_size_sqft": group["size_sqft"].median(),
            "median_asking_price_bdt": group["asking_price_bdt"].median(),
        }
    )


def summarise(df: pd.DataFrame, by: str, order: list) -> pd.DataFrame:
    table = df.groupby(by).apply(ppsf_stats, include_groups=False).reindex(order)
    return table


def build_tables(df: pd.DataFrame) -> dict:
    tables = {}

    area = summarise(df, "area", AREA_ORDER)
    all_row = ppsf_stats(df).rename("All areas")
    area = pd.concat([area, all_row.to_frame().T])
    area["sample_note"] = np.where(
        area["listings"] < SMALL_SAMPLE, "Indicative only (n<10)", "Adequate for comparison"
    )
    area.loc["All areas", "sample_note"] = ""
    medians = area.loc[AREA_ORDER, "median_ppsf"]
    area["median_vs_all_area_median"] = area["median_ppsf"] / area.loc["All areas", "median_ppsf"] - 1
    area["median_vs_lowest_area_median"] = area["median_ppsf"] / medians.min() - 1
    tables["area_summary"] = area

    tables["condition_summary"] = summarise(df, "condition_group", CONDITION_ORDER)[
        ["listings", "median_ppsf", "average_ppsf", "min_ppsf", "max_ppsf"]
    ]
    tables["size_segment_summary"] = summarise(df, "size_segment", SIZE_ORDER)[
        ["listings", "median_ppsf", "average_ppsf", "median_asking_price_bdt"]
    ]

    beds = df.assign(bedroom_group=np.where(df["bedrooms"] >= 5, "5+", df["bedrooms"].astype(str)))
    tables["bedroom_summary"] = summarise(beds, "bedroom_group", ["1", "2", "3", "4", "5+"])[
        ["listings", "median_ppsf", "median_size_sqft"]
    ]
    tables["platform_summary"] = summarise(df, "source_platform", ["bdHousing", "Aabason"])[
        ["listings", "median_ppsf"]
    ]
    return tables


def tukey_fences(df: pd.DataFrame) -> dict:
    q1, q3 = df["ppsf"].quantile(0.25), df["ppsf"].quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    flagged = df[(df["ppsf"] > upper) | (df["ppsf"] < lower)]
    return {
        "q1": q1,
        "iqr": iqr,
        "lower_fence": lower,
        "upper_fence": upper,
        "flagged": len(flagged),
        "flagged_ids": list(flagged["record_id"]),
    }


def pricing_relationships(df: pd.DataFrame) -> dict:
    both = df.dropna(subset=["listed_ppsf_bdt"]).copy()
    both["gap"] = both["listed_ppsf_bdt"] / both["ppsf"] - 1
    return {
        "corr_size_vs_price": df["size_sqft"].corr(df["asking_price_bdt"]),
        "corr_size_vs_ppsf": df["size_sqft"].corr(df["ppsf"]),
        "with_listed_rate": len(both),
        "gap_over_2pct": int((both["gap"].abs() > 0.02).sum()),
        "median_abs_gap": both["gap"].abs().median(),
        # What the workbook's formula actually returns: rows without a listed rate
        # count as a gap of 0 (IF(...) returns FALSE, ABS(FALSE) = 0).
        "median_abs_gap_workbook_formula": (
            df["listed_ppsf_bdt"].notna() * (df["listed_ppsf_bdt"] / df["ppsf"] - 1).abs().fillna(0)
        ).median(),
        "consistent_within_2pct": int((both["gap"].abs() <= 0.02).sum()),
    }


# --------------------------------------------------------------------------- #
# Verification against the workbook's cached values
# --------------------------------------------------------------------------- #
def read_sheet(name: str) -> pd.DataFrame:
    return pd.read_excel(WORKBOOK, sheet_name=name, header=None)


def row_by_label(sheet: pd.DataFrame, label: str, start: int = 0) -> pd.Series:
    hits = sheet.index[(sheet[0] == label) & (sheet.index >= start)]
    if len(hits) == 0:
        raise KeyError(f"label {label!r} not found in workbook sheet")
    return sheet.loc[hits[0]]


def verify(tables: dict, fences: dict, rel: dict, df: pd.DataFrame) -> list:
    """Return a list of (check, recomputed, workbook, ok) tuples."""
    sheet = read_sheet("03 Pricing Analysis")
    results = []

    def compare(name, mine, theirs):
        ok = bool(np.isclose(float(mine), float(theirs), rtol=1e-6, atol=1e-9))
        results.append((name, float(mine), float(theirs), ok))

    # Area table: columns B..J in the workbook
    area_cols = ["listings", "median_ppsf", "average_ppsf", "min_ppsf", "max_ppsf",
                 "q1_ppsf", "q3_ppsf", "median_size_sqft", "median_asking_price_bdt"]
    for label in AREA_ORDER + ["All areas"]:
        row = row_by_label(sheet, label)
        for i, col in enumerate(area_cols, start=1):
            compare(f"area/{label}/{col}", tables["area_summary"].loc[label, col], row[i])

    # Condition group: B..G (listings, median, average, min, max)
    for label in CONDITION_ORDER:
        row = row_by_label(sheet, label)
        for i, col in enumerate(["listings", "median_ppsf", "average_ppsf", "min_ppsf", "max_ppsf"], start=1):
            compare(f"condition/{label}/{col}", tables["condition_summary"].loc[label, col], row[i])

    # Size segment: B..E
    for label in SIZE_ORDER:
        row = row_by_label(sheet, label)
        for i, col in enumerate(["listings", "median_ppsf", "average_ppsf", "median_asking_price_bdt"], start=1):
            compare(f"size/{label}/{col}", tables["size_segment_summary"].loc[label, col], row[i])

    # Bedrooms block: starts at the "Bedrooms" header row
    start = sheet.index[sheet[0] == "Bedrooms"][0]
    for offset, label in enumerate(["1", "2", "3", "4", "5+"], start=1):
        row = sheet.loc[start + offset]
        for i, col in enumerate(["listings", "median_ppsf", "median_size_sqft"], start=1):
            compare(f"bedrooms/{label}/{col}", tables["bedroom_summary"].loc[label, col], row[i])

    # Platform
    for label in ["bdHousing", "Aabason"]:
        row = row_by_label(sheet, label)
        for i, col in enumerate(["listings", "median_ppsf"], start=1):
            compare(f"platform/{label}/{col}", tables["platform_summary"].loc[label, col], row[i])

    # Tukey fences
    compare("tukey/q1", fences["q1"], sheet[sheet[1] == "Q1"].iloc[0][2])
    compare("tukey/iqr", fences["iqr"], sheet[sheet[1] == "IQR"].iloc[0][2])
    compare("tukey/lower_fence", fences["lower_fence"], sheet[sheet[1] == "Lower fence"].iloc[0][2])
    compare("tukey/upper_fence", fences["upper_fence"], sheet[sheet[1] == "Upper fence"].iloc[0][2])
    compare("tukey/flagged", fences["flagged"], sheet[sheet[1] == "Listings flagged"].iloc[0][2])

    # Relationships block (label in col A, value in col B)
    rel_map = {
        "Correlation: size vs total asking price": rel["corr_size_vs_price"],
        "Correlation: size vs price per sq ft": rel["corr_size_vs_ppsf"],
        "Listings with both listed and calculated rate": rel["with_listed_rate"],
        "...of which differ by more than 2%": rel["gap_over_2pct"],
        # Reproduces the workbook value only when no-rate rows are counted as 0.
        # See docs/known-issues.md (issue 1).
        "Median absolute gap, listed vs calculated": rel["median_abs_gap_workbook_formula"],
    }
    for label, mine in rel_map.items():
        compare(f"relationships/{label}", mine, row_by_label(sheet, label)[1])

    # Dashboard KPI: listings with verified prices
    dash = read_sheet("05 Dashboard")
    kpi_row = dash.index[dash.eq("Listings With Verified Prices").any(axis=1)][0]
    kpi = dash.loc[kpi_row + 1].dropna().iloc[-1]
    compare("dashboard/listings_with_verified_prices", rel["consistent_within_2pct"], kpi)

    # Formula columns exported from the workbook vs recomputed here
    # Cached values are stored with limited precision; 0.01 BDT per sq ft is ample.
    max_diff = (df["ppsf"] - df["calculated_ppsf_bdt"]).abs().max()
    results.append(("master/calculated_ppsf (max abs diff < 0.01)", float(max_diff), 0.0, max_diff < 0.01))
    return results


# --------------------------------------------------------------------------- #
# Data consistency checks on the listings themselves
# --------------------------------------------------------------------------- #
def data_checks(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    def add(record_id, check, detail):
        rows.append({"record_id": record_id, "check": check, "detail": detail})

    for r in df.itertuples():
        summary = r.listing_summary
        m = re.search(r"(\d+)\s*sqft", summary, flags=re.I)
        if m and int(m.group(1)) != r.size_sqft:
            add(r.record_id, "size_vs_summary", f"summary says {m.group(1)} sqft, size field is {r.size_sqft}")
        m = re.search(r"(\d+)\s*Beds?", summary, flags=re.I)
        if m and int(m.group(1)) != r.bedrooms:
            add(r.record_id, "bedrooms_vs_summary", f"summary says {m.group(1)} beds, bedrooms field is {r.bedrooms}")
        if r.bathrooms > r.bedrooms + 2:
            add(r.record_id, "bathrooms_high", f"{r.bedrooms} bedrooms but {r.bathrooms} bathrooms")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r.listing_date)) and r.listing_date > r.research_collection_date:
            add(r.record_id, "listing_after_collection",
                f"listing date {r.listing_date} is after collection date {r.research_collection_date}")
        if str(r.listing_date) == "Not stated":
            add(r.record_id, "listing_date_missing", "source did not display a listing date")
        m = re.search(r"available from (\d{1,2} \w{3} (\d{4}))", str(r.research_notes))
        if m and int(m.group(2)) > 2026:
            add(r.record_id, "far_future_availability", f"source shows availability from {m.group(1)}")

    # Collection date: master sheet vs source register
    register = pd.read_csv(ROOT / "data" / "source_register.csv")
    merged = df.merge(register[["record_id", "collection_date"]], on="record_id")
    mismatch = merged[merged["research_collection_date"] != merged["collection_date"].astype(str)]
    for r in mismatch.itertuples():
        add(r.record_id, "collection_date_mismatch",
            f"master sheet {r.research_collection_date} vs source register {r.collection_date}")

    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Charts
# --------------------------------------------------------------------------- #
def make_charts(df: pd.DataFrame, tables: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
    IMAGES.mkdir(parents=True, exist_ok=True)
    navy, light = "#1f3864", "#9aa9c7"

    # 1. Median PPSF by area
    area = tables["area_summary"].loc[AREA_ORDER]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [light if n < SMALL_SAMPLE else navy for n in area["listings"]]
    bars = ax.bar(area.index, area["median_ppsf"], color=colors)
    for bar, n, v in zip(bars, area["listings"], area["median_ppsf"]):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 150, f"{v:,.0f}\n(n={int(n)})", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Median asking price per sq ft (BDT)")
    ax.set_title("Median asking price per sq ft by area")
    ax.set_ylim(0, area["median_ppsf"].max() * 1.2)
    ax.text(0.01, 0.97, "Lighter bars: n < 10, indicative only", transform=ax.transAxes, ha="left", va="top", fontsize=8)
    fig.tight_layout()
    fig.savefig(IMAGES / "median_ppsf_by_area.png", dpi=150)
    plt.close(fig)

    # 2. Distribution by area
    fig, ax = plt.subplots(figsize=(8, 4.5))
    data = [df.loc[df["area"] == a, "ppsf"] for a in AREA_ORDER]
    ax.boxplot(data, tick_labels=AREA_ORDER, showfliers=False, medianprops={"color": navy, "linewidth": 2})
    rng = np.random.default_rng(0)  # fixed seed: jitter only, does not alter data
    for i, vals in enumerate(data, start=1):
        ax.scatter(rng.normal(i, 0.06, len(vals)), vals, s=14, alpha=0.6, color=navy)
    ax.set_ylabel("Asking price per sq ft (BDT)")
    ax.set_title("Distribution of asking price per sq ft by area (each dot is one listing)")
    fig.tight_layout()
    fig.savefig(IMAGES / "ppsf_distribution_by_area.png", dpi=150)
    plt.close(fig)

    # 3. Median PPSF by size segment
    seg = tables["size_segment_summary"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(seg.index, seg["median_ppsf"], color=navy)
    for bar, n, v in zip(bars, seg["listings"], seg["median_ppsf"]):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 150, f"{v:,.0f}\n(n={int(n)})", ha="center", va="bottom", fontsize=9)
    ax.set_xlabel("Apartment size (sq ft)")
    ax.set_ylabel("Median asking price per sq ft (BDT)")
    ax.set_title("Median asking price per sq ft by size segment")
    ax.set_ylim(0, seg["median_ppsf"].max() * 1.2)
    fig.tight_layout()
    fig.savefig(IMAGES / "median_ppsf_by_size_segment.png", dpi=150)
    plt.close(fig)


# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-verify", action="store_true", help="skip comparison with the workbook")
    parser.add_argument("--no-charts", action="store_true", help="skip chart generation")
    args = parser.parse_args()

    df = load_listings()
    OUT.mkdir(exist_ok=True)

    tables = build_tables(df)
    for name, table in tables.items():
        table.round(4).to_csv(OUT / f"{name}.csv", index_label=table.index.name or "group")
    fences = tukey_fences(df)
    rel = pricing_relationships(df)
    pd.Series({**{k: v for k, v in fences.items() if k != "flagged_ids"}, **rel}).to_csv(
        OUT / "overall_metrics.csv", header=["value"], index_label="metric"
    )
    checks = data_checks(df)
    checks.to_csv(OUT / "data_checks.csv", index=False)

    print(f"Listings: {len(df)} | median asking price per sq ft (all areas): {df['ppsf'].median():,.0f} BDT")
    print(f"Outliers by Tukey fences: {fences['flagged']} {fences['flagged_ids']}")
    print(f"Median absolute listed-vs-calculated gap: {rel['median_abs_gap']:.4%} over "
          f"{rel['with_listed_rate']} listings (workbook reports "
          f"{rel['median_abs_gap_workbook_formula']:.4%} because it counts no-rate rows as 0)")
    print(f"Data consistency findings: {len(checks)} (see outputs/data_checks.csv)")
    print(checks.groupby("check").size().to_string())

    status = 0
    if not args.no_verify:
        results = verify(tables, fences, rel, df)
        failed = [r for r in results if not r[3]]
        print(f"\nWorkbook verification: {len(results) - len(failed)}/{len(results)} figures match")
        for name, mine, theirs, _ in failed:
            print(f"  MISMATCH {name}: recomputed={mine} workbook={theirs}")
        status = 1 if failed else 0

    if not args.no_charts:
        make_charts(df, tables)
        print(f"Charts written to {IMAGES.relative_to(ROOT)}/")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
