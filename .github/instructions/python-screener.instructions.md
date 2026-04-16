---
description: "Use when editing Python files in this stock screener project. Covers code style, data conventions, and financial data handling patterns."
applyTo: "**/*.py"
---

# Python Code Guidelines

## Style
- Python 3.10+ — use `X | Y` union types, not `Union[X, Y]`
- Use `np.nan` for missing values in DataFrames, never `None`
- All monetary values in local currency (INR for NSE, CAD for TSX)
- Market cap in Crores (₹ Cr) for Indian stocks

## Data Patterns
- yfinance returns columns newest-first (descending dates)
- Always guard against missing data: check `pd.isna()` before calculations
- Use `_safe_divide()` from `data_fetcher` to avoid division by zero
- CAGR formula: `((newest / oldest) ** (1/n) - 1) * 100`

## Financial Conventions
- ROCE = EBIT / Capital Employed (Total Assets − Current Liabilities)
- Graham Number = √(22.5 × EPS × Book Value per Share)
- Margin of Safety = (Intrinsic − Price) / Intrinsic × 100%
- Positive MoS = undervalued; Negative = overvalued
- Owner Earnings = Net Income + D&A − Maintenance CapEx (70% of total capex)
- Piotroski F-Score = 9 binary tests (profitability, leverage, efficiency)
- Altman Z-Score = 1.2*WC/TA + 1.4*RE/TA + 3.3*EBIT/TA + 0.6*MCap/TL + Rev/TA
- FCF Conversion = FCF / Net Income (>0.8 good)
- Incremental ROCE = delta NOPAT / delta Capital Employed

## Scoring
- 10 dimensions, each scored 0–10, total 0–100
- Dimensions: Valuation, Profitability, Growth Quality, Financial Health, Cash Flow, Business Moat, Earnings Quality, Institutional, Sector & Macro, Management
- Filter 11 (Red Flags) can trigger instant REJECT regardless of score
- Verdicts: GEM (≥75), STRONG (65–74), ACCEPTABLE (55–64), WATCHLIST (40–54), REJECT (<40)
- See `config.py` → `FILTER_REFERENCE` for all definitions and `analyzer.py → score_stock_full()`
