---
description: "Analyse a stock and give a BUY/HOLD/AVOID recommendation with full reasoning."
---

# Analyse Stock: ${input:ticker:Enter ticker (e.g. ZYDUSLIFE.NS)}

Run the equity research pipeline on the given stock:

1. Fetch fundamentals using `data_fetcher.fetch_stock_info("${input:ticker}")`
2. Score it with `analyzer.score_stock_full()` (10-filter, 100-point system)
3. Compute Graham Number and DCF intrinsic value with margin of safety
4. Assess moat (Wide/Narrow/None), moat trend, and Coffee Can eligibility
5. Check Piotroski F-Score, Altman Z-Score, and accrual ratio
6. Compare against sector peers in `config.py → NSE_SECTORS`

Produce a structured output:
- Metrics table: PE, ROCE, D/E, revenue CAGR, margins, Piotroski, Altman Z, Graham Number, MoS, moat, score/100
- Reasoning paragraph explaining the investment thesis
- Key risks
- Clear **BUY / HOLD / AVOID** verdict
