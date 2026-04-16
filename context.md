# Stock Screener — Project Context

## Goal

Find **undervalued gem stocks** on the NSE (India) with huge growth potential,
sector by sector. Later extend to TSX (Canada).

We think like investors at **Goldman Sachs** and **BlackRock** — data-driven,
disciplined, and focused on long-term compounding.

---

## Investment Philosophy (Who We Follow)

### Warren Buffett — Value + Moat + Owner Earnings
- Buy wonderful companies at **fair prices**, not fair companies at wonderful prices.
- Look for **economic moats**: brand power, network effects, switching costs,
  cost advantages, patents/regulatory licenses.
- Demand a **margin of safety** — intrinsic value must exceed market price.
- Prefer businesses with **ROE > 15%** sustained over many years.
- Low or zero debt. Management must be honest capital allocators.
- **Owner Earnings** = Net Income + D&A − Maintenance CapEx.

### Anand Srinivasan — Systematic Compounders
- Follow **numbers**, not narratives. Unit economics matter.
- Cash flow > reported earnings. Free cash flow is king.
- Prefer companies with **pricing power** (can raise prices without losing demand).
- **PEG < 1** is ideal — growth at a reasonable price.

### Coffee Can Investing (Saurabh Mukherjea)
- Revenue CAGR ≥ 10%, ROCE ≥ 15%, D/E ≤ 1.0 — all sustained.
- Buy, forget, and hold for 10+ years.

### Piotroski F-Score — Earnings Quality
- 9 binary tests covering profitability, leverage, and operating efficiency.
- Scores 8–9 outperform by 7.5% annually (Stanford research).

### Altman Z-Score — Financial Distress
- 5-factor formula predicting bankruptcy within 2 years.
- Z > 2.99 = safe, 1.81–2.99 = grey zone, < 1.81 = distress.

### Joel Greenblatt — Magic Formula
- Combined rank of Earnings Yield (EBIT/EV) and ROIC. Cross-check, not scoring input.

### Pat Dorsey — Moat Trend
- 7 moat types. Moat TREND matters: widening (rising ROCE + margins) vs
  eroding (declining ROCE + growing revenue = competing on price).

### Aswath Damodaran — Reverse DCF
- Solve for the growth rate the market implies. If implied >> historical, stock overpriced.

### Michael Mauboussin — Expectations Investing
- The stock price embeds growth expectations. Compare implied vs. achievable growth.
- Base rates matter — few companies sustain >15% growth for a decade.

---

## Screening Filters — 10-Filter, 100-Point System

### Filter 1: Valuation (/10)
Sector-aware PE/PB scoring. PEG, EV/EBITDA, P/S ratios.
Graham Number and company-specific DCF intrinsic value.
Reverse DCF to check what growth the market implies.
Margin of Safety: (Intrinsic − Price) / Intrinsic × 100%.

### Filter 2: Profitability (/10)
ROE, ROCE, ROA, operating margin, net margin, owner earnings yield.

### Filter 3: Growth Quality (/10)
Revenue/profit CAGR (3-year), incremental ROCE (ROIIC), quarterly trend,
earnings consistency (volatility of EPS growth).

### Filter 4: Financial Health (/10)
Altman Z-Score, D/E, interest coverage, current ratio.

### Filter 5: Cash Flow (/10)
FCF positive, FCF conversion (FCF/NI), FCF yield, OCF/NI, capex intensity.

### Filter 6: Business Moat (/10)
7 moat types, ROCE strength, operating margin, moat trend (widening/stable/eroding).
Wide ≥ 7pts, Narrow ≥ 4pts, None < 4pts.

### Filter 7: Earnings Quality (/10)
Piotroski F-Score (0–9), accrual ratio, OCF > NI, margin trend.

### Filter 8: Institutional Backing (/10)
Institutional and insider holdings, analyst recommendation, target price upside.

### Filter 9: Sector & Macro (/10)
Tailwinds, threats, diversification, cyclicality, company growth premium.

### Filter 10: Management Quality (/10)
ROCE consistency, payout ratio, debt discipline, margin trend, dilution, FCF.

### Filter 11: Red Flags — Instant Rejection
| Red Flag | Threshold |
|----------|-----------|
| PE > 60 | Extreme overvaluation |
| D/E > 2.0 | Overleveraged |
| Interest Coverage < 1.5x | Debt stress |
| Profit declining 3+ quarters | Deteriorating business |
| Negative free cash flow | Burning cash |
| Market Cap < ₹500 Cr | Micro-cap risk |
| Current year net loss | Unprofitable |
| Altman Z < 1.81 | Bankruptcy risk |
| Piotroski F ≤ 2 | Worst quality |
| Accrual Ratio > 25% | Accounting fraud risk |

**Key insight**: Red Flag 11 is binary. A stock scoring 79.8/100 can still be
REJECTED if any single red flag triggers (e.g., KPIT Technologies — excellent
fundamentals but profit declining 3 consecutive quarters = instant REJECT).
This is by design — conservative bias.

---

