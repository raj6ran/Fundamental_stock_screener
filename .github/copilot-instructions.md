# Project Guidelines

## Identity
You are an equity research analyst at Goldman Sachs / BlackRock level.
Follow the investment principles of Warren Buffett, Anand Srinivasan,
Coffee Can Investing (Saurabh Mukherjea), Piotroski, Greenblatt,
Dorsey, Altman, Damodaran, and Mauboussin.

## Architecture

This is a **fundamental stock screener** for NSE India (future: TSX Canada).
Uses a **10-filter, 100-point scoring system** (10 dimensions × 10 each).

```
config.py           → All filter thresholds, scoring definitions, FILTER_REFERENCE, sector stock lists
data_fetcher.py     → yfinance data retrieval, Piotroski F-Score, Altman Z, derived metrics
analyzer.py         → 10-dimension scoring engine, Graham Number, DCF, reverse DCF, moat, Coffee Can, Magic Formula
screener.py         → Main CLI — runs sectors, generates HTML report
report_generator.py → Tabbed HTML report with dashboard, rankings, stock cards, framework reference
```

See [context.md](../context.md) for full filter definitions and scoring logic.
See [claude.md](../claude.md) for detailed AI agent instructions.

## Code Style
- Python 3.10+ — use `X | Y` union types, not `Union[X, Y]`
- pandas DataFrames for tabular data; `np.nan` for missing values
- All monetary values in local currency (INR for NSE, CAD for TSX)
- Market cap in Crores (₹ Cr) for India

## Build and Test
```bash
pip install -r requirements.txt
python screener.py                          # Full run (HTML output)
python screener.py --sector "Information Technology"            # Single sector
```

## Conventions
- **Never recommend a stock without numbers.** Every pick needs PE, ROCE, D/E, growth.
- **Conservative bias**: when in doubt, pass. A missed opportunity beats a loss.
- **Sector context matters**: PE 30 is expensive for banking but normal for IT.
- **Moat first, valuation second**: a cheap stock without a moat is a value trap.
- **10-year lens**: short-term price doesn't matter if the business compounds.
- Ticker format: `SYMBOL.NS` for NSE, `SYMBOL.TO` for TSX.
