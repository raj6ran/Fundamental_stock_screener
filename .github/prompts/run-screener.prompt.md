---
description: "Run the full stock screener across one or all sectors and generate a fresh HTML report."
---

# Screen Stocks: ${input:sector:Enter sector name or 'all' for full run}

Run the stock screener pipeline:

1. If sector is "all": run `python screener.py`
   Otherwise: run `python screener.py --sector "${input:sector}"`
2. The screener automatically generates `report.html` at the end
3. Show the top picks from the run — GEM and STRONG verdicts
4. Highlight Coffee Can candidates and Wide Moat stocks
5. Open `report.html` in the browser
