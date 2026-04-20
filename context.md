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

## Sectors Covered (NSE India) — 22 Sectors, ~730 Stocks

| # | Sector | Stocks | Notes |
|---|--------|--------|-------|
| 1 | **Automobile and Auto Components** | ~49 | Maruti, M&M, Tata Motors, Bajaj Auto, TVS, Eicher, MRF, Motherson, Bosch… |
| 2 | **Capital Goods** | ~50 | L&T, ABB, Siemens, HAL, BEL, Kaynes, Cochin Ship, Mazagon Dock, IRCTC… |
| 3 | **Chemicals** | ~48 | Pidilite, Asian Paints, SRF, PI Industries, Atul, Navin Fluorine, Deepak Nitrite… |
| 4 | **Construction Materials** | ~43 | UltraTech, Shree Cement, Ambuja, ACC, Dalmia, Astral, Kajaria, APL Apollo… |
| 5 | **Consumer Durables** | ~46 | Titan, Havells, Polycab, Dixon, Blue Star, Crompton, Voltas, Kalyan Jewellers… |
| 6 | **Consumer Services** | ~45 | Jubilant Food, Zomato, IRCTC, Naukri, Delhivery, PVR INOX, Wonderla… |
| 7 | **Diversified** | ~50 | Reliance, Adani Enterprises, ITC, L&T, Grasim, 3M India, Siemens… |
| 8 | **Fast Moving Consumer Goods** | ~46 | HUL, ITC, Nestle, Britannia, Dabur, Marico, Godrej CP, Colgate, Emami… |
| 9 | **Fertilizers & Agrochemicals** | ~50 | Coromandel, Chambal, GNFC, PI Industries, UPL, Rallis, Dhanuka, Bayer… |
| 10 | **Financial Services** | ~63 | HDFC Bank, ICICI, Kotak, Axis, SBI, Bajaj Finance, LIC, HDFC AMC, BSE, CDSL… |
| 11 | **Forest Materials** | ~48 | JK Paper, TNPL, UFlex, EPL, Century Ply, Greenply, Cosmo Films… |
| 12 | **Healthcare** | ~49 | Sun Pharma, Dr Reddy, Cipla, Divi's, Zydus, Apollo Hospitals, Max Health… |
| 13 | **Information Technology** | ~50 | TCS, Infosys, HCL, Wipro, LTIM, Persistent, Coforge, KPIT, Naukri… |
| 14 | **Media, Entertainment & Publication** | ~44 | Zee, Sun TV, PVR INOX, Nazara, Saregama, NDTV, Jagran, DB Corp… |
| 15 | **Metals & Mining** | ~47 | Tata Steel, JSW Steel, Hindalco, Vedanta, NMDC, Hindustan Zinc, Coal India… |
| 16 | **Oil, Gas & Consumable Fuels** | ~46 | Reliance, ONGC, BPCL, IOC, GAIL, Coal India, Petronet, IGL, MGL… |
| 17 | **Real Estate** | ~46 | DLF, Godrej Properties, Oberoi, Prestige, Lodha, Brigade, Embassy REIT… |
| 18 | **Retailing** | ~45 | DMart, Trent, Titan, Nykaa, Zomato, Shoppers Stop, Jubilant, Metro Brands… |
| 19 | **Services** | ~46 | TCS, Infosys, Quess, TeamLease, CRISIL, Delhivery, BlueDart, KFINTECH… |
| 20 | **Telecommunication** | ~44 | Bharti Airtel, Indus Towers, Tata Comm, HFCL, Tejas Networks, Railtel… |
| 21 | **Textiles** | ~47 | Trident, Welspun, KPR Mill, Gokaldas, Kitex, Arvind, Page Industries… |
| 22 | **Utilities** | ~47 | NTPC, Power Grid, Tata Power, NHPC, JSW Energy, Suzlon, Waaree, PFC, IEX… |

