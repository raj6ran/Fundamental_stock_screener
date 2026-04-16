---
description: "Compare two or more stocks side by side on fundamentals, scoring, moat, and valuation."
---

# Compare: ${input:tickers:Enter tickers comma-separated (e.g. TCS.NS, INFY.NS)}

Compare the given stocks head-to-head:

1. Fetch data for each ticker using `data_fetcher.fetch_stock_info()`
2. Score each using the analyzer pipeline
3. Build a side-by-side comparison table showing:
   - Price, PE, PB, PEG
   - ROE, ROCE, operating margin
   - Revenue CAGR, profit CAGR
   - Debt/Equity, current ratio
   - Moat rating, Coffee Can status
   - Composite score, Graham Number, margin of safety
4. Declare a winner with reasoning
5. Give BUY/HOLD/AVOID for each