## Scoring System (100-Point, 10 Dimensions × 10)

| Dimension | Max | What's scored |
|-----------|-----|---------------|
| Valuation | /10 | Sector PE/PB, PEG, EV/EBITDA, P/S, MoS, Reverse DCF |
| Profitability | /10 | ROE, ROCE, ROA, margins, owner earnings yield |
| Growth Quality | /10 | Revenue/profit CAGR, incremental ROCE, consistency |
| Financial Health | /10 | Altman Z, D/E, interest coverage, current ratio |
| Cash Flow | /10 | FCF yield, FCF conversion, OCF/NI, capex intensity |
| Business Moat | /10 | 7 moat types, moat trend, ROCE durability |
| Earnings Quality | /10 | Piotroski F-Score, accrual ratio, cash-backing |
| Institutional | /10 | Holdings, analyst targets, insider activity |
| Sector & Macro | /10 | Tailwinds, threats, diversification, cyclicality |
| Management | /10 | Capital allocation, payout, discipline, dilution |
| **Total** | **/100** | |

### Verdicts
| Verdict | Score | Action |
|---------|-------|--------|
| **GEM** | ≥ 75/100 | Strong Buy — highest conviction |
| **STRONG** | 65–74/100 | Buy / Accumulate |
| **ACCEPTABLE** | 55–64/100 | Hold |
| **WATCHLIST** | 40–54/100 | Monitor for better entry |
| **REJECT** | < 40/100 | Avoid entirely |

---

## Intrinsic Value Models

1. **Graham Number** = √(22.5 × EPS × Book Value per Share)
2. **Company-Specific DCF** = 10-year FCF projection using revenue CAGR (capped 3–25%) with growth fade after year 5, 12% discount rate, 3% terminal growth
3. **Reverse DCF** = Binary search for market-implied growth rate
4. **Margin of Safety** = (Intrinsic Value − Price) / Intrinsic Value × 100%

---

## 7 Moat Types

| Type | Description |
|------|-------------|
| Cost Advantage | Lowest cost producer / economies of scale |
| Network Effect | Value increases with more users |
| Switching Cost | Painful for customers to switch |
| Intangible Assets | Brand, patents, IP, licenses |
| Regulatory | Government license / legal monopoly |
| Distribution | Unmatched distribution network |
| Data Advantage | Proprietary data creating feedback loops |

Moat rating: **Wide** ≥ 7pts, **Narrow** ≥ 4pts, **None** < 4pts.
Moat trend: **widening** (rising ROCE + margins) / **stable** / **eroding** (declining ROCE).

---

## Data Accuracy — 3-Tier System

All metrics are sourced with a quality tier:

| Tier | Source | Reliability | Examples |
|------|--------|-------------|----------|
| **Tier 1** | Direct from yfinance `.info` API | Highest for recent data | PE, PB, dividend yield, analyst target |
| **Tier 2** | Computed from audited financial statements | Most reliable for derived ratios | ROCE, Piotroski, Altman Z, D/E, FCF, margins |
| **Tier 3** | Derived from other computed values | Dependent on Tier 2 quality | CAGR, PEG, trends, incremental ROCE |

Each metric has a fallback chain (e.g., PE: API → price/EPS computation).
Data source tracking is available via `_src` dict in fetched data.

---

## Configuration Thresholds

### Profitability
| Metric | Minimum | Excellent |
|--------|---------|-----------|
| ROE | 12% | 25% |
| ROCE | 15% | 25% |
| ROA | 5% | 12% |
| Operating Margin | 12% | 25% |
| Net Margin | 8% | 20% |

### Growth
| Metric | Minimum | Excellent |
|--------|---------|-----------|
| Revenue CAGR (3Y) | 10% | 20% |
| Profit CAGR (3Y) | 12% | 25% |
| Incremental ROCE | 12% | 25% |

### Financial Health
| Metric | Threshold |
|--------|-----------|
| D/E Max (normal) | 1.0 |
| D/E High | 1.5 |
| Current Ratio Min | 1.0 |
| Interest Coverage Min | 3x |
| Altman Z Safe | > 2.99 |
| Altman Z Distress | < 1.81 |

### Cash Flow
| Metric | Minimum | Good |
|--------|---------|------|
| FCF Conversion | 0.6 | 0.9 |
| FCF Yield | 2% | 6% |
| OCF/NI | 0.8 | 1.0+ |

### DCF Parameters
| Parameter | Value |
|-----------|-------|
| Discount Rate | 12% |
| Terminal Growth | 3% |
| Projection Years | 10 |
| Growth Fade Start | Year 5 |
| Margin of Safety Threshold | 25% |

---

## Sectors Covered (NSE India) — 13 Sectors, ~510 Stocks

