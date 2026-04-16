"""
Stock Screener — Main Orchestrator (HTML-only output)
=====================================================
Fetches data per sector, runs 10-filter analysis, generates HTML report.

Usage:
    python screener.py                          # Full run, all sectors
    python screener.py --sector "IT"            # Single sector
"""

import argparse
import sys
import time
import pandas as pd

from config import NSE_SECTORS
from data_fetcher import fetch_sector_data
from analyzer import analyze_dataframe
from report_generator import build_report


def run_screener(sectors: dict, selected_sector: str | None = None, slow: bool = False):
    """Run the full screening pipeline and generate HTML report."""

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

    # Sort final
    all_data = all_data.sort_values("total_score", ascending=False).reset_index(drop=True)

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
    args = parser.parse_args()

    run_screener(NSE_SECTORS, selected_sector=args.sector, slow=args.slow)
