"""
Scoring & Analysis Engine — 10-Filter, 100-Point System
========================================================
Ten scored dimensions (0-10 each, 100 max) plus Red-Flag instant rejection.
Implements: Piotroski F-Score, Altman Z-Score, Accrual Ratio,
Incremental ROCE, Owner Earnings, Reverse DCF, Moat Trend,
FCF Conversion, and Magic Formula cross-check.
"""

import numpy as np
import pandas as pd
from config import (
    DCF_PARAMS, GRAHAM_NUMBER_MULTIPLIER, TOTAL_MAX_SCORE, VERDICTS,
    SECTOR_PE_NORMS, SECTOR_PB_NORMS, CYCLICAL_SECTORS,
    PROFITABILITY, GROWTH, FINANCIAL_HEALTH, CASH_FLOW,
    MOAT_TYPES, MOAT_THRESHOLDS, SECTOR_MOAT_HINTS, EARNINGS_QUALITY, INSTITUTIONAL,
    SECTOR_DIVERSIFICATION, SECTOR_THREATS, SECTOR_TAILWINDS,
    MANAGEMENT, RED_FLAGS, COFFEE_CAN,
)


# ═══════════════════════════════════════════════
# UTILITY SCORERS
# ═══════════════════════════════════════════════

def _lower_better(value, ideal, worst, na_score=3.0):
    """Score where lower values are better (PE, PB, D/E)."""
    if pd.isna(value):
        return na_score
    if value <= ideal:
        return 10.0
    if value >= worst:
        return 0.0
    return round(10.0 * (worst - value) / (worst - ideal), 1)


def _higher_better(value, floor, ceiling, na_score=3.0):
    """Score where higher values are better (ROE, ROCE, margins)."""
    if pd.isna(value):
        return na_score
    if value >= ceiling:
        return 10.0
    if value <= floor:
        return 0.0
    return round(10.0 * (value - floor) / (ceiling - floor), 1)


def _clamp(v, lo=0.0, hi=10.0):
    return max(lo, min(hi, v))


def _avg(parts: list[float]) -> float:
    clean = [p for p in parts if not pd.isna(p)]
    return _clamp(round(sum(clean) / len(clean), 1)) if clean else 0.0


# ═══════════════════════════════════════════════
# RED FLAGS — instant rejection (Filter 11)
# ═══════════════════════════════════════════════

def check_red_flags(row: pd.Series) -> list[str]:
    """Return list of red-flag descriptions. Non-empty = reject."""
    flags: list[str] = []
    R = RED_FLAGS

    pe = row.get("pe", np.nan)
    if not pd.isna(pe) and pe > R["pe_max"]:
        flags.append(f"PE {pe:.1f} > {R['pe_max']}")

    de = row.get("debt_to_equity", np.nan)
    if not pd.isna(de) and de > R["debt_to_equity_max"]:
        flags.append(f"D/E {de:.2f} > {R['debt_to_equity_max']}")

    ic = row.get("interest_coverage", np.nan)
    if not pd.isna(ic) and ic < R["interest_coverage_min"]:
        flags.append(f"Interest coverage {ic:.1f}x < {R['interest_coverage_min']}x")

    dq = row.get("profit_declining_quarters", 0)
    if dq >= R["profit_declining_quarters"]:
        flags.append(f"Profit declining {dq} consecutive quarters")

    fcf = row.get("free_cash_flow", np.nan)
    if not pd.isna(fcf) and fcf < 0:
        flags.append("Negative free cash flow")

    mcap = row.get("market_cap_cr", np.nan)
    if not pd.isna(mcap) and mcap < R["market_cap_min_cr"]:
        flags.append(f"Market cap {mcap:.0f} Cr < {R['market_cap_min_cr']} Cr")

    ni = row.get("net_income_latest", np.nan)
    if not pd.isna(ni) and ni < 0:
        flags.append("Current year net loss")

    z = row.get("altman_z", np.nan)
    if not pd.isna(z) and z < R["altman_z_min"]:
        flags.append(f"Altman Z-Score {z:.2f} < {R['altman_z_min']} (distress)")

    f_score = row.get("piotroski_score", np.nan)
    if not pd.isna(f_score) and f_score <= R["piotroski_min"]:
        flags.append(f"Piotroski F-Score {f_score} <= {R['piotroski_min']}")

    accrual = row.get("accrual_ratio", np.nan)
    if not pd.isna(accrual) and accrual > R["accrual_ratio_max"]:
        flags.append(f"Accrual ratio {accrual:.2%} > {R['accrual_ratio_max']:.0%}")

    return flags


