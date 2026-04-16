"""
Data Fetcher — 10-Filter, 100-Point System
===========================================
Retrieves fundamentals from yfinance for NSE/TSX stocks.
Computes derived metrics: Piotroski F-Score, Altman Z-Score,
accrual ratio, incremental ROCE, owner earnings, FCF conversion.

Supports parallel fetching via ThreadPoolExecutor for speed.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import yfinance as yf
import pandas as pd
import numpy as np

_print_lock = threading.Lock()


def fetch_stock_info(ticker: str, retries: int = 2) -> dict | None:
    """Fetch fundamental data for a single ticker. Returns flat dict or None."""
    for attempt in range(retries + 1):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info or info.get("regularMarketPrice") is None:
                return None

            financials = stock.financials
            balance = stock.balance_sheet
            cashflow = stock.cashflow
            quarterly_fin = stock.quarterly_financials

            return _extract_fundamentals(
                ticker, info, financials, balance, cashflow, quarterly_fin,
            )
        except Exception:
            if attempt < retries:
                time.sleep(1)
            continue
    return None


def _fetch_one(ticker: str, sector_name: str) -> tuple[str, dict | None]:
    """Fetch a single ticker and tag with sector. Thread-safe."""
    data = fetch_stock_info(ticker)
    if data:
        data["sector"] = sector_name
    return ticker, data


def fetch_sector_data(
    sector_name: str,
    tickers: list[str],
    max_workers: int = 5,
) -> pd.DataFrame:
    """Fetch data for all tickers in a sector using parallel threads."""
    rows: list[dict] = []
    ok = 0
    skip = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_fetch_one, t, sector_name): t
            for t in tickers
        }
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                _, data = future.result()
                with _print_lock:
                    if data:
                        rows.append(data)
                        ok += 1
                        print(f"  {ticker:>20s} ... OK  ({ok + skip}/{len(tickers)})")
                    else:
                        skip += 1
                        print(f"  {ticker:>20s} ... SKIP ({ok + skip}/{len(tickers)})")
            except Exception:
                skip += 1
                with _print_lock:
                    print(f"  {ticker:>20s} ... ERROR ({ok + skip}/{len(tickers)})")

    print(f"    => {ok} fetched, {skip} skipped")
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────

def _safe(info: dict, key: str, default=np.nan):
    val = info.get(key)
    return default if val is None else val


def _cagr(series: pd.Series) -> float:
    series = series.dropna()
    if len(series) < 2:
        return np.nan
    newest, oldest = series.iloc[0], series.iloc[-1]
    n = len(series) - 1
    if oldest <= 0 or newest <= 0:
        return np.nan
    return ((newest / oldest) ** (1 / n) - 1) * 100


def _yoy_growth(series: pd.Series) -> float:
    series = series.dropna()
    if len(series) < 2:
        return np.nan
    cur, prev = series.iloc[0], series.iloc[1]
    if prev == 0:
        return np.nan
    return ((cur - prev) / abs(prev)) * 100


def _safe_divide(a, b):
    if b is None or b == 0 or pd.isna(b) or pd.isna(a):
        return np.nan
    return a / b


def _row(df: pd.DataFrame | None, label: str) -> pd.Series | None:
    if df is None or df.empty:
        return None
    for idx in df.index:
        if label.lower() in str(idx).lower():
            return df.loc[idx]
    return None


def _latest(series: pd.Series | None) -> float:
    if series is None:
        return np.nan
    vals = series.dropna()
    return vals.iloc[0] if len(vals) > 0 else np.nan


def _prev(series: pd.Series | None, offset: int = 1) -> float:
    if series is None:
        return np.nan
    vals = series.dropna()
    return vals.iloc[offset] if len(vals) > offset else np.nan


def _quarterly_profit_trend(quarterly_fin: pd.DataFrame | None) -> tuple[int, str]:
    ni = _row(quarterly_fin, "Net Income")
    if ni is None:
        return 0, "unknown"
    vals = ni.dropna()
    if len(vals) < 2:
        return 0, "unknown"

    declining = 0
    for i in range(len(vals) - 1):
        if vals.iloc[i] < vals.iloc[i + 1]:
            declining += 1
        else:
            break

    if declining >= 3:
        direction = "declining"
    elif declining == 0:
        direction = "improving"
    else:
        direction = "mixed"
    return declining, direction


# ──────────────────────────────────────────────────────
# Piotroski F-Score (9 binary signals)
# ──────────────────────────────────────────────────────

def _compute_piotroski(
    net_income_cur: float, net_income_prev: float,
    ocf_cur: float, total_assets_cur: float, total_assets_prev: float,
    long_term_debt_cur: float, long_term_debt_prev: float,
    current_ratio_cur: float, current_ratio_prev: float,
    shares_cur: float, shares_prev: float,
    gross_margin_cur: float, gross_margin_prev: float,
    revenue_cur: float, revenue_prev: float,
) -> int:
    """Compute Piotroski F-Score (0-9)."""
    score = 0

    # ── Profitability signals (4 points) ──
    # 1. Positive net income
    if not pd.isna(net_income_cur) and net_income_cur > 0:
        score += 1
    # 2. Positive OCF
    if not pd.isna(ocf_cur) and ocf_cur > 0:
        score += 1
    # 3. Rising ROA (NI/TA)
    roa_cur = _safe_divide(net_income_cur, total_assets_cur)
    roa_prev = _safe_divide(net_income_prev, total_assets_prev)
    if not pd.isna(roa_cur) and not pd.isna(roa_prev) and roa_cur > roa_prev:
        score += 1
    # 4. OCF > Net Income (quality of earnings)
    if not pd.isna(ocf_cur) and not pd.isna(net_income_cur) and ocf_cur > net_income_cur:
        score += 1

    # ── Leverage signals (3 points) ──
    # 5. Declining long-term debt
    if not pd.isna(long_term_debt_cur) and not pd.isna(long_term_debt_prev):
        if long_term_debt_cur <= long_term_debt_prev:
            score += 1
    elif pd.isna(long_term_debt_cur):
        score += 1  # no debt = pass
    # 6. Improving current ratio
    if not pd.isna(current_ratio_cur) and not pd.isna(current_ratio_prev):
        if current_ratio_cur >= current_ratio_prev:
            score += 1
    # 7. No share dilution
    if not pd.isna(shares_cur) and not pd.isna(shares_prev):
        if shares_cur <= shares_prev:
            score += 1

    # ── Operating efficiency signals (2 points) ──
    # 8. Rising gross margin
    if not pd.isna(gross_margin_cur) and not pd.isna(gross_margin_prev):
        if gross_margin_cur >= gross_margin_prev:
            score += 1
    # 9. Rising asset turnover (Revenue / Total Assets)
    at_cur = _safe_divide(revenue_cur, total_assets_cur)
    at_prev = _safe_divide(revenue_prev, total_assets_prev)
    if not pd.isna(at_cur) and not pd.isna(at_prev) and at_cur > at_prev:
        score += 1

    return score


# ──────────────────────────────────────────────────────
# Altman Z-Score
# ──────────────────────────────────────────────────────

def _compute_altman_z(
    working_capital: float, retained_earnings: float,
    ebit: float, market_cap: float, total_liabilities: float,
    revenue: float, total_assets: float,
) -> float:
    """Altman Z-Score = 1.2*WC/TA + 1.4*RE/TA + 3.3*EBIT/TA + 0.6*MCap/TL + Rev/TA"""
    if pd.isna(total_assets) or total_assets <= 0:
        return np.nan

    x1 = _safe_divide(working_capital, total_assets) or 0
    x2 = _safe_divide(retained_earnings, total_assets) or 0
    x3 = _safe_divide(ebit, total_assets) or 0
    x4 = _safe_divide(market_cap, total_liabilities) if not pd.isna(total_liabilities) and total_liabilities > 0 else 0
    x5 = _safe_divide(revenue, total_assets) or 0

    z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + x5
    return round(z, 2)


# ──────────────────────────────────────────────────────
# Main extractor
# ──────────────────────────────────────────────────────

def _extract_fundamentals(ticker, info, financials, balance, cashflow, quarterly_fin) -> dict:
    """Build flat dict of all metrics for the 10-filter scoring engine."""

    # ── Revenue & profit series ──
    revenue = _row(financials, "Total Revenue")
    net_income = _row(financials, "Net Income")
    ebit = _row(financials, "EBIT")
    gross_profit = _row(financials, "Gross Profit")
    operating_income = _row(financials, "Operating Income")
    depreciation = _row(cashflow, "Depreciation")
    capex = _row(cashflow, "Capital Expenditure")

    total_debt = _row(balance, "Total Debt")
    long_term_debt = _row(balance, "Long Term Debt")
    total_equity = _row(balance, "Stockholders Equity")
    total_assets = _row(balance, "Total Assets")
    current_assets = _row(balance, "Current Assets")
    current_liabilities = _row(balance, "Current Liabilities")
    retained_earnings = _row(balance, "Retained Earnings")

    interest_expense = _row(financials, "Interest Expense")

    ocf_series = _row(cashflow, "Operating Cash Flow")
    if ocf_series is None:
        ocf_series = _row(cashflow, "Total Cash From Operating Activities")

    # ══════════════════════════════════════════════════
    # Data Accuracy Hierarchy
    # Tier 1: Direct from yfinance info (API-reported)
    # Tier 2: Computed from audited financial statements
    # Tier 3: Derived from other computed values
    # ══════════════════════════════════════════════════
    _src = {}  # tracks data source tier per field

    # ── Derived scalars ──
    mcap_raw = _safe(info, "marketCap", 0)
    mcap_cr = mcap_raw / 1e7 if mcap_raw else np.nan
    latest_ni = _latest(net_income)
    latest_rev = _latest(revenue)
    latest_capex = _latest(capex)
    latest_dep = _latest(depreciation)
    price = _safe(info, "regularMarketPrice")
    shares = _safe(info, "sharesOutstanding", np.nan)

    # Capital Employed
    ce_series = None
    if total_assets is not None and current_liabilities is not None:
        ce_series = total_assets - current_liabilities

    # ROCE (always Tier 2 — computed from statements)
    roce = np.nan
    latest_ebit = _latest(ebit)
    latest_ce = _latest(ce_series)
    if not pd.isna(latest_ebit) and not pd.isna(latest_ce) and latest_ce != 0:
        roce = (latest_ebit / latest_ce) * 100

    # Previous year ROCE (for incremental ROCE & moat trend)
    prev_ebit = _prev(ebit)
    prev_ce = _prev(ce_series)
    roce_prev = np.nan
    if not pd.isna(prev_ebit) and not pd.isna(prev_ce) and prev_ce != 0:
        roce_prev = (prev_ebit / prev_ce) * 100

    # D/E
    de = _safe_divide(_latest(total_debt), _latest(total_equity))

    # Current Ratio
    cr_cur = _safe_divide(_latest(current_assets), _latest(current_liabilities))
    cr_prev = _safe_divide(_prev(current_assets), _prev(current_liabilities))

    # Interest Coverage
    ic = np.nan
    ie_val = _latest(interest_expense)
    if not pd.isna(latest_ebit) and not pd.isna(ie_val) and ie_val != 0:
        ic = abs(latest_ebit / ie_val)

    # ── EPS — Tier 1 → Tier 2 ──
    eps = _safe(info, "trailingEps")
    _src["eps"] = "api"
    if pd.isna(eps) and not pd.isna(latest_ni) and not pd.isna(shares) and shares > 0:
        eps = latest_ni / shares
        _src["eps"] = "computed"

    # ── Book Value Per Share — Tier 1 → Tier 2 ──
    book_value_per_share = _safe(info, "bookValue")
    _src["bvps"] = "api"
    if pd.isna(book_value_per_share):
        eq = _latest(total_equity)
        if not pd.isna(eq) and not pd.isna(shares) and shares > 0:
            book_value_per_share = eq / shares
            _src["bvps"] = "computed"

    # ── PE — Tier 1 (api) → Tier 2 (price/EPS) ──
    pe = _safe(info, "trailingPE")
    _src["pe"] = "api"
    if pd.isna(pe) and not pd.isna(price) and not pd.isna(eps) and eps > 0:
        pe = price / eps
        _src["pe"] = "computed"

    # ── Forward PE — Tier 1 only ──
    forward_pe = _safe(info, "forwardPE")

    # ── PB — Tier 1 → Tier 2 (price/BVPS) ──
    pb = _safe(info, "priceToBook")
    _src["pb"] = "api"
    if pd.isna(pb) and not pd.isna(price) and not pd.isna(book_value_per_share) and book_value_per_share > 0:
        pb = price / book_value_per_share
        _src["pb"] = "computed"

    # ── PEG — Tier 1 → Tier 3 (PE / profit CAGR) ──
    peg = _safe(info, "pegRatio")
    _src["peg"] = "api"
    profit_cagr_val = (
        _cagr(net_income.iloc[:4]) if net_income is not None and len(net_income.dropna()) >= 4
        else (_cagr(net_income) if net_income is not None and len(net_income.dropna()) >= 2 else np.nan)
    )
    if pd.isna(peg) and not pd.isna(pe) and not pd.isna(profit_cagr_val) and profit_cagr_val > 0:
        peg = pe / profit_cagr_val
        _src["peg"] = "derived"

    # ── ROE — Tier 1 → Tier 2 (NI / Equity) ──
    roe_raw = _safe(info, "returnOnEquity", np.nan)
    _src["roe"] = "api"
    if not pd.isna(roe_raw) and roe_raw:
        roe_pct = roe_raw * 100
    else:
        eq = _latest(total_equity)
        roe_pct = np.nan
        if not pd.isna(latest_ni) and not pd.isna(eq) and eq > 0:
            roe_pct = (latest_ni / eq) * 100
            _src["roe"] = "computed"

    # ── ROA — Tier 1 → Tier 2 (NI / Total Assets) ──
    roa = _safe(info, "returnOnAssets", np.nan)
    _src["roa"] = "api"
    if not pd.isna(roa):
        roa_pct = roa * 100
    else:
        ta = _latest(total_assets)
        roa_pct = np.nan
        if not pd.isna(latest_ni) and not pd.isna(ta) and ta > 0:
            roa_pct = (latest_ni / ta) * 100
            _src["roa"] = "computed"

    # ── Operating Margin — Tier 1 → Tier 2 (OI / Revenue) ──
    op_margin = _safe(info, "operatingMargins", np.nan)
    _src["op_margin"] = "api"
    if not pd.isna(op_margin):
        op_margin *= 100
    else:
        oi = _latest(operating_income)
        if not pd.isna(oi) and not pd.isna(latest_rev) and latest_rev > 0:
            op_margin = (oi / latest_rev) * 100
            _src["op_margin"] = "computed"

    # ── Net Margin — Tier 1 → Tier 2 (NI / Revenue) ──
    net_margin = _safe(info, "profitMargins", np.nan)
    _src["net_margin"] = "api"
    if not pd.isna(net_margin):
        net_margin *= 100
    else:
        if not pd.isna(latest_ni) and not pd.isna(latest_rev) and latest_rev > 0:
            net_margin = (latest_ni / latest_rev) * 100
            _src["net_margin"] = "computed"

    # ── P/S — Tier 1 → Tier 2 (MCap / Revenue) ──
    ps_ratio = _safe(info, "priceToSalesTrailing12Months", np.nan)
    _src["ps"] = "api"
    if pd.isna(ps_ratio) and mcap_raw and not pd.isna(latest_rev) and latest_rev > 0:
        ps_ratio = mcap_raw / latest_rev
        _src["ps"] = "computed"

    # ── Cash flow metrics — Tier 1 → Tier 2 ──
    # OCF: Tier 1 (info) → Tier 2 (cashflow statement)
    ocf_raw = _safe(info, "operatingCashflow", np.nan)
    _src["ocf"] = "api"
    if pd.isna(ocf_raw) and ocf_series is not None:
        ocf_raw = _latest(ocf_series)
        if not pd.isna(ocf_raw):
            _src["ocf"] = "computed"

    # FCF: Tier 1 (info) → Tier 2 (OCF - CapEx)
    fcf_raw = _safe(info, "freeCashflow", np.nan)
    _src["fcf"] = "api"
    if pd.isna(fcf_raw) and not pd.isna(ocf_raw) and not pd.isna(latest_capex):
        fcf_raw = ocf_raw - abs(latest_capex)
        _src["fcf"] = "computed"

    fcf_yield = _safe_divide(fcf_raw, mcap_raw) * 100 if not pd.isna(fcf_raw) and mcap_raw else np.nan

    # FCF Conversion = FCF / Net Income
    fcf_conversion = _safe_divide(fcf_raw, latest_ni) if not pd.isna(fcf_raw) else np.nan

    # OCF / Net Income
    ocf_ni_ratio = _safe_divide(ocf_raw, latest_ni) if not pd.isna(ocf_raw) else np.nan

    # CapEx intensity
    capex_intensity = np.nan
    if not pd.isna(latest_capex) and not pd.isna(latest_rev) and latest_rev > 0:
        capex_intensity = abs(latest_capex) / latest_rev

    # ── Owner Earnings (Buffett) ──
    # Owner Earnings = Net Income + D&A - Maintenance CapEx
    # Approximate maintenance capex as 70% of total capex
    owner_earnings = np.nan
    if not pd.isna(latest_ni) and not pd.isna(latest_dep):
        maint_capex = abs(latest_capex) * 0.7 if not pd.isna(latest_capex) else 0
        owner_earnings = latest_ni + abs(latest_dep) - maint_capex

    owner_earnings_yield = np.nan
    if not pd.isna(owner_earnings) and mcap_raw and mcap_raw > 0:
        owner_earnings_yield = (owner_earnings / mcap_raw) * 100

    # ── Holdings ──
    inst_hold = _safe(info, "heldPercentInstitutions", np.nan)
    inst_hold_pct = inst_hold * 100 if not pd.isna(inst_hold) else np.nan
    insider_hold = _safe(info, "heldPercentInsiders", np.nan)
    insider_hold_pct = insider_hold * 100 if not pd.isna(insider_hold) else np.nan

    # ── Governance proxies ──
    payout_ratio = _safe(info, "payoutRatio", np.nan)
    _src["payout"] = "api"
    if pd.isna(payout_ratio):
        # Tier 2: dividends / net income from statements
        div_paid = _latest(_row(cashflow, "Dividends Paid"))
        if not pd.isna(div_paid) and not pd.isna(latest_ni) and latest_ni > 0:
            payout_ratio = abs(div_paid) / latest_ni
            _src["payout"] = "computed"
    payout_pct = payout_ratio * 100 if not pd.isna(payout_ratio) else np.nan
    analyst_target = _safe(info, "targetMeanPrice", np.nan)
    analyst_rec = _safe(info, "recommendationKey", "none")

    # ── Quarterly trend ──
    declining_q, q_direction = _quarterly_profit_trend(quarterly_fin)

    # ── Margin trend ──
    margin_trend = "stable"
    if operating_income is not None and revenue is not None:
        oi_vals = operating_income.dropna()
        rev_vals = revenue.dropna()
        if len(oi_vals) >= 2 and len(rev_vals) >= 2:
            cur_m = _safe_divide(oi_vals.iloc[0], rev_vals.iloc[0])
            prev_m = _safe_divide(oi_vals.iloc[1], rev_vals.iloc[1])
            if not pd.isna(cur_m) and not pd.isna(prev_m):
                diff = cur_m - prev_m
                if diff > 0.01:
                    margin_trend = "expanding"
                elif diff < -0.01:
                    margin_trend = "contracting"

    # ── Gross margin trend (for Piotroski) ──
    gm_cur = _safe_divide(_latest(gross_profit), _latest(revenue)) if gross_profit is not None else np.nan
    gm_prev = _safe_divide(_prev(gross_profit), _prev(revenue)) if gross_profit is not None else np.nan

    # ── Piotroski F-Score ──
    piotroski = _compute_piotroski(
        net_income_cur=_latest(net_income),
        net_income_prev=_prev(net_income),
        ocf_cur=ocf_raw if not pd.isna(ocf_raw) else _latest(ocf_series),
        total_assets_cur=_latest(total_assets),
        total_assets_prev=_prev(total_assets),
        long_term_debt_cur=_latest(long_term_debt) if long_term_debt is not None else _latest(total_debt),
        long_term_debt_prev=_prev(long_term_debt) if long_term_debt is not None else _prev(total_debt),
        current_ratio_cur=cr_cur if not pd.isna(cr_cur) else np.nan,
        current_ratio_prev=cr_prev if not pd.isna(cr_prev) else np.nan,
        shares_cur=shares,
        shares_prev=shares,  # yfinance doesn't give prior year shares easily
        gross_margin_cur=gm_cur if not pd.isna(gm_cur) else np.nan,
        gross_margin_prev=gm_prev if not pd.isna(gm_prev) else np.nan,
        revenue_cur=_latest(revenue),
        revenue_prev=_prev(revenue),
    )

    # ── Altman Z-Score ──
    wc = np.nan
    if not pd.isna(_latest(current_assets)) and not pd.isna(_latest(current_liabilities)):
        wc = _latest(current_assets) - _latest(current_liabilities)

    total_liabilities = np.nan
    tl_row = _row(balance, "Total Liabilities")
    if tl_row is not None:
        total_liabilities = _latest(tl_row)
    elif not pd.isna(_latest(total_assets)) and not pd.isna(_latest(total_equity)):
        total_liabilities = _latest(total_assets) - _latest(total_equity)

    altman_z = _compute_altman_z(
        working_capital=wc,
        retained_earnings=_latest(retained_earnings),
        ebit=latest_ebit,
        market_cap=mcap_raw,
        total_liabilities=total_liabilities,
        revenue=_latest(revenue),
        total_assets=_latest(total_assets),
    )

    # ── Accrual Ratio = (Net Income - OCF) / Total Assets ──
    accrual_ratio = np.nan
    ocf_val = ocf_raw if not pd.isna(ocf_raw) else _latest(ocf_series)
    ta_val = _latest(total_assets)
    if not pd.isna(latest_ni) and not pd.isna(ocf_val) and not pd.isna(ta_val) and ta_val > 0:
        accrual_ratio = (latest_ni - ocf_val) / ta_val

    # ── Incremental ROCE (ROIIC proxy) ──
    incremental_roce = np.nan
    if not pd.isna(latest_ebit) and not pd.isna(prev_ebit) and not pd.isna(latest_ce) and not pd.isna(prev_ce):
        delta_nopat = latest_ebit - prev_ebit  # EBIT as NOPAT proxy
        delta_ce = latest_ce - prev_ce
        if delta_ce > 0:
            incremental_roce = (delta_nopat / delta_ce) * 100

    # ── Moat trend (ROCE direction) ──
    moat_trend = "stable"
    if not pd.isna(roce) and not pd.isna(roce_prev):
        if roce > roce_prev + 1:
            moat_trend = "widening"
        elif roce < roce_prev - 1:
            moat_trend = "eroding"

    # ── Shares trend (dilution check) ──
    # yfinance doesn't easily provide prior-year shares, use a proxy
    shares_diluted = False  # default

    return {
        "ticker": ticker,
        "name": _safe(info, "shortName", ticker),
        "price": _safe(info, "regularMarketPrice"),
        "market_cap_cr": round(mcap_cr, 1) if not pd.isna(mcap_cr) else np.nan,

        # ── Valuation ──
        "pe": round(pe, 2) if not pd.isna(pe) else np.nan,
        "forward_pe": forward_pe,
        "pb": round(pb, 2) if not pd.isna(pb) else np.nan,
        "peg": round(peg, 2) if not pd.isna(peg) else np.nan,
        "ev_ebitda": _safe(info, "enterpriseToEbitda"),
        "ps_ratio": round(ps_ratio, 2) if not pd.isna(ps_ratio) else np.nan,
        "dividend_yield": (_safe(info, "dividendYield", 0) or 0) * 100,

        # ── Profitability ──
        "roe_pct": round(roe_pct, 2) if not pd.isna(roe_pct) else np.nan,
        "roce_pct": round(roce, 2) if not pd.isna(roce) else np.nan,
        "roce_prev_pct": round(roce_prev, 2) if not pd.isna(roce_prev) else np.nan,
        "roa_pct": round(roa_pct, 2) if not pd.isna(roa_pct) else np.nan,
        "operating_margin_pct": round(op_margin, 2) if not pd.isna(op_margin) else np.nan,
        "net_margin_pct": round(net_margin, 2) if not pd.isna(net_margin) else np.nan,
        "owner_earnings": owner_earnings,
        "owner_earnings_yield_pct": round(owner_earnings_yield, 2) if not pd.isna(owner_earnings_yield) else np.nan,

        # ── Growth ──
        "revenue_cagr_3y": round(_cagr(revenue.iloc[:4]), 2) if revenue is not None and len(revenue.dropna()) >= 4 else
                           (round(_cagr(revenue), 2) if revenue is not None and len(revenue.dropna()) >= 2 else np.nan),
        "profit_cagr_3y": round(_cagr(net_income.iloc[:4]), 2) if net_income is not None and len(net_income.dropna()) >= 4 else
                          (round(_cagr(net_income), 2) if net_income is not None and len(net_income.dropna()) >= 2 else np.nan),
        "eps": eps,
        "eps_growth_yoy": round(_yoy_growth(net_income), 2) if net_income is not None else np.nan,
        "revenue_yoy": round(_yoy_growth(revenue), 2) if revenue is not None else np.nan,
        "incremental_roce": round(incremental_roce, 2) if not pd.isna(incremental_roce) else np.nan,

        # ── Financial Health ──
        "debt_to_equity": round(de, 2) if not pd.isna(de) else np.nan,
        "current_ratio": round(cr_cur, 2) if not pd.isna(cr_cur) else np.nan,
        "interest_coverage": round(ic, 2) if not pd.isna(ic) else np.nan,
        "altman_z": altman_z,

        # ── Cash Flow ──
        "free_cash_flow": fcf_raw,
        "operating_cash_flow": ocf_raw,
        "fcf_yield_pct": round(fcf_yield, 2) if not pd.isna(fcf_yield) else np.nan,
        "fcf_conversion": round(fcf_conversion, 2) if not pd.isna(fcf_conversion) else np.nan,
        "ocf_ni_ratio": round(ocf_ni_ratio, 2) if not pd.isna(ocf_ni_ratio) else np.nan,
        "capex_intensity": round(capex_intensity, 4) if not pd.isna(capex_intensity) else np.nan,

        # ── Earnings Quality ──
        "piotroski_score": piotroski,
        "accrual_ratio": round(accrual_ratio, 4) if not pd.isna(accrual_ratio) else np.nan,

        # ── Institutional / Ownership ──
        "institutional_holding_pct": round(inst_hold_pct, 2) if not pd.isna(inst_hold_pct) else np.nan,
        "insider_holding_pct": round(insider_hold_pct, 2) if not pd.isna(insider_hold_pct) else np.nan,

        # ── Management / Governance ──
        "payout_ratio_pct": round(payout_pct, 2) if not pd.isna(payout_pct) else np.nan,
        "analyst_target_price": analyst_target,
        "analyst_recommendation": analyst_rec,
        "shares_outstanding": shares,
        "shares_diluted": shares_diluted,

        # ── Trends ──
        "profit_declining_quarters": declining_q,
        "quarterly_profit_direction": q_direction,
        "margin_trend": margin_trend,
        "moat_trend": moat_trend,

        # ── Quality ──
        "book_value": book_value_per_share,
        "net_income_latest": latest_ni,

        # ── Data source tiers (for transparency) ──
        "data_sources": _src,
    }