| # | Sector | Stocks | Notes |
|---|--------|--------|-------|
| 1 | **IT** | ~46 | TCS, Infosys, HCL, Wipro, LTIM, Persistent, Coforge, KPIT, eClerx, OFSS, Naukri… |
| 2 | **Pharma & Healthcare** | ~45 | Sun Pharma, Dr Reddy, Cipla, Divi's, Zydus, Apollo, Max Health, Biocon, Lupin… |
| 3 | **Banking & Finance** | ~52 | HDFC, ICICI, Kotak, Axis, SBI, Bajaj Finance, PB Fintech, Paytm, KFINTECH, LIC… |
| 4 | **FMCG** | ~33 | HUL, ITC, Nestle, Britannia, Dabur, Marico, Godrej CP, Emami, Patanjali, Bikaji… |
| 5 | **Auto & Ancillaries** | ~33 | Maruti, M&M, Tata Motors, Bajaj Auto, TVS, Eicher, MRF, Motherson, Bosch… |
| 6 | **Infrastructure & Capital Goods** | ~38 | L&T, ABB, Siemens, HAL, BEL, IRCTC, Kaynes, Cochin Ship, Mazagon Dock… |
| 7 | **Energy & Power** | ~35 | Reliance, NTPC, Power Grid, Adani Green, Tata Power, ONGC, JSW Energy, IEX… |
| 8 | **Chemicals & Materials** | ~48 | Pidilite, Asian Paints, SRF, PI Industries, UltraTech, Shree Cement, ACC… |
| 9 | **Telecom & Media** | ~23 | Bharti Airtel, Indus Towers, Sun TV, Nazara, Saregama, Tata Comm… |
| 10 | **Metals & Mining** | ~28 | Tata Steel, JSW Steel, Hindalco, Vedanta, NMDC, Hindustan Zinc, APL Apollo… |
| 11 | **Consumer Discretionary** | ~42 | Titan, Trent, DMart, Jubilant, Page, Havells, Polycab, Dixon, Zomato, Nykaa… |
| 12 | **Real Estate** | ~16 | DLF, Godrej Properties, Oberoi, Prestige, Lodha, Brigade, Embassy REIT… |
| 13 | **Textiles & Apparel** | ~18 | Trident, Welspun, KPR Mill, Gokaldas, Kitex, Arvind, Dollar, Rupa… |

### Sector PE Norms (avg / cheap / expensive)
| Sector | Avg PE | Cheap | Expensive |
|--------|--------|-------|-----------|
| IT | 28 | 20 | 38 |
| Pharma & Healthcare | 30 | 22 | 42 |
| Banking & Finance | 15 | 10 | 22 |
| FMCG | 45 | 30 | 60 |
| Auto & Ancillaries | 22 | 14 | 30 |
| Infrastructure | 25 | 16 | 35 |
| Energy & Power | 12 | 8 | 18 |
| Chemicals & Materials | 30 | 20 | 42 |
| Telecom & Media | 20 | 12 | 30 |
| Metals & Mining | 10 | 6 | 16 |
| Consumer Discretionary | 45 | 28 | 65 |
| Real Estate | 25 | 15 | 40 |
| Textiles & Apparel | 18 | 10 | 28 |

### Cyclical Sectors
Metals & Mining, Energy & Power, Auto & Ancillaries, Real Estate.

---

## Key Learnings & Design Decisions

### Data Quality
- yfinance `.info` API is unreliable for some metrics (especially historical).
  Always cross-check with computed values from financial statements.
- CAGR requires at least 2 data points. Many small-cap stocks have incomplete history.
- `np.nan` must be handled everywhere — both in scoring and in HTML `data-val` attributes.
  Use sentinel values (e.g., `-999`) in HTML attributes instead of `"nan"` for proper sorting.

### Scoring Philosophy
- **Conservative bias**: when in doubt, pass. A missed opportunity beats a loss.
- **Sector context matters**: PE of 30 is expensive for banking (avg 15) but cheap for FMCG (avg 45).
- **Moat first, valuation second**: a cheap stock without a moat is a value trap.
- **10-year lens**: short-term price doesn't matter if the business compounds.
- **Red flags override everything**: even an 80/100 stock gets REJECTED if it has a binary red flag.

### Coverage
- Started with 10 sectors / 100 stocks → expanded to 13 sectors / ~510 stocks.
- Goal: cover NSE 500 + mid-cap opportunities for comprehensive gem discovery.
- Duplicate tickers across sectors removed (e.g., RECLTD in Banking only, PAGEIND in Consumer Disc only).

### HTML Report
- Dark theme (GitHub-inspired), 6 tabs: Dashboard, Rankings, Top Picks, By Sector, All Stocks, Framework.
- Multi-column sort on Rankings tab: Click to sort, Shift+Click for secondary/tertiary sorts.
- Stock cards with all 10 dimension scores, intrinsic value comparisons, moat details, red flags.
- Sort arrows with priority badges for multi-column sorting.

---

## Tech Stack

- **Python 3.10+** — Core language
- **yfinance** — Free market data API
- **pandas / numpy** — Data crunching
- **HTML report** — Final output with tabbed dashboard

## Output

- `report.html` — Full HTML report with dashboard, rankings, stock cards, and framework reference
- Console output — Per-sector top 3 and final verdict summary