### Sector PE Norms (avg / cheap / expensive)
| Sector | Avg PE | Cheap | Expensive |
|--------|--------|-------|-----------|
| Automobile and Auto Components | 22 | 14 | 30 |
| Capital Goods | 25 | 16 | 35 |
| Chemicals | 30 | 20 | 42 |
| Construction Materials | 25 | 15 | 38 |
| Consumer Durables | 45 | 28 | 65 |
| Consumer Services | 40 | 25 | 60 |
| Diversified | 20 | 12 | 30 |
| Fast Moving Consumer Goods | 45 | 30 | 60 |
| Fertilizers & Agrochemicals | 15 | 8 | 25 |
| Financial Services | 15 | 10 | 22 |
| Forest Materials | 12 | 7 | 20 |
| Healthcare | 30 | 22 | 42 |
| Information Technology | 28 | 20 | 38 |
| Media, Entertainment & Publication | 22 | 12 | 35 |
| Metals & Mining | 10 | 6 | 16 |
| Oil, Gas & Consumable Fuels | 12 | 8 | 18 |
| Real Estate | 25 | 15 | 40 |
| Retailing | 50 | 30 | 75 |
| Services | 28 | 18 | 40 |
| Telecommunication | 20 | 12 | 30 |
| Textiles | 18 | 10 | 28 |
| Utilities | 14 | 8 | 22 |

### Cyclical Sectors
Metals & Mining, Oil Gas & Consumable Fuels, Automobile and Auto Components, Real Estate, Construction Materials, Fertilizers & Agrochemicals.

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
- Started with 10 sectors / 100 stocks → expanded to 22 sectors / ~730 unique stocks (deduplicated from ~1,100).
- Uses official NSE sector classification (22 sectors) for comprehensive coverage.
- Goal: cover all NSE sectors with top 50 stocks each for comprehensive gem discovery.

### HTML Report
- Dark theme (GitHub-inspired), 6 tabs: Dashboard, Rankings, Top Picks, By Sector, All Stocks, Frameworks.
- Multi-column sort on Rankings tab: Click to sort, Shift+Click for secondary/tertiary sorts.
- Stock cards with all 10 dimension scores, intrinsic value comparisons, moat details, red flags.
- Sort arrows with priority badges for multi-column sorting.

---

## SIP Portfolio — Core 9 Stocks (April 2026)

Selected via 100-point quantitative screener + 10 published investment frameworks overlay.
Criteria: GEM/STRONG verdict, 7+/10 framework passes, Wide/Narrow moat, Coffee Can eligible, D/E < 0.35, no cyclicals.

| # | Ticker | Sector | Score | PE | ROCE% | D/E | CAGR% | Moat | Mgrs |
|---|--------|--------|-------|----|-------|-----|-------|------|------|
| 1 | BLS.NS | Services | 83.1 | 19.0 | 27.3 | 0.21 | 37.2 | Wide | 10/10 |
| 2 | NATCOPHARM.NS | Fertilizers & Agrochemicals | 73.8 | 12.9 | 30.0 | 0.04 | 32.3 | Wide | 10/10 |
| 3 | ZYDUSLIFE.NS | Healthcare | 72.4 | 19.2 | 21.7 | 0.13 | 15.0 | Wide | 10/10 |
| 4 | EPIGRAL.NS | Chemicals | 71.6 | 15.3 | 21.9 | 0.31 | 17.5 | Narrow | 10/10 |
| 5 | NEWGEN.NS | Information Technology | 77.0 | 22.9 | 25.2 | 0.04 | 24.1 | Wide | 9/10 |
| 6 | DODLA.NS | FMCG | 75.5 | 33.6 | 24.2 | 0.03 | 18.4 | Narrow | 9/10 |
| 7 | GULFOILLUB.NS | Oil, Gas & Consumable Fuels | 74.2 | 13.8 | 31.8 | 0.32 | 18.4 | Wide | 9/10 |
| 8 | CIGNITITEC.NS | Information Technology | 71.5 | 11.9 | 27.7 | 0.03 | 17.5 | Narrow | 9/10 |
| 9 | AGI.NS | Forest Materials | 71.3 | 11.4 | 18.5 | 0.26 | 21.4 | Wide | 9/10 |

