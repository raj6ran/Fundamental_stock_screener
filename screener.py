"""
Stock Screener — Main Orchestrator (HTML-only output)
=====================================================
Fetches data per sector, runs 10-filter analysis, generates HTML report.

Usage:
    python screener.py                          # Full run, all sectors
    python screener.py --sector "IT"            # Single sector
    python screener.py --sector "IT" --export-csv sector_data/  # Export analyzed CSV
    python screener.py --combine sector_data/   # Combine CSVs and generate report
"""

import argparse
import glob
import os
import sys
import time
import pandas as pd

from config import NSE_SECTORS
from data_fetcher import fetch_sector_data
from analyzer import analyze_dataframe
from report_generator import build_report


def run_screener(
    sectors: dict,
    selected_sector: str | None = None,
    slow: bool = False,
    export_csv_dir: str | None = None,
):
    """Run the screening pipeline. Optionally export sector CSV instead of HTML."""

    all_dfs: list[pd.DataFrame] = []

    sector_items = sectors.items()
    if selected_sector:
        key = next((k for k in sectors if k.lower() == selected_sector.lower()), None)
        if not key:
            print(f"Sector '{selected_sector}' not found. Available: {list(sectors.keys())}")
            sys.exit(1)
        sector_items = [(key, sectors[key])]

    for idx, (sector_name, sector_info) in enumerate(sector_items):
        if idx > 0:
            time.sleep(2)  # cooldown between sectors to avoid rate limits
        print(f"\n>>> Screening: {sector_name}")
        print(f"    {sector_info['description']} ({len(sector_info['stocks'])} stocks)")

        df = fetch_sector_data(sector_name, sector_info["stocks"], slow_mode=slow)
        if df.empty:
            print(f"    No data retrieved for {sector_name}")
            continue

        analyzed = analyze_dataframe(df)
        all_dfs.append(analyzed)

        # Print console summary
        for i in range(min(3, len(analyzed))):
            row = analyzed.iloc[i]
            v = row.get("verdict", "?")
            t = row.get("total_score", 0)
            print(f"    {row.get('ticker','?'):>15s}  {t:5.1f}/100  {v}")

    if not all_dfs:
        print("\nNo data retrieved. Check network connection.")
        sys.exit(1)

    all_data = pd.concat(all_dfs, ignore_index=True)

    # If exporting CSV for CI matrix jobs, write and exit early
    if export_csv_dir:
        os.makedirs(export_csv_dir, exist_ok=True)
        safe_name = (selected_sector or "all").replace(" ", "_").replace("&", "and")
        csv_path = os.path.join(export_csv_dir, f"{safe_name}.csv")
        all_data.to_csv(csv_path, index=False)
        print(f"\n  Exported {len(all_data)} stocks to {csv_path}")
        return

    _finalize_and_report(all_data)


def combine_csvs(csv_dir: str):
    """Combine sector CSVs from parallel CI jobs into a single HTML report."""
    csv_files = sorted(glob.glob(os.path.join(csv_dir, "*.csv")))
    if not csv_files:
        print(f"No CSV files found in {csv_dir}")
        sys.exit(1)

    print(f"Combining {len(csv_files)} sector CSV files...")
    dfs = []
    for f in csv_files:
        df = pd.read_csv(f)
        print(f"  {os.path.basename(f)}: {len(df)} stocks")
        dfs.append(df)

    all_data = pd.concat(dfs, ignore_index=True)
    _finalize_and_report(all_data)


def _finalize_and_report(all_data: pd.DataFrame):
    """Deduplicate, print summary, and generate HTML report."""
    # Deduplicate: keep the highest-scoring entry when a stock appears in multiple sectors
    all_data = all_data.sort_values("total_score", ascending=False)
    before = len(all_data)
    all_data = all_data.drop_duplicates(subset="ticker", keep="first").reset_index(drop=True)
    duped = before - len(all_data)
    if duped:
        print(f"    (Removed {duped} duplicate ticker entries, kept highest score)")

    # Console summary
    total = len(all_data)
    gems = len(all_data[all_data["verdict"] == "GEM"])
    strong = len(all_data[all_data["verdict"] == "STRONG"])
    acceptable = len(all_data[all_data["verdict"] == "ACCEPTABLE"])
    watchlist = len(all_data[all_data["verdict"] == "WATCHLIST"])
    rejected = len(all_data[all_data["verdict"] == "REJECT"])

    print(f"\n{'='*60}")
    print(f"  SCREENING COMPLETE: {total} stocks across {all_data['sector'].nunique()} sectors")
    print(f"  GEM: {gems} | STRONG: {strong} | ACCEPTABLE: {acceptable} | WATCHLIST: {watchlist} | REJECT: {rejected}")
    print(f"{'='*60}")

    # Generate HTML report
    build_report(all_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NSE Stock Screener — 100-Point System")
    parser.add_argument("--sector", type=str, default=None, help="Screen a single sector")
    parser.add_argument("--slow", action="store_true", help="Fetch stocks sequentially with 3s delay (avoids rate limits)")
    parser.add_argument("--export-csv", type=str, default=None, metavar="DIR",
                        help="Export analyzed data as CSV to DIR (for CI matrix jobs)")
    parser.add_argument("--combine", type=str, default=None, metavar="DIR",
                        help="Combine sector CSVs from DIR and generate HTML report")
    args = parser.parse_args()

    if args.combine:
        combine_csvs(args.combine)
    else:
        run_screener(NSE_SECTORS, selected_sector=args.sector, slow=args.slow,
                     export_csv_dir=args.export_csv)
