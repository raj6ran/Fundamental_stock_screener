# NSE Stock Screener

A fundamental stock screener for **NSE India** using a **10-filter, 100-point scoring system**.
Screens ~510 stocks across 13 sectors with investment principles from Buffett, Mukherjea, Piotroski, Greenblatt, Dorsey, Altman, Damodaran, and Mauboussin.

## Quick Start

```bash
pip install -r requirements.txt

python screener.py                          # All 13 sectors → report.html
python screener.py --sector "IT"            # Single sector
```

Open `report.html` in a browser to view the interactive report.

## How It Works

Every run pulls **live data** from yfinance — nothing is cached. You can re-run after a week, a month, or a year and it will fetch the latest financials automatically.

1. `screener.py` iterates through all sectors
2. `data_fetcher.py` fetches live data for each stock (ThreadPoolExecutor, 5 workers)
3. `analyzer.py` scores each stock across 10 dimensions (0–10 each, 100 total)
4. `report_generator.py` produces a 6-tab HTML report

## Scoring System (100 Points)

| Dimension | /10 | What's Scored |
|-----------|-----|---------------|
| Valuation | /10 | Sector PE/PB, PEG, EV/EBITDA, P/S, Margin of Safety, Reverse DCF |
| Profitability | /10 | ROE, ROCE, ROA, margins, owner earnings yield |
| Growth Quality | /10 | Revenue/profit CAGR, incremental ROCE, consistency |
| Financial Health | /10 | Altman Z, D/E, interest coverage, current ratio |
| Cash Flow | /10 | FCF yield, FCF conversion, OCF/NI, capex intensity |
| Business Moat | /10 | 7 moat types, moat trend, ROCE durability |
| Earnings Quality | /10 | Piotroski F-Score, accrual ratio, cash-backing |
| Institutional | /10 | Holdings, analyst targets, insider activity |
| Sector & Macro | /10 | Tailwinds, threats, diversification, cyclicality |
| Management | /10 | Capital allocation, payout, discipline, dilution |

### Verdicts

| Verdict | Score | Action |
|---------|-------|--------|
| **GEM** | ≥ 75 | Strong Buy — highest conviction |
| **STRONG** | 65–74 | Buy / Accumulate |
| **ACCEPTABLE** | 55–64 | Hold |
| **WATCHLIST** | 40–54 | Monitor for better entry |
| **REJECT** | < 40 | Avoid |

### Red Flags (Filter 11) — Instant REJECT

Any of these triggers an automatic REJECT regardless of score:

- PE > 60, D/E > 2.0, Interest Coverage < 1.5x
- Profit declining 3+ quarters, negative FCF, net loss
- Market Cap < ₹500 Cr, Altman Z < 1.81, Piotroski ≤ 2, Accrual Ratio > 25%

## Analyse a Single Stock

```python
from data_fetcher import fetch_stock_info
from analyzer import score_stock_full, graham_number, dcf_intrinsic_value, margin_of_safety

data = fetch_stock_info("ZYDUSLIFE.NS")
scores = score_stock_full(data, "Pharma & Healthcare")
print(scores["total_score"], scores["verdict"], scores["moat"], scores["red_flags"])

gn = graham_number(data["eps"], data["book_value"])
print(f"Graham Number: ₹{gn:.0f}, MoS: {margin_of_safety(data['price'], gn):.1f}%")
```

## Reading the Report

- **Rankings tab** — Click column headers to sort. Shift+Click for multi-column sort.
- **Score bars** — Shows which of the 10 dimensions is weak.
- **Red flags** — Even an 80/100 stock gets REJECTED if a flag triggers.
- **Moat** — Wide/Narrow/None + trend (▲ widening, ▬ stable, ▼ eroding).
- **MoS** — Positive = undervalued, Negative = overvalued.
- **Coffee Can ☕** — Meets 10% rev CAGR + 15% ROCE + D/E ≤ 1.0.

## Add New Stocks

In `config.py` → `NSE_SECTORS`, find the sector and append tickers:

```python
"stocks": ["EXISTING.NS", ..., "NEWSTOCK.NS"],
```

Run `python screener.py --sector "Sector Name"` to test.

## Add a New Sector

Update ALL of these in `config.py` (miss one = crash):

```
NSE_SECTORS["New Sector"]           → stocks list + description
SECTOR_PE_NORMS["New Sector"]       → {"avg": X, "cheap": Y, "expensive": Z}
SECTOR_PB_NORMS["New Sector"]       → {"cheap": X, "avg": Y, "expensive": Z}
SECTOR_MOAT_HINTS["New Sector"]     → ["moat_type1", "moat_type2"]
SECTOR_TAILWINDS["New Sector"]      → 1–9 score
SECTOR_DIVERSIFICATION["New Sector"]→ 1–9 score
SECTOR_THREATS["New Sector"]        → 1–9 score
```

If cyclical, add to `CYCLICAL_SECTORS` set.

## Sectors Covered (13)

IT, Pharma & Healthcare, Banking & Finance, FMCG, Auto & Ancillaries, Infrastructure & Capital Goods, Energy & Power, Chemicals & Materials, Telecom & Media, Metals & Mining, Consumer Discretionary, Real Estate, Textiles & Apparel

## Key Files

| File | Purpose |
|------|---------|
| `config.py` | Stocks, sectors, thresholds, scoring definitions |
| `data_fetcher.py` | yfinance data retrieval, Piotroski, Altman Z computation |
| `analyzer.py` | 10-dimension scoring, intrinsic value, moat, Magic Formula |
| `screener.py` | CLI orchestrator |
| `report_generator.py` | HTML report generation |
| `context.md` | Full project goals, filters, learnings |
| `claude.md` | AI agent instructions |

## Data Notes

- **Live data**: Every run fetches fresh from yfinance. No cache.
- **3-tier accuracy**: Tier 1 (API), Tier 2 (computed from statements), Tier 3 (derived).
- **Financial lag**: Statements reflect most recent filings (1–2 quarters behind). Price is real-time.
- **Maintenance**: Delisted/acquired tickers and new IPOs need manual updates in `config.py`.

## Golden Rules

1. **Never trust a single metric.** The 10-dimension score exists for a reason.
2. **Red flags override scores.** Conservative bias saves capital.
3. **Sector norms matter.** PE 30 is cheap for FMCG, expensive for banking.
4. **Moat first, valuation second.** Cheap + no moat = value trap.
5. **Re-run quarterly.** Catch moat erosion and deteriorating fundamentals early.
