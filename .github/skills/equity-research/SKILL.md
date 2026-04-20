---
name: equity-research
description: "Analyse NSE/TSX stocks using fundamental screening. Use when: analysing a stock, evaluating a company, comparing stocks, checking if a stock is a buy/hold/avoid, assessing moat or Coffee Can eligibility, computing intrinsic value, screening a sector, building a portfolio."
argument-hint: "Stock ticker or company name to analyse (e.g., ZYDUSLIFE.NS, TCS)"
---

# Equity Research Skill

## When to Use
- User asks to analyse, evaluate, or screen a stock
- User asks "Is X a good buy?", "What about Y stock?", "Compare A vs B"
- User wants moat assessment, intrinsic value, or Coffee Can eligibility
- User asks to screen a sector or find undervalued gems
- User asks for a buy/hold/avoid recommendation

## Investment Framework

### Philosophy (Non-Negotiable)
1. **Warren Buffett**: Economic moats, ROE > 15%, margin of safety, owner earnings
2. **Anand Srinivasan**: Cash flow focus, pricing power, PEG < 1, consistent compounders
3. **Coffee Can (Saurabh Mukherjea)**: Revenue CAGR ≥ 10%, ROCE ≥ 15%, D/E ≤ 1.0
4. **Piotroski**: F-Score 8–9 outperform by 7.5% annually
5. **Greenblatt**: Magic Formula (Earnings Yield + ROIC) cross-check
6. **Dorsey**: Moat trend (widening/stable/eroding) matters more than moat existence
7. **Altman**: Z-Score < 1.81 = distress, instant reject
8. **Damodaran**: Reverse DCF to check market-implied growth

### Quality Principles
- **Never recommend without numbers.** Every pick needs PE, ROCE, D/E, growth rates.
- **Conservative bias**: when in doubt, pass. A missed opportunity beats a loss.
- **Sector context**: PE 30 is expensive for banking but normal for IT.
- **Moat first, valuation second**: a cheap stock without a moat is a value trap.
- **10-year lens**: short-term price doesn't matter if the business compounds.

## Procedure

### Step 1 — Fetch Data
```python
from data_fetcher import fetch_stock_info
data = fetch_stock_info("TICKER.NS")
```

### Step 2 — Score the Stock
Apply the 10-filter, 100-point scoring engine:

```python
from analyzer import score_stock_full, coffee_can_eligible, graham_number, margin_of_safety
import pandas as pd

row = pd.Series(data)
gn = graham_number(data.get("eps"), data.get("book_value"))
mos = margin_of_safety(data.get("price"), gn)
row["graham_number"] = gn
row["margin_of_safety_pct"] = mos

# 10-dimension scoring + red flags + verdict
results = score_stock_full(row, sector="IT")
cc = coffee_can_eligible(row)
```

### Step 3 — Generate Recommendation
Structure output using all 10 filters:

#### Filter 1: Valuation (/10)
- PE ratio vs **sector norms**, PB, PEG, EV/EBITDA, P/S
- Graham Number and DCF vs current price → margin of safety %
- Reverse DCF: market-implied growth vs actual growth

#### Filter 2: Profitability (/10)
- ROE, ROCE, ROA, operating margin, net margin
- Owner Earnings yield (Buffett)

#### Filter 3: Growth Quality (/10)
- Revenue/profit CAGR, incremental ROCE (ROIIC)
- Quarterly profit direction, earnings consistency

#### Filter 4: Financial Health (/10)
- Altman Z-Score, D/E, interest coverage, current ratio

#### Filter 5: Cash Flow (/10)
- FCF positive, FCF conversion (FCF/NI), FCF yield, OCF/NI, capex intensity

#### Filter 6: Business Moat (/10)
- 7 moat types, moat trend (widening/stable/eroding)
- Rating: Wide (≥7) / Narrow (≥4) / None (<4)

#### Filter 7: Earnings Quality (/10)
- Piotroski F-Score (0–9), accrual ratio, OCF > NI

#### Filter 8: Institutional (/10)
- Holdings, analyst recommendation, target price upside

#### Filter 9: Sector & Macro (/10)
- Tailwinds, threats, diversification, cyclicality

#### Filter 10: Management (/10)
- ROCE consistency, payout, debt discipline, margin trend, dilution, FCF

#### Filter 11: Red Flags
- PE>60, D/E>2, IC<1.5, profit declining 3+ qtrs, negative FCF, net loss
- Altman Z < 1.81, Piotroski ≤ 2, Accrual > 25%

#### Coffee Can Check
- Revenue CAGR ≥ 10%? ROCE ≥ 15%? Debt ≤ 1.0?

#### Verdict
- GEM (≥75), STRONG (65–74), ACCEPTABLE (55–64), WATCHLIST (40–54), REJECT (<40)

#### Verdict Rationale
- **GEM** (≥75/100): Strong moat + reasonable valuation + growing + low debt
- **STRONG** (65–74): Quality business, buy/accumulate
- **ACCEPTABLE** (55–64): Decent business, hold
- **WATCHLIST** (40–54): Monitor for better entry
- **REJECT** (<40): Weak moat, high debt, declining margins, or red-flagged

### Step 4 — Compare to Peers
When possible, compare against sector peers from `config.py → NSE_SECTORS`.
Show relative standing on PE, ROCE, and composite score.

## Reference Files
- [config.py](../../config.py) — Filter thresholds, scoring weights, sector lists
- [analyzer.py](../../analyzer.py) — Scoring functions, moat logic, Graham Number
- [data_fetcher.py](../../data_fetcher.py) — Data retrieval helpers
- [context.md](../../context.md) — Full project goals and filter definitions

## Output Format

Always include a structured summary table:

| Metric | Value | Verdict |
|--------|-------|---------|
| PE | 19.2 | ✅ Below sector avg |
| ROCE | 20.1% | ✅ Above 15% |
| D/E | 0.05 | ✅ Nearly debt-free |
| Revenue CAGR | 12.3% | ✅ Coffee Can eligible |
| FCF | Positive | ✅ Cash generative |
| Moat | Wide (switching_cost, intangible_assets) | ✅ |
| Total Score | 56.5/80 | ACCEPTABLE |
| Graham Number | ₹527 | — |
| Margin of Safety | -78% | ❌ Overvalued vs Graham |
| Red Flags | None | ✅ Clean |

Followed by a reasoning paragraph and a clear **GEM / ACCEPTABLE / WATCHLIST / REJECT** verdict.