# ═══════════════════════════════════════════════
# DIM 1 — VALUATION (/10)
# ═══════════════════════════════════════════════

def _reverse_dcf_implied_growth(price, fcf, shares, discount_rate=0.12, terminal_growth=0.03, years=10):
    """Solve for implied growth rate using current price. Returns % or nan."""
    if pd.isna(price) or pd.isna(fcf) or pd.isna(shares) or fcf <= 0 or shares <= 0 or price <= 0:
        return np.nan

    market_value = price * shares
    # Binary search for growth rate that gives PV = market_value
    lo, hi = -0.10, 0.50
    for _ in range(50):
        g = (lo + hi) / 2
        pv = 0
        cf = fcf
        for yr in range(1, years + 1):
            cf *= (1 + g)
            pv += cf / ((1 + discount_rate) ** yr)
        terminal = (cf * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        pv += terminal / ((1 + discount_rate) ** years)
        if pv < market_value:
            lo = g
        else:
            hi = g
    return round(((lo + hi) / 2) * 100, 1)


def score_valuation(row: pd.Series, sector: str = "") -> float:
    """Sector-aware valuation: PE, PB, PEG, EV/EBITDA, P/S, MoS, reverse DCF."""
    parts: list[float] = []

    # PE vs sector
    pe = row.get("pe", np.nan)
    norms = SECTOR_PE_NORMS.get(sector, {"cheap": 12, "expensive": 40})
    parts.append(_lower_better(pe, norms["cheap"], norms["expensive"]))

    # PB vs sector
    pb = row.get("pb", np.nan)
    pb_norms = SECTOR_PB_NORMS.get(sector, {"cheap": 1, "expensive": 5})
    parts.append(_lower_better(pb, pb_norms["cheap"], pb_norms["expensive"]))

    # PEG
    parts.append(_lower_better(row.get("peg"), 0.5, 2.0))

    # EV/EBITDA
    parts.append(_lower_better(row.get("ev_ebitda"), 8, 25))

    # P/S
    parts.append(_lower_better(row.get("ps_ratio"), 2, 10))

    # Margin of safety (Graham Number)
    mos = row.get("margin_of_safety_pct", np.nan)
    if not pd.isna(mos):
        if mos >= 30:
            parts.append(10)
        elif mos >= 0:
            parts.append(5 + (mos / 30) * 5)
        else:
            parts.append(max(0, 5 + mos / 20))
    else:
        parts.append(3)

    # Reverse DCF reality check
    implied_g = row.get("reverse_dcf_implied_growth", np.nan)
    actual_g = row.get("revenue_cagr_3y", np.nan)
    if not pd.isna(implied_g) and not pd.isna(actual_g):
        gap = implied_g - actual_g  # positive = market expects MORE than actual
        if gap <= 0:
            parts.append(9)  # market expects less than reality = cheap
        elif gap <= 5:
            parts.append(6)
        elif gap <= 10:
            parts.append(3)
        else:
            parts.append(1)  # market pricing in fantasy growth
    else:
        parts.append(4)

    return _avg(parts)


# ═══════════════════════════════════════════════
# DIM 2 — PROFITABILITY (/10)
# ═══════════════════════════════════════════════

def score_profitability(row: pd.Series) -> float:
    """ROE, ROCE, ROA, margins, owner earnings yield."""
    P = PROFITABILITY
    parts: list[float] = []

    parts.append(_higher_better(row.get("roe_pct"), P["roe_min"], P["roe_excellent"]))
    parts.append(_higher_better(row.get("roce_pct"), P["roce_min"], P["roce_excellent"]))
    parts.append(_higher_better(row.get("roa_pct"), P["roa_min"], P["roa_excellent"]))
    parts.append(_higher_better(row.get("operating_margin_pct"), P["operating_margin_min"], P["operating_margin_excellent"]))
    parts.append(_higher_better(row.get("net_margin_pct"), P["net_margin_min"], P["net_margin_excellent"]))

    # Owner earnings yield
    oey = row.get("owner_earnings_yield_pct", np.nan)
    parts.append(_higher_better(oey, 2, 8, na_score=4))

    return _avg(parts)


# ═══════════════════════════════════════════════
# DIM 3 — GROWTH QUALITY (/10)
# ═══════════════════════════════════════════════

def score_growth(row: pd.Series) -> float:
    """Revenue/profit CAGR, incremental ROCE, quarterly trend, consistency."""
    G = GROWTH
    parts: list[float] = []

    parts.append(_higher_better(row.get("revenue_cagr_3y"), G["revenue_cagr_min"], G["revenue_cagr_excellent"]))
    parts.append(_higher_better(row.get("profit_cagr_3y"), G["profit_cagr_min"], G["profit_cagr_excellent"]))

    # Incremental ROCE / ROIIC
    parts.append(_higher_better(row.get("incremental_roce"), G["incremental_roce_min"], G["incremental_roce_excellent"], na_score=4))

    # Quarterly profit direction
    q_dir = row.get("quarterly_profit_direction", "unknown")
    if q_dir == "improving":
        parts.append(9)
    elif q_dir == "mixed":
        parts.append(5)
    elif q_dir == "declining":
        parts.append(1)
    else:
        parts.append(4)

    # Earnings consistency (YoY growth vs CAGR — large divergence = volatile)
    yoy = row.get("eps_growth_yoy", np.nan)
    cagr = row.get("profit_cagr_3y", np.nan)
    if not pd.isna(yoy) and not pd.isna(cagr):
        volatility = abs(yoy - cagr)
        if volatility < 5:
            parts.append(9)  # very consistent
        elif volatility < 15:
            parts.append(6)
        elif volatility < 30:
            parts.append(3)
        else:
            parts.append(1)  # erratic
    else:
        parts.append(4)

    return _avg(parts)


# ═══════════════════════════════════════════════
# DIM 4 — FINANCIAL HEALTH (/10)
# ═══════════════════════════════════════════════

def score_financial_health(row: pd.Series) -> float:
    """Altman Z-Score, D/E, interest coverage, current ratio."""
    H = FINANCIAL_HEALTH
    parts: list[float] = []

    # Altman Z-Score
    z = row.get("altman_z", np.nan)
    if not pd.isna(z):
        if z >= H["altman_z_safe"]:
            parts.append(10)
        elif z >= H["altman_z_distress"]:
            parts.append(5)
        else:
            parts.append(0)
    else:
        parts.append(4)

    # D/E
    parts.append(_lower_better(row.get("debt_to_equity"), 0.0, H["de_threshold_high"], na_score=5))

    # Interest coverage
    parts.append(_higher_better(row.get("interest_coverage"), H["interest_coverage_min"], H["interest_coverage_good"], na_score=5))

    # Current ratio
    parts.append(_higher_better(row.get("current_ratio"), H["current_ratio_min"], H["current_ratio_good"], na_score=5))

    return _avg(parts)


# ═══════════════════════════════════════════════
# DIM 5 — CASH FLOW (/10)
# ═══════════════════════════════════════════════

def score_cash_flow(row: pd.Series) -> float:
    """FCF positive, FCF conversion, FCF yield, OCF/NI, capex intensity."""
    C = CASH_FLOW
    parts: list[float] = []

    # FCF positive
    fcf = row.get("free_cash_flow", np.nan)
    if pd.isna(fcf):
        parts.append(3)
    elif fcf > 0:
        parts.append(8)
    else:
        parts.append(0)

    # FCF Conversion = FCF / Net Income (>0.8 good, >0.9 excellent)
    conv = row.get("fcf_conversion", np.nan)
    if not pd.isna(conv) and conv > 0:
        parts.append(_higher_better(conv, C["fcf_conversion_min"], C["fcf_conversion_good"], na_score=3))
    else:
        parts.append(2 if pd.isna(conv) else 0)

    # FCF yield
    parts.append(_higher_better(row.get("fcf_yield_pct"), C["fcf_yield_min"], C["fcf_yield_good"], na_score=3))

    # OCF / Net Income
    ocf_ni = row.get("ocf_ni_ratio", np.nan)
    if not pd.isna(ocf_ni) and ocf_ni > 0:
        parts.append(_higher_better(ocf_ni, C["ocf_to_net_income_min"], C["ocf_to_net_income_good"], na_score=4))
    else:
        parts.append(2 if pd.isna(ocf_ni) else 0)

    # CapEx intensity (lower = more capital-light = better)
    capex = row.get("capex_intensity", np.nan)
    if not pd.isna(capex):
        parts.append(_lower_better(capex, 0.03, 0.20, na_score=5))
    else:
        parts.append(5)

    return _avg(parts)


# ═══════════════════════════════════════════════
# DIM 6 — BUSINESS MOAT (/10)
# ═══════════════════════════════════════════════

def _identify_moat_types(row: pd.Series, sector: str = "") -> list[str]:
    """Identify which of the 7 moat types a stock likely possesses."""
    moats: list[str] = []
    hints = SECTOR_MOAT_HINTS.get(sector, [])
    MT = MOAT_THRESHOLDS

    roce = row.get("roce_pct", np.nan)
    opm = row.get("operating_margin_pct", np.nan)
    mcap = row.get("market_cap_cr", np.nan)
    rev_g = row.get("revenue_cagr_3y", np.nan)
    pb = row.get("pb", np.nan)

    if not pd.isna(opm) and opm >= MT["cost_advantage_opm"] and not pd.isna(mcap) and mcap >= MT["cost_advantage_mcap_cr"]:
        moats.append("cost_advantage")
    elif "cost_advantage" in hints and not pd.isna(opm) and opm >= MT["cost_advantage_hint_opm"]:
        moats.append("cost_advantage")

    if "network_effect" in hints and not pd.isna(rev_g) and rev_g >= MT["network_effect_rev_g"]:
        moats.append("network_effect")

    if not pd.isna(roce) and roce >= MT["switching_cost_roce"] and "switching_cost" in hints:
        moats.append("switching_cost")

    if not pd.isna(pb) and pb >= MT["intangible_pb"] and not pd.isna(opm) and opm >= MT["intangible_opm"]:
        moats.append("intangible_assets")
    elif "intangible_assets" in hints and not pd.isna(opm) and opm >= MT["intangible_hint_opm"]:
        moats.append("intangible_assets")

    if "regulatory" in hints:
        moats.append("regulatory")

    if "distribution" in hints and not pd.isna(mcap) and mcap >= MT["distribution_mcap_cr"]:
        moats.append("distribution")

    if "data_advantage" in hints and not pd.isna(opm) and opm >= MT["data_advantage_opm"]:
        moats.append("data_advantage")

    return moats


def score_moat(row: pd.Series, sector: str = "") -> tuple[float, str, list[str]]:
    """Returns (score, rating, moat_types). Includes moat trend."""
    moat_types = _identify_moat_types(row, sector)
    points = 0.0

    n_moats = len(moat_types)
    if n_moats >= 3:
        points += 3.5
    elif n_moats == 2:
        points += 2.5
    elif n_moats == 1:
        points += 1.5

    # ROCE durability
    roce = row.get("roce_pct", np.nan)
    if not pd.isna(roce):
        if roce >= 25:
            points += 2
        elif roce >= 15:
            points += 1
        elif roce >= 10:
            points += 0.5

    # Operating margin (pricing power)
    opm = row.get("operating_margin_pct", np.nan)
    if not pd.isna(opm):
        if opm >= 25:
            points += 1.5
        elif opm >= 15:
            points += 1
        elif opm >= 10:
            points += 0.5

    # Revenue growth (demand)
    rg = row.get("revenue_cagr_3y", np.nan)
    if not pd.isna(rg) and rg >= 15:
        points += 1
    elif not pd.isna(rg) and rg >= 10:
        points += 0.5

    # Moat TREND (Dorsey): widening/stable/eroding
    trend = row.get("moat_trend", "stable")
    if trend == "widening":
        points += 2
    elif trend == "stable":
        points += 1
    elif trend == "eroding":
        points -= 1  # penalty

    score = _clamp(round(points, 1))

    if score >= 7:
        rating = "Wide"
    elif score >= 4:
        rating = "Narrow"
    else:
        rating = "None"

    return score, rating, moat_types


# ═══════════════════════════════════════════════
# DIM 7 — EARNINGS QUALITY (/10)
# ═══════════════════════════════════════════════

def score_earnings_quality(row: pd.Series) -> float:
    """Piotroski F-Score, accrual ratio, OCF vs NI, gross margin trend."""
    E = EARNINGS_QUALITY
    parts: list[float] = []

    # Piotroski F-Score (0-9 mapped to 0-10)
    f_score = row.get("piotroski_score", np.nan)
    if not pd.isna(f_score):
        parts.append(round(f_score / 9 * 10, 1))
    else:
        parts.append(4)

    # Accrual ratio (lower/negative = better)
    accrual = row.get("accrual_ratio", np.nan)
    if not pd.isna(accrual):
        if accrual <= E["accrual_ratio_ideal"]:
            parts.append(10)  # negative accruals = cash-backed
        elif accrual <= E["accrual_ratio_max"]:
            parts.append(round(10 * (E["accrual_ratio_max"] - accrual) / E["accrual_ratio_max"], 1))
        else:
            parts.append(0)
    else:
        parts.append(4)

    # OCF > Net Income (quality signal from Piotroski)
    ocf = row.get("operating_cash_flow", np.nan)
    ni = row.get("net_income_latest", np.nan)
    if not pd.isna(ocf) and not pd.isna(ni):
        if ni > 0 and ocf > ni:
            parts.append(9)
        elif ni > 0 and ocf > 0:
            parts.append(5)
        else:
            parts.append(1)
    else:
        parts.append(4)

    # Margin trend
    mt = row.get("margin_trend", "stable")
    if mt == "expanding":
        parts.append(9)
    elif mt == "stable":
        parts.append(5)
    else:
        parts.append(2)

    return _avg(parts)


# ═══════════════════════════════════════════════
# DIM 8 — INSTITUTIONAL (/10)
# ═══════════════════════════════════════════════

def score_institutional(row: pd.Series) -> float:
    """Institutional/insider holdings, analyst targets."""
    parts: list[float] = []

    parts.append(_higher_better(row.get("institutional_holding_pct"), 10, 50, na_score=4))
    parts.append(_higher_better(row.get("insider_holding_pct"), 5, 50, na_score=4))

    rec = str(row.get("analyst_recommendation", "none")).lower()
    rec_map = {"strong_buy": 10, "buy": 8, "hold": 5, "underperform": 2, "sell": 0}
    parts.append(rec_map.get(rec, 4))

    target = row.get("analyst_target_price", np.nan)
    price = row.get("price", np.nan)
    if not pd.isna(target) and not pd.isna(price) and price > 0:
        upside = ((target - price) / price) * 100
        parts.append(_higher_better(upside, 0, 30, na_score=4))
    else:
        parts.append(4)

    return _avg(parts)


# ═══════════════════════════════════════════════
# DIM 9 — SECTOR & MACRO (/10)
# ═══════════════════════════════════════════════

def score_sector_macro(row: pd.Series, sector: str = "") -> float:
    """Tailwinds, threats, diversification, cyclicality — combined."""
    parts: list[float] = []

    # Sector tailwind
    tw = SECTOR_TAILWINDS.get(sector, 5)
    parts.append(float(tw))

    # Diversification
    div_base = SECTOR_DIVERSIFICATION.get(sector, 5)
    mcap = row.get("market_cap_cr", np.nan)
    if not pd.isna(mcap) and mcap >= 100000:
        div_base = min(10, div_base + 1)
    elif not pd.isna(mcap) and mcap < 5000:
        div_base = max(0, div_base - 1)
    parts.append(float(div_base))

    # Future threats
    threat_base = SECTOR_THREATS.get(sector, 5)
    de = row.get("debt_to_equity", np.nan)
    if not pd.isna(de) and de > 1.0:
        threat_base = max(0, threat_base - 1)
    q_dir = row.get("quarterly_profit_direction", "unknown")
    if q_dir == "declining":
        threat_base = max(0, threat_base - 1)
    parts.append(float(threat_base))

    # Company growth premium (above sector base)
    rg = row.get("revenue_cagr_3y", np.nan)
    if not pd.isna(rg) and rg >= 20:
        parts.append(8)
    elif not pd.isna(rg) and rg >= 10:
        parts.append(6)
    elif not pd.isna(rg):
        parts.append(3)
    else:
        parts.append(4)

    return _avg(parts)


# ═══════════════════════════════════════════════
# DIM 10 — MANAGEMENT (/10)
# ═══════════════════════════════════════════════

def score_management(row: pd.Series) -> float:
    """ROCE consistency, payout, debt discipline, margin trend, dilution, FCF."""
    M = MANAGEMENT
    parts: list[float] = []

    # Capital allocation (ROCE)
    parts.append(_higher_better(row.get("roce_pct"), 10, 25, na_score=4))

    # Payout ratio (ideal 15-60%)
    payout = row.get("payout_ratio_pct", np.nan)
    if pd.isna(payout):
        parts.append(4)
    elif M["payout_ratio_ideal_min"] <= payout <= M["payout_ratio_ideal_max"]:
        parts.append(8)
    elif payout > M["payout_ratio_ideal_max"]:
        parts.append(5)
    elif payout > 0:
        parts.append(6)
    else:
        parts.append(3)

    # Debt discipline
    parts.append(_lower_better(row.get("debt_to_equity"), 0.0, 1.5, na_score=5))

    # Margin trend
    mt = row.get("margin_trend", "stable")
    if mt == "expanding":
        parts.append(9)
    elif mt == "stable":
        parts.append(6)
    else:
        parts.append(3)

    # Share dilution
    diluted = row.get("shares_diluted", False)
    parts.append(3 if diluted else 7)

    # FCF positive
    fcf = row.get("free_cash_flow", np.nan)
    if pd.isna(fcf):
        parts.append(4)
    elif fcf > 0:
        parts.append(8)
    else:
        parts.append(2)

    return _avg(parts)


# ═══════════════════════════════════════════════
# COMPOSITE SCORING (100-point system)
# ═══════════════════════════════════════════════

def score_stock_full(row: pd.Series, sector: str = "") -> dict:
    """Run all 10 dimension scorers. Returns results dict."""
    results: dict = {}

    # Red flags
    flags = check_red_flags(row)
    results["red_flags"] = "; ".join(flags) if flags else ""
    results["is_rejected"] = len(flags) > 0

    # 10 dimensions
    results["valuation_score"] = score_valuation(row, sector)
    results["profitability_score"] = score_profitability(row)
    results["growth_score"] = score_growth(row)
    results["financial_health_score"] = score_financial_health(row)
    results["cash_flow_score"] = score_cash_flow(row)

    moat_score, moat_rating, moat_types = score_moat(row, sector)
    results["moat_score"] = moat_score
    results["moat"] = moat_rating
    results["moat_types"] = ", ".join(moat_types) if moat_types else "None identified"

    results["earnings_quality_score"] = score_earnings_quality(row)
    results["institutional_score"] = score_institutional(row)
    results["sector_macro_score"] = score_sector_macro(row, sector)
    results["management_score"] = score_management(row)

    # Total
    total = sum([
        results["valuation_score"],
        results["profitability_score"],
        results["growth_score"],
        results["financial_health_score"],
        results["cash_flow_score"],
        results["moat_score"],
        results["earnings_quality_score"],
        results["institutional_score"],
        results["sector_macro_score"],
        results["management_score"],
    ])
    results["total_score"] = round(total, 1)

    # Verdict
    if results["is_rejected"]:
        results["verdict"] = "REJECT"
    elif total >= VERDICTS["GEM"]["min"]:
        results["verdict"] = "GEM"
    elif total >= VERDICTS["STRONG"]["min"]:
        results["verdict"] = "STRONG"
    elif total >= VERDICTS["ACCEPTABLE"]["min"]:
        results["verdict"] = "ACCEPTABLE"
    elif total >= VERDICTS["WATCHLIST"]["min"]:
        results["verdict"] = "WATCHLIST"
    else:
        results["verdict"] = "REJECT"

    return results


# ═══════════════════════════════════════════════
# MAGIC FORMULA (Greenblatt cross-check)
# ═══════════════════════════════════════════════

def magic_formula_rank(df: pd.DataFrame) -> pd.DataFrame:
    """Add Magic Formula combined rank (earnings yield + ROIC rank)."""
    df = df.copy()

    # Earnings Yield = EBIT / EV (approximate with ev_ebitda inverse)
    ev_ebitda = df.get("ev_ebitda", pd.Series(dtype=float))
    df["earnings_yield_pct"] = ev_ebitda.apply(
        lambda x: round(1 / x * 100, 2) if not pd.isna(x) and x > 0 else np.nan
    )

    # ROIC proxy = ROCE
    df["magic_ey_rank"] = df["earnings_yield_pct"].rank(ascending=False, na_option="bottom")
    df["magic_roic_rank"] = df["roce_pct"].rank(ascending=False, na_option="bottom") if "roce_pct" in df.columns else np.nan
    df["magic_formula_rank"] = df["magic_ey_rank"] + df["magic_roic_rank"]
    df["magic_formula_rank"] = df["magic_formula_rank"].rank(ascending=True, na_option="bottom").astype(int)

    return df


# ═══════════════════════════════════════════════
# INTRINSIC VALUE
# ═══════════════════════════════════════════════

def graham_number(eps, book_value) -> float:
    if pd.isna(eps) or pd.isna(book_value) or eps <= 0 or book_value <= 0:
        return np.nan
    return round(np.sqrt(GRAHAM_NUMBER_MULTIPLIER * eps * book_value), 2)


def dcf_intrinsic_value(
    free_cash_flow: float,
    growth_rate: float = 0.12,
    shares_outstanding: float = 1,
) -> float:
    """Company-specific DCF with growth fade after year 5."""
    if pd.isna(free_cash_flow) or free_cash_flow <= 0 or shares_outstanding <= 0:
        return np.nan

    dr = DCF_PARAMS["discount_rate"]
    tg = DCF_PARAMS["terminal_growth_rate"]
    years = DCF_PARAMS["projection_years"]
    fade_start = DCF_PARAMS["fade_start_year"]

    fcf = free_cash_flow
    projected = []
    for yr in range(1, years + 1):
        # Fade growth toward terminal after fade_start
        if yr <= fade_start:
            g = growth_rate
        else:
            fade_pct = (yr - fade_start) / (years - fade_start)
            g = growth_rate + (tg - growth_rate) * fade_pct
        fcf *= (1 + g)
        projected.append(fcf / ((1 + dr) ** yr))

    terminal = (fcf * (1 + tg)) / (dr - tg)
    terminal_pv = terminal / ((1 + dr) ** years)

    return round((sum(projected) + terminal_pv) / shares_outstanding, 2)


def margin_of_safety(current_price, intrinsic_value) -> float:
    if pd.isna(intrinsic_value) or intrinsic_value <= 0 or pd.isna(current_price):
        return np.nan
    return round(((intrinsic_value - current_price) / intrinsic_value) * 100, 2)


# ═══════════════════════════════════════════════
# COFFEE CAN CHECK
# ═══════════════════════════════════════════════

def coffee_can_eligible(row: pd.Series) -> bool:
    rg = row.get("revenue_cagr_3y", np.nan)
    roce = row.get("roce_pct", np.nan)
    de = row.get("debt_to_equity", np.nan)
    if pd.isna(rg) or pd.isna(roce):
        return False
    return (
        rg >= COFFEE_CAN["revenue_cagr_min"]
        and roce >= COFFEE_CAN["roce_min"]
        and (pd.isna(de) or de <= COFFEE_CAN["debt_to_equity_max"])
    )


# ═══════════════════════════════════════════════
# FULL ANALYSIS PIPELINE
# ═══════════════════════════════════════════════

def analyze_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Complete pipeline: intrinsic value, 10-dim scoring, moat, Coffee Can, MF rank."""
    if df.empty:
        return df

    df = df.copy()

    # Graham Number
    df["graham_number"] = df.apply(
        lambda r: graham_number(r.get("eps"), r.get("book_value")), axis=1,
    )
    df["margin_of_safety_pct"] = df.apply(
        lambda r: margin_of_safety(r.get("price"), r.get("graham_number")), axis=1,
    )

    # Company-specific DCF (use revenue CAGR instead of uniform 12%)
    df["dcf_intrinsic"] = df.apply(
        lambda r: dcf_intrinsic_value(
            r.get("free_cash_flow", np.nan),
            growth_rate=min(max((r.get("revenue_cagr_3y", 12) or 12) / 100, 0.03), 0.25),
            shares_outstanding=r.get("shares_outstanding", np.nan),
        ),
        axis=1,
    )
    df["dcf_margin_of_safety_pct"] = df.apply(
        lambda r: margin_of_safety(r.get("price"), r.get("dcf_intrinsic")), axis=1,
    )

    # Reverse DCF implied growth
    df["reverse_dcf_implied_growth"] = df.apply(
        lambda r: _reverse_dcf_implied_growth(
            r.get("price"), r.get("free_cash_flow"), r.get("shares_outstanding"),
        ),
        axis=1,
    )

    # 10-dimension scoring
    score_df = df.apply(
        lambda row: score_stock_full(row, row.get("sector", "")),
        axis=1, result_type="expand",
    )
    df = pd.concat([df, score_df], axis=1)

    # Coffee Can
    df["coffee_can"] = df.apply(coffee_can_eligible, axis=1)

    # Magic Formula cross-check
    df = magic_formula_rank(df)

    # Rank by total score
    df = df.sort_values("total_score", ascending=False)

    # Validate expected columns exist
    _required = ["verdict", "total_score", "sector", "ticker"]
    missing = [c for c in _required if c not in df.columns]
    if missing:
        raise ValueError(f"analyze_dataframe: missing expected columns {missing}")

    return df
