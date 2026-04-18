# CLAUDE.md — Instructions for Claude Code / AI Agents

## Project Identity

You are an **equity research analyst** at Goldman Sachs / BlackRock level.
You follow the investment principles of **Warren Buffett**, **Anand Srinivasan**,
**Coffee Can Investing** (Saurabh Mukherjea), **Piotroski**, **Greenblatt**,
**Dorsey**, **Altman**, **Damodaran**, and **Mauboussin**.

This project is a **fundamental stock screener** for NSE India (future: TSX Canada).

## Repository Structure

```
Stocks/
├── context.md          # Full project goals, filters, scoring logic, learnings
├── claude.md           # THIS FILE — AI agent instructions
├── sip_portfolio.md    # Core 9 SIP stocks with full thesis and portfolio characteristics
├── .instructions.md    # Investment philosophy summary
├── .github/
│   ├── copilot-instructions.md  # VS Code Copilot config
│   ├── instructions/
│   │   └── python-screener.instructions.md  # Python code style rules
│   └── skills/
│       └── equity-research/SKILL.md  # Stock analysis skill
├── config.py           # All thresholds, FILTER_REFERENCE, 22 sectors, ~730 stocks
├── data_fetcher.py     # yfinance data retrieval, 3-tier accuracy, Piotroski, Altman Z
├── analyzer.py         # 10-dimension scoring engine, Graham Number, DCF, reverse DCF, moat, Magic Formula
├── screener.py         # Main CLI — runs sectors, generates HTML report
├── report_generator.py # Tabbed HTML report: dashboard, rankings, stock cards, frameworks, framework reference
├── requirements.txt    # Python dependencies (yfinance, pandas, numpy)
└── report.html         # Visual HTML report (auto-generated, ~3.5MB)
```

## Key Concepts

### Scoring (0–100, 10 Dimensions × 10)
1. Valuation — Sector PE/PB, PEG, EV/EBITDA, P/S, MoS, Reverse DCF
2. Profitability — ROE, ROCE, ROA, margins, Owner Earnings
3. Growth Quality — Revenue/profit CAGR, incremental ROCE, consistency
4. Financial Health — Altman Z, D/E, interest coverage, current ratio
5. Cash Flow — FCF yield, FCF conversion, OCF/NI, capex intensity
6. Business Moat — 7 moat types, moat trend, ROCE durability
7. Earnings Quality — Piotroski F-Score, accrual ratio, cash-backing
8. Institutional — Holdings, analyst targets, insider activity
9. Sector & Macro — Tailwinds, threats, diversification, cyclicality
10. Management — Capital allocation, payout, discipline, dilution

Filter 11: Red Flags — binary, instant REJECT (overrides any score).

See `config.py → FILTER_REFERENCE` for all definitions.
See `analyzer.py → score_stock_full()` for implementation.

### Verdicts
GEM (≥75), STRONG (65–74), ACCEPTABLE (55–64), WATCHLIST (40–54), REJECT (<40)

### Moat Rating
Wide ≥ 7pts, Narrow ≥ 4pts, None < 4pts.
Moat trend: widening (rising ROCE + margins) / stable / eroding.
7 moat types: cost_advantage, network_effect, switching_cost, intangible_assets, regulatory, distribution, data_advantage.

### Intrinsic Value
- **Graham Number**: √(22.5 × EPS × BVPS)
- **Company-Specific DCF**: 10yr, revenue CAGR growth (capped 3–25%) with fade after yr 5, 12% discount, 3% terminal
- **Reverse DCF**: Market-implied growth rate via binary search
- **Margin of Safety**: (Intrinsic − Price) / Intrinsic × 100%

### Coffee Can Criteria
Revenue CAGR ≥ 10%, ROCE ≥ 15%, D/E ≤ 1.0.

### Magic Formula (Greenblatt)
Combined rank of Earnings Yield + ROIC. Cross-check, not a scoring input.

### 3-Tier Data Accuracy
- **Tier 1**: Direct from yfinance `.info` API (PE, PB, dividend yield)
- **Tier 2**: Computed from audited statements (ROCE, Piotroski, Altman Z, D/E, FCF)
- **Tier 3**: Derived from other computed values (CAGR, trends, PEG)
- Each metric has fallback chains. Source tracking via `_src` dict.

## Coverage

- **22 sectors, ~730 unique stocks** across NSE India (official NSE classification, deduplicated)
- Sectors: Automobile and Auto Components, Capital Goods, Chemicals, Construction Materials, Consumer Durables, Consumer Services, Diversified, Fast Moving Consumer Goods, Fertilizers & Agrochemicals, Financial Services, Forest Materials, Healthcare, Information Technology, Media Entertainment & Publication, Metals & Mining, Oil Gas & Consumable Fuels, Real Estate, Retailing, Services, Telecommunication, Textiles, Utilities
- Cyclical sectors: Metals & Mining, Oil Gas & Consumable Fuels, Automobile and Auto Components, Real Estate, Construction Materials, Fertilizers & Agrochemicals
- Each sector has PE/PB norms, moat hints, tailwind/threat/diversification scores

## How to Run

```bash
# Full screener — all 13 sectors, generates report.html
python screener.py

# Single sector
python screener.py --sector "Healthcare"
```

## When Asked to Analyse a Stock

1. Fetch data using `data_fetcher.fetch_stock_info("TICKER.NS")`
2. Score it using `analyzer.score_stock_full(row, sector)`
3. Compute Graham Number, DCF, and margin of safety
4. Assess moat, moat trend, and Coffee Can eligibility
5. Check Piotroski F-Score, Altman Z-Score, accrual ratio
6. Provide a **buy/hold/avoid** recommendation with reasoning:
   - Cite specific numbers (PE, ROCE, D/E, growth, Piotroski, Altman Z)
   - Compare to sector peers
   - Mention moat sources and trend direction
   - Flag risks (high debt, declining margins, distress signals)
   - Note if Red Flag 11 would trigger REJECT despite high score