Portfolio avg: Score 74.3, ROCE 25.4%, D/E 0.13, CAGR 22.4%, Piotroski 7.0/9, 100% Coffee Can.
See `sip_portfolio.md` for full thesis on each stock.

---

## Investment Frameworks — Published & Verifiable

10 published stock-picking frameworks cross-referenced against screener results in the Frameworks tab.
Every framework has a verifiable source (book, academic paper, or annual study). No speculative criteria.

| # | Framework | Author | Source | Key Criteria |
|---|-----------|--------|--------|--------------|
| 1 | Graham Value | Benjamin Graham | *The Intelligent Investor* (1949) | PE<15, PB<1.5, PE×PB<22.5, D/E<0.5, CR>2, MoS>0 |
| 2 | Piotroski F-Score | Joseph Piotroski | *Journal of Accounting Research* (2000) | 9 binary tests — STRONG 7-9, MODERATE 4-6 |
| 3 | Altman Z-Score | Edward Altman | *Journal of Finance* (1968) | Z formula — SAFE >2.99, GREY 1.81-2.99, DISTRESS <1.81 |
| 4 | Magic Formula | Joel Greenblatt | *The Little Book That Beats the Market* (2005) | Combined rank: Earnings Yield + ROIC |
| 5 | Coffee Can | Saurabh Mukherjea | *Coffee Can Investing* (2018) | Rev CAGR≥10%, ROCE≥15%, D/E≤1.0 |
| 6 | QGLP | Raamdeo Agrawal | Motilal Oswal Wealth Creation Study (annual) | Quality✓ Growth✓ Longevity✓ Price✓ |
| 7 | Lynch PEG | Peter Lynch | *One Up on Wall Street* (1989) | PEG<1.0 BARGAIN, <1.5 FAIR |
| 8 | Buffett Moat | Warren Buffett | Berkshire Hathaway Annual Letters | ROE≥15%, moat, owner earnings, FCF |
| 9 | Dorsey Moat | Pat Dorsey | *The Little Book That Builds Wealth* (2008) | 5 moat sources, ROIC>WACC, trend |
| 10 | DCF Intrinsic Value | Aswath Damodaran | *Investment Valuation* (Wiley) | MoS from Graham/DCF |

Stocks passing 7+/10 frameworks = highest conviction SIP candidates.

---

## Tech Stack

- **Python 3.10+** — Core language
- **yfinance** — Free market data API
- **pandas / numpy** — Data crunching
- **HTML report** — Final output with tabbed dashboard

## Output

- `report.html` — Full HTML report with dashboard, rankings, stock cards, and frameworks
- `sip_portfolio.md` — Core 9 SIP stocks with full thesis and portfolio characteristics
- Console output — Per-sector top 3 and final verdict summary

---

## Current Status (April 2026)

### Completed
- 22 NSE sectors, ~730 stocks fully configured in config.py
- 10-dimension × 10-point scoring engine with sector-aware thresholds
- Sector-aware fixes: FINANCIAL_SECTORS, HIGH_LEVERAGE_SECTORS, sector-specific D/E and PE norms
- 10 published investment frameworks replacing old speculative fund manager overlay
- 6-tab HTML report: Dashboard, Rankings, Top Picks, By Sector, All Stocks, Frameworks (combined investment frameworks + scoring reference)
- SIP portfolio: 9 core stocks selected (avg score 74.3, ROCE 25.4%, 100% Coffee Can)
- IT sector test passed (42 stocks, 1 GEM, 14 STRONG)

### Last Full Run Results (IT sector only)
- 42 stocks fetched, 6 skipped (yfinance 404)
- GEM: 1 (NEWGEN), STRONG: 14, ACCEPTABLE: 11, WATCHLIST: 4, REJECT: 12

### Pending / Future
- Full 22-sector run to regenerate report.html with new frameworks system
- SIP portfolio framework pass counts need re-validation against new 10-framework system
- TSX Canada expansion (future)
- Potential: framework-weighted consensus scoring (weight by source authority)