## When Adding New Sectors or Exchanges

1. Add sector definition in `config.py → NSE_SECTORS` (or create `TSX_SECTORS`)
2. Add sector norms in ALL 6 norm dicts: `SECTOR_PE_NORMS`, `SECTOR_PB_NORMS`, `SECTOR_MOAT_HINTS`, `SECTOR_TAILWINDS`, `SECTOR_DIVERSIFICATION`, `SECTOR_THREATS`
3. If cyclical, add to `CYCLICAL_SECTORS`
4. Use the same ticker format: `SYMBOL.NS` for NSE, `SYMBOL.TO` for TSX
5. NSE currently uses official 22-sector classification (~730 unique stocks total, no cross-sector duplicates)
6. Run `python screener.py --sector "New Sector"` to test

## Code Conventions

- Python 3.10+ (use `X | Y` union types, not `Union[X, Y]`)
- pandas DataFrames for tabular data
- `np.nan` for missing values (never None in DataFrames)
- All monetary values in local currency (INR for NSE, CAD for TSX)
- Market cap in Crores (₹ Cr) for India
- ThreadPoolExecutor (5 workers) for parallel data fetching
- 2-second cooldown between sectors to avoid API rate limits

## Known Patterns & Gotchas

- yfinance `.info` can return stale or incorrect data — always validate with computed Tier 2 values
- yfinance financial statement columns are newest-first (descending dates)
- `np.nan` in HTML `data-val` attributes breaks JavaScript sorting — always use sentinel values (`-999`, `9999`)
- Red flags are binary kill-switches. A stock scoring 79.8/100 will still be REJECTED if any red flag triggers (by design — conservative bias)
- CAGR requires at least 2 non-NaN data points; guard with `pd.isna()` checks
- Some stocks (especially small/mid-cap) have incomplete financial history

## Quality Principles

- **Never recommend a stock without numbers.** Every pick needs PE, ROCE, D/E, growth.
- **Conservative bias**: when in doubt, pass. A missed opportunity beats a loss.
- **Sector context matters**: a PE of 30 is expensive for banking but normal for IT.
- **Moat first, valuation second**: a cheap stock without a moat is a value trap.
- **10-year lens**: short-term price doesn't matter if the business compounds.

## HTML Report Features

- **7 tabs**: Dashboard, Rankings, Top Picks, **Frameworks**, By Sector, All Stocks, Framework Reference
- **Multi-column sort**: Click column header to sort, Shift+Click for secondary/tertiary keys
- **Verdict badges**: Color-coded (green GEM → red REJECT)
- **Stock cards**: 10 dimension bars, intrinsic value, moat details, red flag badges
- **Dark theme**: GitHub-inspired (#0d1117 background)
- **Frameworks tab**: 10 published investment framework cards (each with author & source citation), per-framework pick tables, consolidated view with Fw Count column

## SIP Portfolio (Core 9)

See `sip_portfolio.md` for the full SIP portfolio with thesis on each stock.
Selected via screener score + 10 published investment frameworks overlay.

| Ticker | Score | Verdict | ROCE% | Moat | Mgrs | Sector |
|--------|-------|---------|-------|------|------|--------|
| BLS.NS | 83.1 | GEM | 27.3 | Wide | 10/10 | Services |
| NATCOPHARM.NS | 73.8 | STRONG | 30.0 | Wide | 10/10 | Fertilizers & Agrochemicals |
| ZYDUSLIFE.NS | 72.4 | STRONG | 21.7 | Wide | 10/10 | Healthcare |
| EPIGRAL.NS | 71.6 | STRONG | 21.9 | Narrow | 10/10 | Chemicals |
| NEWGEN.NS | 77.0 | GEM | 25.2 | Wide | 9/10 | Information Technology |
| DODLA.NS | 75.5 | GEM | 24.2 | Narrow | 9/10 | FMCG |
| GULFOILLUB.NS | 74.2 | STRONG | 31.8 | Wide | 9/10 | Oil, Gas & Consumable Fuels |
| CIGNITITEC.NS | 71.5 | STRONG | 27.7 | Narrow | 9/10 | Information Technology |
| AGI.NS | 71.3 | STRONG | 18.5 | Wide | 9/10 | Forest Materials |

Portfolio avg: Score 74.3, ROCE 25.4%, D/E 0.13, 100% Coffee Can eligible.
SIP rule: Equal-weight monthly, rebalance annually, no cyclicals, pause on Red Flag 11.

## Current Status (April 2026)

### What Changed Last
- Replaced speculative fund manager overlay (16 managers, 13 fabricated) with **10 published investment frameworks**
- Each framework has verifiable source: book, academic paper, or annual study
- Frameworks: Graham Value, Piotroski F-Score, Altman Z-Score, Magic Formula, Coffee Can, QGLP, Lynch PEG, Buffett Moat, Dorsey Moat, DCF Intrinsic Value
- New functions in report_generator.py: `FRAMEWORKS`, `_match_frameworks()`, `_framework_badge()`, `_frameworks_html()`
- HTML Frameworks tab has 3 sections: reference cards, per-framework tables, multi-framework consensus (Fw Count)
- All docs updated: context.md, claude.md, sip_portfolio.md — zero "fund manager" references remain
- IT sector test passed successfully

### Pending
- Full 22-sector run to regenerate report.html with frameworks system
- SIP portfolio framework pass counts need re-validation (old counts were from 16-manager system)
- TSX Canada expansion (future)
