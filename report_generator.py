"""
Report Generator — 10-Filter, 100-Point HTML Report
====================================================
Generates a professional dark-themed HTML report from screening results.
Outputs: report.html (dashboard + all stocks) + per-sector pages.

Usage:
    Called by screener.py → build_report(df)
    Or standalone:  python report_generator.py
"""

import os
import math
from datetime import datetime
from html import escape

import numpy as np
import pandas as pd

from config import FILTER_REFERENCE, VERDICTS, NSE_SECTORS, SECTOR_PE_NORMS, CYCLICAL_SECTORS


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
REPORT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_REPORT = os.path.join(REPORT_DIR, "report.html")

VERDICT_COLORS = {
    "GEM":        ("#00e676", "#1b5e20"),  # bright green on dark green
    "STRONG":     ("#64dd17", "#33691e"),   # lime on dark olive
    "ACCEPTABLE": ("#ffab00", "#4e3a00"),   # amber on dark amber
    "WATCHLIST":  ("#ff9100", "#4e2600"),   # orange on dark brown
    "REJECT":     ("#ff1744", "#4a0012"),   # red on dark red
}

DIMENSION_NAMES = [
    ("valuation_score",        "Valuation"),
    ("profitability_score",    "Profitability"),
    ("growth_score",           "Growth"),
    ("financial_health_score", "Fin. Health"),
    ("cash_flow_score",        "Cash Flow"),
    ("moat_score",             "Moat"),
    ("earnings_quality_score", "Earnings Q."),
    ("institutional_score",    "Institutional"),
    ("sector_macro_score",     "Sector"),
    ("management_score",       "Management"),
]

MOAT_TREND_ICONS = {
    "widening": ("&#9650;", "#00e676"),  # ▲ green
    "stable":   ("&#9644;", "#ffab00"),  # ▬ amber
    "eroding":  ("&#9660;", "#ff1744"),  # ▼ red
}


# ─────────────────────────────────────────────
# Formatting helpers
# ─────────────────────────────────────────────

def _is_valid_number(val) -> bool:
    """Check if value is a usable numeric (not None, NaN, or Inf)."""
    if val is None:
        return False
    if not isinstance(val, (int, float, np.integer, np.floating)):
        return False
    if math.isnan(float(val)) or math.isinf(float(val)):
        return False
    return True


def _fmt(val, fmt=".1f", prefix="", suffix="", na="—"):
    """Format a numeric value for HTML display."""
    if not _is_valid_number(val):
        return na
    try:
        return f"{prefix}{val:{fmt}}{suffix}"
    except (ValueError, TypeError):
        return str(val)


def _fmt_cr(val, na="—"):
    """Format market cap in Crores."""
    if not _is_valid_number(val):
        return na
    if val >= 100000:
        return f"{val/100000:.1f}L Cr"
    return f"{val:,.0f} Cr"


def _pct(val, na="—"):
    return _fmt(val, ".1f", suffix="%", na=na)


def _score_color(score, max_val=10):
    """Return color hex based on score ratio."""
    if not _is_valid_number(score):
        return "#555"
    ratio = score / max_val
    if ratio >= 0.75:
        return "#00e676"
    if ratio >= 0.55:
        return "#64dd17"
    if ratio >= 0.40:
        return "#ffab00"
    if ratio >= 0.25:
        return "#ff9100"
    return "#ff1744"


def _verdict_badge(verdict):
    fg, bg = VERDICT_COLORS.get(verdict, ("#aaa", "#333"))
    return f'<span class="badge" style="background:{bg};color:{fg};border:1px solid {fg}">{escape(verdict)}</span>'


def _bar_html(score, max_val=10, width_px=120):
    """Mini score bar."""
    pct_fill = min(100, max(0, (score / max_val) * 100)) if score and not math.isnan(score) else 0
    color = _score_color(score, max_val)
    return (
        f'<div class="bar-bg" style="width:{width_px}px">'
        f'<div class="bar-fill" style="width:{pct_fill:.0f}%;background:{color}"></div>'
        f'<span class="bar-label">{_fmt(score, ".1f")}</span>'
        f'</div>'
    )


# ─────────────────────────────────────────────
# CSS (shared)
# ─────────────────────────────────────────────

def _css():
    return """
<style>
:root {
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #e6edf3; --text2: #8b949e; --accent: #58a6ff;
    --green: #00e676; --red: #ff1744; --amber: #ffab00;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--bg); color:var(--text); font-family:'Segoe UI',system-ui,-apple-system,sans-serif; line-height:1.5; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }

.container { max-width:1400px; margin:0 auto; padding:20px; }
h1 { font-size:1.8rem; margin-bottom:8px; }
h2 { font-size:1.4rem; margin:24px 0 12px; border-bottom:1px solid var(--border); padding-bottom:6px; }
h3 { font-size:1.1rem; margin:16px 0 8px; color:var(--accent); }

.meta { color:var(--text2); font-size:0.85rem; margin-bottom:16px; }
.grid { display:grid; gap:16px; }
.grid-4 { grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); }
.grid-5 { grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); }

/* Dashboard cards */
.stat-card { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:16px; text-align:center; }
.stat-card .num { font-size:2rem; font-weight:700; }
.stat-card .label { color:var(--text2); font-size:0.82rem; text-transform:uppercase; letter-spacing:0.5px; }

/* Badges */
.badge { display:inline-block; padding:2px 10px; border-radius:12px; font-weight:600; font-size:0.78rem; letter-spacing:0.5px; }

/* Score bars */
.bar-bg { display:inline-block; background:#21262d; border-radius:4px; height:16px; position:relative; vertical-align:middle; }
.bar-fill { height:100%; border-radius:4px; transition:width 0.3s; }
.bar-label { position:absolute; right:4px; top:-1px; font-size:0.7rem; color:var(--text); font-weight:600; line-height:16px; }

/* Stock cards */
.stock-card { background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:18px; margin-bottom:16px; }
.stock-header { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:12px; }
.stock-title { font-size:1.15rem; font-weight:700; }
.stock-subtitle { color:var(--text2); font-size:0.82rem; }

.metrics-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:8px 16px; font-size:0.85rem; margin:10px 0; }
.metric { display:flex; justify-content:space-between; padding:2px 0; border-bottom:1px solid #1c2128; }
.metric .k { color:var(--text2); }
.metric .v { font-weight:600; }

.dim-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:6px 16px; font-size:0.82rem; margin:8px 0; }
.dim-row { display:flex; align-items:center; gap:6px; }
.dim-name { width:90px; color:var(--text2); flex-shrink:0; }

.flags { color:var(--red); font-size:0.82rem; margin-top:6px; }
.flag-item { display:inline-block; background:#4a0012; border:1px solid var(--red); border-radius:4px; padding:1px 8px; margin:2px; font-size:0.78rem; }

.moat-tag { display:inline-block; background:#1a2332; border:1px solid #30506d; border-radius:4px; padding:1px 7px; font-size:0.75rem; color:var(--accent); margin:2px; }

.coffee-can { display:inline-block; background:#1b3a1b; border:1px solid var(--green); border-radius:4px; padding:1px 8px; font-size:0.75rem; color:var(--green); margin-left:6px; }

/* Tables */
table { width:100%; border-collapse:collapse; font-size:0.82rem; margin:10px 0; }
th { background:var(--surface); color:var(--text2); text-align:left; padding:8px 10px; border-bottom:2px solid var(--border); font-weight:600; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.5px; }
td { padding:6px 10px; border-bottom:1px solid var(--border); }
tr:hover td { background:#1c2128; }

/* Filter ref */
.filter-ref { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:16px; margin:8px 0; }
.filter-ref h4 { color:var(--accent); margin-bottom:6px; }
.filter-ref p { color:var(--text2); font-size:0.82rem; margin-bottom:6px; }
.filter-ref ul { list-style:disc; padding-left:20px; color:var(--text2); font-size:0.8rem; }
.filter-ref li { margin:2px 0; }
.filter-src { color:#555; font-size:0.72rem; font-style:italic; }

/* Sector nav */
.sector-nav { display:flex; flex-wrap:wrap; gap:8px; margin:12px 0; }
.sector-pill { display:inline-block; padding:4px 14px; border-radius:16px; background:var(--surface); border:1px solid var(--border); color:var(--text2); font-size:0.82rem; cursor:pointer; transition:all 0.2s; }
.sector-pill:hover, .sector-pill.active { background:var(--accent); color:var(--bg); border-color:var(--accent); }

/* Verdict counts row */
.verdict-row { display:flex; gap:12px; flex-wrap:wrap; margin:12px 0; }
.verdict-chip { padding:6px 16px; border-radius:8px; font-weight:600; font-size:0.9rem; }

/* Tabs */
.tab-bar { display:flex; gap:0; border-bottom:2px solid var(--border); margin:16px 0 0; }
.tab { padding:8px 20px; cursor:pointer; color:var(--text2); font-size:0.9rem; border-bottom:2px solid transparent; margin-bottom:-2px; transition:all 0.2s; }
.tab:hover { color:var(--text); }
.tab.active { color:var(--accent); border-bottom-color:var(--accent); }
.tab-panel { display:none; padding:16px 0; }
.tab-panel.active { display:block; }

/* Responsive */
@media (max-width:768px) {
    .metrics-grid { grid-template-columns:1fr; }
    .dim-grid { grid-template-columns:1fr; }
    .grid-4 { grid-template-columns:repeat(2,1fr); }
}

/* Sort indicators */
.sort-badge { color:var(--accent); font-size:0.8em; margin-left:2px; }
.sort-badge sup { font-size:0.7em; }
thead th { user-select:none; white-space:nowrap; }
</style>
"""


# ─────────────────────────────────────────────
# JS (tabs + sorting)
# ─────────────────────────────────────────────

def _js():
    return """
<script>
function showTab(tabId) {
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    document.querySelector('[data-tab="'+tabId+'"]').classList.add('active');
}

var _sortState = {};

function sortTable(tableId, colIdx, numeric, evt) {
    if (!_sortState[tableId]) _sortState[tableId] = [];

    if (evt && evt.shiftKey) {
        var idx = -1;
        for (var k = 0; k < _sortState[tableId].length; k++) {
            if (_sortState[tableId][k].col === colIdx) { idx = k; break; }
        }
        if (idx >= 0) {
            _sortState[tableId][idx].asc = !_sortState[tableId][idx].asc;
        } else {
            _sortState[tableId].push({col: colIdx, asc: true, numeric: numeric});
        }
    } else {
        if (_sortState[tableId].length === 1 && _sortState[tableId][0].col === colIdx) {
            _sortState[tableId][0].asc = !_sortState[tableId][0].asc;
        } else {
            _sortState[tableId] = [{col: colIdx, asc: true, numeric: numeric}];
        }
    }

    var st = _sortState[tableId];
    var table = document.getElementById(tableId);
    if (!table) return;
    var tbody = table.querySelector('tbody');
    if (!tbody) return;
    var rows = [];
    var trs = tbody.getElementsByTagName('tr');
    for (var i = 0; i < trs.length; i++) rows.push(trs[i]);

    rows.sort(function(ra, rb) {
        for (var si = 0; si < st.length; si++) {
            var s = st[si];
            var cellA = ra.cells[s.col];
            var cellB = rb.cells[s.col];
            var va = (cellA.getAttribute('data-val') !== null) ? cellA.getAttribute('data-val') : cellA.textContent.trim();
            var vb = (cellB.getAttribute('data-val') !== null) ? cellB.getAttribute('data-val') : cellB.textContent.trim();
            var cmp = 0;
            if (s.numeric) {
                var na = parseFloat(va);
                var nb = parseFloat(vb);
                if (isNaN(na)) na = -999999;
                if (isNaN(nb)) nb = -999999;
                cmp = na - nb;
            } else {
                va = va.toLowerCase();
                vb = vb.toLowerCase();
                if (va < vb) cmp = -1;
                else if (va > vb) cmp = 1;
            }
            if (cmp !== 0) return s.asc ? cmp : -cmp;
        }
        return 0;
    });

    for (var j = 0; j < rows.length; j++) tbody.appendChild(rows[j]);

    // Update sort indicators
    var ths = table.querySelectorAll('thead th');
    for (var t = 0; t < ths.length; t++) {
        var badge = ths[t].querySelector('.sort-badge');
        if (badge) badge.parentNode.removeChild(badge);
    }
    for (var m = 0; m < st.length; m++) {
        var th = ths[st[m].col];
        var arrow = st[m].asc ? '\\u25B2' : '\\u25BC';
        var pri = st.length > 1 ? '<sup>' + (m + 1) + '</sup>' : '';
        var span = document.createElement('span');
        span.className = 'sort-badge';
        span.innerHTML = ' ' + arrow + pri;
        th.appendChild(span);
    }
}
</script>
"""


# ═══════════════════════════════════════════════
# Fund Manager Picks — Qualitative Overlay
# ═══════════════════════════════════════════════

FUND_MANAGERS = [
    {
        "name": "Sankaran Naren",
        "firm": "ICICI Prudential AMC",
        "strategy": "Contrarian Value",
        "philosophy": "Buys beaten-down sectors and out-of-favour large caps at deep discounts. Rotates into cyclicals at trough valuations. Mean-reversion thesis.",
    },
    {
        "name": "Raamdeo Agrawal",
        "firm": "Motilal Oswal",
        "strategy": "QGLP",
        "philosophy": "Quality-Growth-Longevity-Price. Seeks 100-baggers: consistent ROE > 20%, earnings CAGR > 15%, wide moat, at reasonable PE.",
    },
    {
        "name": "Rajeev Thakkar",
        "firm": "PPFAS Mutual Fund",
        "strategy": "GARP + Cash Flow",
        "philosophy": "Cash-flow obsessed GARP investor. OCF must back reported earnings. Low churn, high conviction, avoids fads and IPO frenzies.",
    },
    {
        "name": "Bharat Shah",
        "firm": "ASK Investment Managers",
        "strategy": "Quality Compounder",
        "philosophy": "Only extraordinary businesses. ROCE > 20% sustained for decades, pricing power as the ultimate moat, near-zero debt. Never sell a great company.",
    },
    {
        "name": "Saurabh Mukherjea",
        "firm": "Marcellus Investment",
        "strategy": "Coffee Can / Consistent Compounders",
        "philosophy": "Buy and forget for 10 years. Revenue CAGR ≥ 10%, ROCE ≥ 15%, D/E ≤ 1.0. Clean governance, minimal capital needs.",
    },
    {
        "name": "Prashant Jain",
        "firm": "3P Investment Managers",
        "strategy": "Growth at Reasonable Price",
        "philosophy": "Patient growth investor. Buys visible earnings growth > 12% at PE below sector median. Concentrated, long holding periods.",
    },
    {
        "name": "Nilesh Shah",
        "firm": "Kotak AMC",
        "strategy": "Balanced Quality",
        "philosophy": "Balanced scorecard approach — no single dimension should be weak. Moderate ROCE, low debt, decent growth, institutional backing.",
    },
    {
        "name": "Madhusudan Kela",
        "firm": "MK Ventures",
        "strategy": "Growth Momentum",
        "philosophy": "Backs high-growth companies in secular trends. Revenue/profit CAGR > 15%, strong moat, willing to pay premium for growth visibility.",
    },
    {
        "name": "Kenneth Andrade",
        "firm": "Old Bridge Capital",
        "strategy": "Capital Cycle / Earnings Recovery",
        "philosophy": "Invests in capex-cycle recoveries and earnings turnarounds. Contrarian on cyclicals, looks for improving ROCE and sector upcycles.",
    },
    {
        "name": "Anand Srinivasan",
        "firm": "Independent Investor",
        "strategy": "Cash Flow + PEG",
        "philosophy": "PEG < 1.5, positive FCF, pricing power. Focuses on consistent compounders with cash-backed earnings and operating leverage.",
    },
]


def _match_fund_managers(row) -> list[dict]:
    """Match a stock row against fund manager criteria. Returns list of picks."""
    picks = []
    score = row.get("total_score", 0)
    verdict = row.get("verdict", "REJECT")
    pe = row.get("pe")
    roce = row.get("roce_pct")
    roe = row.get("roe_pct")
    de = row.get("debt_to_equity")
    rev_cagr = row.get("revenue_cagr_3y")
    profit_cagr = row.get("profit_cagr_3y")
    fcf_conv = row.get("fcf_conversion")
    ocf_ni = row.get("ocf_ni_ratio")
    piotroski = row.get("piotroski_score")
    moat = str(row.get("moat", "None"))
    moat_trend = str(row.get("moat_trend", "stable"))
    moat_score = row.get("moat_score", 0)
    coffee_can = bool(row.get("coffee_can"))
    sector = str(row.get("sector", ""))
    mos_g = row.get("margin_of_safety_pct")
    mos_d = row.get("dcf_margin_of_safety_pct")
    peg = row.get("peg")
    op_margin = row.get("operating_margin_pct")
    val_score = row.get("valuation_score", 0)
    prof_score = row.get("profitability_score", 0)
    growth_score = row.get("growth_score", 0)
    health_score = row.get("financial_health_score", 0)
    cashflow_score = row.get("cash_flow_score", 0)
    eq_score = row.get("earnings_quality_score", 0)
    mgmt_score = row.get("management_score", 0)
    incr_roce = row.get("incremental_roce")
    altman_z = row.get("altman_z")

    v = _is_valid_number

    # PE norm for sector
    pe_norm = SECTOR_PE_NORMS.get(sector, {}).get("avg", 25)
    pe_cheap = SECTOR_PE_NORMS.get(sector, {}).get("cheap", 15)
    is_cyclical = sector in CYCLICAL_SECTORS

    # ── 1. Sankaran Naren — Contrarian Value ──
    # Cheap PE (below sector cheap threshold), positive MoS, any ROCE
    naren_match = False
    naren_reasons = []
    if v(pe) and pe < pe_cheap:
        naren_reasons.append(f"PE {pe:.1f} below sector cheap ({pe_cheap})")
        naren_match = True
    if v(mos_g) and mos_g > 15:
        naren_reasons.append(f"Graham MoS +{mos_g:.0f}%")
        naren_match = True
    if v(mos_d) and mos_d > 15:
        naren_reasons.append(f"DCF MoS +{mos_d:.0f}%")
        naren_match = True
    if is_cyclical and val_score >= 6:
        naren_reasons.append(f"Cyclical sector at reasonable valuation")
        naren_match = True
    if naren_match and naren_reasons:
        status = "STRONG BUY" if (v(pe) and pe < pe_cheap and score >= 60) else "BUY" if score >= 55 else "HOLD"
        picks.append({"manager_idx": 0, "reasons": naren_reasons, "status": status})

    # ── 2. Raamdeo Agrawal — QGLP ──
    qglp_reasons = []
    q_ok = v(roce) and roce >= 15 and v(roe) and roe >= 15
    g_ok = (v(rev_cagr) and rev_cagr >= 15) or (v(profit_cagr) and profit_cagr >= 15)
    l_ok = moat in ("Wide", "Narrow") and moat_trend != "eroding"
    p_ok = v(pe) and pe <= pe_norm * 1.5
    if q_ok:
        qglp_reasons.append(f"Quality: ROCE {roce:.1f}%, ROE {roe:.1f}%")
    if g_ok:
        growth_val = rev_cagr if v(rev_cagr) and rev_cagr >= 15 else profit_cagr
        qglp_reasons.append(f"Growth: {growth_val:.1f}% CAGR")
    if l_ok:
        qglp_reasons.append(f"Longevity: {moat} moat, {moat_trend}")
    if p_ok:
        qglp_reasons.append(f"Price: PE {pe:.1f} vs norm {pe_norm}")
    if q_ok and g_ok and l_ok:
        status = "STRONG BUY" if (p_ok and score >= 65) else "BUY" if score >= 55 else "HOLD"
        picks.append({"manager_idx": 1, "reasons": qglp_reasons, "status": status})

    # ── 3. Rajeev Thakkar — GARP + Cash Flow ──
    thakkar_reasons = []
    fcf_ok = v(fcf_conv) and fcf_conv > 0.6
    ocf_ok = v(ocf_ni) and ocf_ni > 0.8
    piot_ok = v(piotroski) and piotroski >= 5
    val_ok = v(pe) and pe <= pe_norm * 1.2
    if fcf_ok:
        thakkar_reasons.append(f"FCF conversion {fcf_conv:.2f}")
    if ocf_ok:
        thakkar_reasons.append(f"OCF/NI {ocf_ni:.2f} — earnings cash-backed")
    if piot_ok:
        thakkar_reasons.append(f"Piotroski {piotroski:.0f}/9")
    if val_ok:
        thakkar_reasons.append(f"PE {pe:.1f} ≤ sector norm")
    if (fcf_ok or ocf_ok) and piot_ok:
        status = "STRONG BUY" if (fcf_ok and ocf_ok and val_ok and score >= 65) else "BUY" if score >= 55 else "HOLD"
        picks.append({"manager_idx": 2, "reasons": thakkar_reasons, "status": status})

    # ── 4. Bharat Shah — Quality Compounder ──
    bharat_reasons = []
    roce_high = v(roce) and roce >= 20
    moat_wide = moat == "Wide"
    debt_low = v(de) and de < 0.5
    if roce_high:
        bharat_reasons.append(f"ROCE {roce:.1f}% — compounding machine")
    if moat_wide:
        bharat_reasons.append(f"Wide moat ({moat_trend})")
    if debt_low:
        bharat_reasons.append(f"D/E {de:.2f} — near-zero leverage")
    if v(op_margin) and op_margin >= 20:
        bharat_reasons.append(f"Operating margin {op_margin:.1f}% — pricing power")
    if roce_high and (moat_wide or moat_score >= 6):
        status = "STRONG BUY" if (debt_low and score >= 65) else "BUY" if score >= 55 else "HOLD"
        picks.append({"manager_idx": 3, "reasons": bharat_reasons, "status": status})

    # ── 5. Saurabh Mukherjea — Coffee Can ──
    if coffee_can:
        cc_reasons = []
        if v(rev_cagr):
            cc_reasons.append(f"Rev CAGR {rev_cagr:.1f}% ≥ 10%")
        if v(roce):
            cc_reasons.append(f"ROCE {roce:.1f}% ≥ 15%")
        if v(de):
            cc_reasons.append(f"D/E {de:.2f} ≤ 1.0")
        status = "STRONG BUY" if score >= 65 else "BUY" if score >= 55 else "HOLD"
        picks.append({"manager_idx": 4, "reasons": cc_reasons, "status": status})

    # ── 6. Prashant Jain — Growth at Reasonable Price ──
    pj_reasons = []
    growth_ok = v(rev_cagr) and rev_cagr >= 12
    roe_ok = v(roe) and roe >= 12
    pe_reasonable = v(pe) and pe <= pe_norm
    if growth_ok:
        pj_reasons.append(f"Rev CAGR {rev_cagr:.1f}%")
    if roe_ok:
        pj_reasons.append(f"ROE {roe:.1f}%")
    if pe_reasonable:
        pj_reasons.append(f"PE {pe:.1f} ≤ sector avg {pe_norm}")
    if growth_ok and roe_ok and pe_reasonable:
        status = "STRONG BUY" if score >= 65 else "BUY" if score >= 55 else "HOLD"
        picks.append({"manager_idx": 5, "reasons": pj_reasons, "status": status})

    # ── 7. Nilesh Shah — Balanced Quality ──
    dims = [val_score, prof_score, growth_score, health_score, cashflow_score,
            row.get("moat_score", 0), eq_score, mgmt_score]
    min_dim = min(d for d in dims if v(d)) if any(v(d) for d in dims) else 0
    balanced = min_dim >= 4 and v(roce) and roce >= 12
    if balanced:
        ns_reasons = [f"Balanced: min dimension {min_dim:.1f}/10"]
        if v(roce):
            ns_reasons.append(f"ROCE {roce:.1f}%")
        if v(de) and de < 1.5:
            ns_reasons.append(f"D/E {de:.2f}")
        status = "STRONG BUY" if (min_dim >= 5 and score >= 65) else "BUY" if score >= 55 else "HOLD"
        picks.append({"manager_idx": 6, "reasons": ns_reasons, "status": status})

    # ── 8. Madhusudan Kela — Growth Momentum ──
    kela_reasons = []
    high_growth = (v(rev_cagr) and rev_cagr >= 15) or (v(profit_cagr) and profit_cagr >= 15)
    strong_moat = moat in ("Wide", "Narrow")
    if high_growth and strong_moat:
        if v(rev_cagr) and rev_cagr >= 15:
            kela_reasons.append(f"Rev CAGR {rev_cagr:.1f}%")
        if v(profit_cagr) and profit_cagr >= 15:
            kela_reasons.append(f"Profit CAGR {profit_cagr:.1f}%")
        kela_reasons.append(f"{moat} moat — sustainable growth")
        status = "STRONG BUY" if score >= 70 else "BUY" if score >= 55 else "HOLD"
        picks.append({"manager_idx": 7, "reasons": kela_reasons, "status": status})

    # ── 9. Kenneth Andrade — Capital Cycle / Earnings Recovery ──
    ka_reasons = []
    recovery = moat_trend == "widening" or (v(incr_roce) and incr_roce > 15)
    cyclical_cheap = is_cyclical and v(pe) and pe < pe_cheap * 1.2
    if recovery and (is_cyclical or val_score >= 6):
        if moat_trend == "widening":
            ka_reasons.append("Moat widening — earnings improving")
        if v(incr_roce) and incr_roce > 15:
            ka_reasons.append(f"Incremental ROCE {incr_roce:.1f}%")
        if cyclical_cheap:
            ka_reasons.append(f"Cyclical PE {pe:.1f} near trough")
        if v(altman_z) and altman_z > 1.81:
            ka_reasons.append(f"Altman Z {altman_z:.2f} — no distress")
        status = "STRONG BUY" if score >= 65 else "BUY" if score >= 55 else "HOLD"
        picks.append({"manager_idx": 8, "reasons": ka_reasons, "status": status})

    # ── 10. Anand Srinivasan — Cash Flow + PEG ──
    as_reasons = []
    peg_ok = v(peg) and 0 < peg < 1.5
    fcf_pos = v(fcf_conv) and fcf_conv > 0.5
    margin_ok = v(op_margin) and op_margin >= 15
    rev_ok = v(rev_cagr) and rev_cagr >= 10
    if (peg_ok or (fcf_pos and margin_ok)) and rev_ok:
        if peg_ok:
            as_reasons.append(f"PEG {peg:.2f} < 1.5")
        if fcf_pos:
            as_reasons.append(f"FCF conversion {fcf_conv:.2f}")
        if margin_ok:
            as_reasons.append(f"Op. margin {op_margin:.1f}% — pricing power")
        if rev_ok:
            as_reasons.append(f"Rev CAGR {rev_cagr:.1f}%")
        status = "STRONG BUY" if (peg_ok and fcf_pos and score >= 65) else "BUY" if score >= 55 else "HOLD"
        picks.append({"manager_idx": 9, "reasons": as_reasons, "status": status})

    return picks


def _status_badge(status: str) -> str:
    """Color-coded status badge for fund manager pick."""
    colors = {
        "STRONG BUY": ("#00e676", "#1b5e20"),
        "BUY":        ("#64dd17", "#33691e"),
        "HOLD":       ("#ffab00", "#4e3a00"),
        "WATCH":      ("#ff9100", "#4e2600"),
    }
    fg, bg = colors.get(status, ("#aaa", "#333"))
    return f'<span class="badge" style="background:{bg};color:{fg};border:1px solid {fg}">{escape(status)}</span>'


def _fund_manager_picks_html(df) -> str:
    """Build the Fund Manager Picks tab content."""
    # Only consider GEM, STRONG, ACCEPTABLE stocks
    qualified = df[df["verdict"].isin(["GEM", "STRONG", "ACCEPTABLE"])].copy()

    # Collect all picks: (stock_row, manager_info, reasons, status)
    all_picks = []
    for i in range(len(qualified)):
        row = qualified.iloc[i]
        matches = _match_fund_managers(row)
        for m in matches:
            mgr = FUND_MANAGERS[m["manager_idx"]]
            all_picks.append({
                "ticker": row.get("ticker", ""),
                "name": row.get("name", ""),
                "sector": row.get("sector", ""),
                "score": row.get("total_score", 0),
                "verdict": row.get("verdict", ""),
                "manager": mgr["name"],
                "firm": mgr["firm"],
                "strategy": mgr["strategy"],
                "reasons": "; ".join(m["reasons"]),
                "status": m["status"],
            })

    if not all_picks:
        return '<p class="meta">No stocks matched fund manager criteria in this run.</p>'

    lines = []

    # ── Section 1: Manager philosophy cards ──
    lines.append('<h3>Fund Manager Strategies</h3>')
    lines.append('<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;">')
    for mgr in FUND_MANAGERS:
        lines.append('<div class="filter-ref">')
        lines.append(f'<h4>{escape(mgr["name"])} <span style="color:var(--text2);font-weight:400">— {escape(mgr["firm"])}</span></h4>')
        lines.append(f'<p><strong>{escape(mgr["strategy"])}</strong></p>')
        lines.append(f'<p>{escape(mgr["philosophy"])}</p>')
        lines.append('</div>')
    lines.append('</div>')

    # ── Section 2: Summary by manager ──
    lines.append('<h3>Picks by Manager</h3>')

    # Group picks by manager
    from collections import defaultdict
    by_manager: dict[str, list] = defaultdict(list)
    for p in all_picks:
        by_manager[p["manager"]].append(p)

    # Sort by status priority within each manager
    status_order = {"STRONG BUY": 0, "BUY": 1, "HOLD": 2, "WATCH": 3}

    for mgr in FUND_MANAGERS:
        mgr_name = mgr["name"]
        mgr_picks = by_manager.get(mgr_name, [])
        mgr_picks.sort(key=lambda p: (status_order.get(p["status"], 9), -p["score"]))
        count = len(mgr_picks)
        strong_buys = sum(1 for p in mgr_picks if p["status"] == "STRONG BUY")
        buys = sum(1 for p in mgr_picks if p["status"] == "BUY")

        lines.append(f'<h3 style="margin-top:20px">{escape(mgr_name)} '
                     f'<span style="color:var(--text2);font-weight:400">'
                     f'— {escape(mgr["strategy"])} ({count} picks'
                     f'{f", {strong_buys} STRONG BUY" if strong_buys else ""}'
                     f'{f", {buys} BUY" if buys else ""})</span></h3>')

        if not mgr_picks:
            lines.append('<p class="meta">No qualifying stocks match this strategy in the current screening.</p>')
            continue

        table_id = f'fm_{mgr_name.replace(" ", "_").lower()}'
        lines.append(f'<table id="{table_id}">')
        lines.append('<thead><tr>')
        fm_cols = [("Ticker", False), ("Name", False), ("Sector", False),
                   ("Score", True), ("Verdict", False), ("Status", False), ("Reasoning", False)]
        for ci, (label, numeric) in enumerate(fm_cols):
            sort_call = f' onclick="sortTable(\'{table_id}\',{ci},{str(numeric).lower()},event)" style="cursor:pointer"'
            lines.append(f'<th{sort_call}>{label}</th>')
        lines.append('</tr></thead><tbody>')

        for p in mgr_picks:
            t_score = p["score"]
            lines.append('<tr>')
            lines.append(f'<td><a href="#{escape(p["ticker"])}">{escape(p["ticker"])}</a></td>')
            lines.append(f'<td>{escape(p["name"])}</td>')
            lines.append(f'<td>{escape(p["sector"])}</td>')
            lines.append(f'<td data-val="{t_score}" style="color:{_score_color(t_score, 100)};font-weight:700">{t_score:.1f}</td>')
            lines.append(f'<td>{_verdict_badge(p["verdict"])}</td>')
            lines.append(f'<td>{_status_badge(p["status"])}</td>')
            lines.append(f'<td style="font-size:0.8rem;color:var(--text2)">{escape(p["reasons"])}</td>')
            lines.append('</tr>')

        lines.append('</tbody></table>')

    # ── Section 3: Master table (all picks, all managers) ──
    lines.append('<h3 style="margin-top:24px">All Picks — Consolidated View</h3>')
    lines.append('<p class="meta">Stocks endorsed by multiple managers have stronger conviction. Sort by any column.</p>')

    # Count how many managers picked each stock
    from collections import Counter
    ticker_mgr_count = Counter(p["ticker"] for p in all_picks)

    # Sort: most managers first, then by score
    all_picks_sorted = sorted(all_picks, key=lambda p: (-ticker_mgr_count[p["ticker"]], -p["score"], status_order.get(p["status"], 9)))

    lines.append('<table id="fm_all">')
    lines.append('<thead><tr>')
    all_cols = [("Stock", False), ("Sector", False), ("Score", True), ("Verdict", False),
                ("Manager", False), ("Strategy", False), ("Status", False),
                ("Reasoning", False), ("Mgr Count", True)]
    for ci, (label, numeric) in enumerate(all_cols):
        sort_call = f' onclick="sortTable(\'fm_all\',{ci},{str(numeric).lower()},event)" style="cursor:pointer"'
        lines.append(f'<th{sort_call}>{label}</th>')
    lines.append('</tr></thead><tbody>')

    for p in all_picks_sorted:
        t_score = p["score"]
        mc = ticker_mgr_count[p["ticker"]]
        mc_color = "var(--green)" if mc >= 5 else "var(--accent)" if mc >= 3 else "var(--text2)"
        lines.append('<tr>')
        lines.append(f'<td><a href="#{escape(p["ticker"])}">{escape(p["ticker"])}</a><br><span style="font-size:0.75rem;color:var(--text2)">{escape(p["name"])}</span></td>')
        lines.append(f'<td>{escape(p["sector"])}</td>')
        lines.append(f'<td data-val="{t_score}" style="color:{_score_color(t_score, 100)};font-weight:700">{t_score:.1f}</td>')
        lines.append(f'<td>{_verdict_badge(p["verdict"])}</td>')
        lines.append(f'<td style="font-weight:600">{escape(p["manager"])}</td>')
        lines.append(f'<td style="font-size:0.8rem">{escape(p["strategy"])}</td>')
        lines.append(f'<td>{_status_badge(p["status"])}</td>')
        lines.append(f'<td style="font-size:0.78rem;color:var(--text2)">{escape(p["reasons"])}</td>')
        lines.append(f'<td data-val="{mc}" style="text-align:center;font-weight:700;color:{mc_color}">{mc}</td>')
        lines.append('</tr>')

    lines.append('</tbody></table>')

    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Stock card builder
# ═══════════════════════════════════════════════

def _stock_card_html(row) -> str:
    """Build a detailed card for one stock."""
    ticker = row.get("ticker", "?")
    name = escape(str(row.get("name", ticker)))
    sector = escape(str(row.get("sector", "")))
    verdict = row.get("verdict", "REJECT")
    total = row.get("total_score", 0)
    price = row.get("price", None)

    lines = []
    lines.append('<div class="stock-card">')

    # Header
    lines.append('<div class="stock-header">')
    lines.append(f'<div><span class="stock-title">{name}</span>'
                 f' <span class="stock-subtitle">({escape(ticker)}) &bull; {sector}</span></div>')
    badge = _verdict_badge(verdict)
    score_color = _score_color(total, 100)
    coffee = '<span class="coffee-can">&#9749; Coffee Can</span>' if row.get("coffee_can") else ""
    lines.append(f'<div>{badge} <span style="font-size:1.3rem;font-weight:700;color:{score_color}">{_fmt(total, ".1f")}/100</span>{coffee}</div>')
    lines.append('</div>')

    # Dimension bars
    lines.append('<div class="dim-grid">')
    for col, label in DIMENSION_NAMES:
        val = row.get(col, 0)
        lines.append(f'<div class="dim-row"><span class="dim-name">{label}</span>{_bar_html(val)}</div>')
    lines.append('</div>')

    # Key metrics
    lines.append('<div class="metrics-grid">')

    metrics = [
        ("Price", _fmt(price, ",.1f", prefix="&#8377;")),
        ("Market Cap", _fmt_cr(row.get("market_cap_cr"))),
        ("PE", _fmt(row.get("pe"))),
        ("PB", _fmt(row.get("pb"), ".2f")),
        ("PEG", _fmt(row.get("peg"), ".2f")),
        ("EV/EBITDA", _fmt(row.get("ev_ebitda"))),
        ("P/S", _fmt(row.get("ps_ratio"), ".2f")),
        ("Div Yield", _pct(row.get("dividend_yield"))),

        ("ROE", _pct(row.get("roe_pct"))),
        ("ROCE", _pct(row.get("roce_pct"))),
        ("ROA", _pct(row.get("roa_pct"))),
        ("Op. Margin", _pct(row.get("operating_margin_pct"))),
        ("Net Margin", _pct(row.get("net_margin_pct"))),
        ("Owner Earn. Yield", _pct(row.get("owner_earnings_yield_pct"))),

        ("Rev CAGR 3Y", _pct(row.get("revenue_cagr_3y"))),
        ("Profit CAGR 3Y", _pct(row.get("profit_cagr_3y"))),
        ("Incr. ROCE", _pct(row.get("incremental_roce"))),
        ("EPS Growth YoY", _pct(row.get("eps_growth_yoy"))),

        ("D/E", _fmt(row.get("debt_to_equity"), ".2f")),
        ("Current Ratio", _fmt(row.get("current_ratio"), ".2f")),
        ("Int. Coverage", _fmt(row.get("interest_coverage"), ".1f", suffix="x")),
        ("Altman Z", _fmt(row.get("altman_z"), ".2f")),

        ("FCF Yield", _pct(row.get("fcf_yield_pct"))),
        ("FCF Conversion", _fmt(row.get("fcf_conversion"), ".2f")),
        ("OCF/NI", _fmt(row.get("ocf_ni_ratio"), ".2f")),
        ("CapEx Intensity", _pct(row.get("capex_intensity", None), na="—") if row.get("capex_intensity") is None or (isinstance(row.get("capex_intensity"), float) and math.isnan(row.get("capex_intensity"))) else _fmt(row.get("capex_intensity") * 100, ".1f", suffix="%")),

        ("Piotroski F", _fmt(row.get("piotroski_score"), ".0f", suffix="/9")),
        ("Accrual Ratio", _fmt(row.get("accrual_ratio"), ".3f")),

        ("Inst. Holding", _pct(row.get("institutional_holding_pct"))),
        ("Insider Holding", _pct(row.get("insider_holding_pct"))),
        ("Analyst Target", _fmt(row.get("analyst_target_price"), ",.1f", prefix="&#8377;")),
        ("Analyst Rec", escape(str(row.get("analyst_recommendation", "—")).replace("_", " ").title())),
    ]

    for label, val_str in metrics:
        lines.append(f'<div class="metric"><span class="k">{label}</span><span class="v">{val_str}</span></div>')
    lines.append('</div>')

    # Intrinsic value section
    graham = row.get("graham_number")
    dcf_iv = row.get("dcf_intrinsic")
    mos_g = row.get("margin_of_safety_pct")
    mos_d = row.get("dcf_margin_of_safety_pct")
    rdcf = row.get("reverse_dcf_implied_growth")
    mf_rank = row.get("magic_formula_rank")

    lines.append('<div class="metrics-grid">')
    lines.append(f'<div class="metric"><span class="k">Graham Number</span><span class="v">{_fmt(graham, ",.1f", prefix="&#8377;")}</span></div>')
    lines.append(f'<div class="metric"><span class="k">Graham MoS</span><span class="v" style="color:{"var(--green)" if mos_g and not math.isnan(mos_g) and mos_g > 0 else "var(--red)" if mos_g and not math.isnan(mos_g) else "var(--text2)"}">{_pct(mos_g)}</span></div>')
    lines.append(f'<div class="metric"><span class="k">DCF Intrinsic</span><span class="v">{_fmt(dcf_iv, ",.1f", prefix="&#8377;")}</span></div>')
    lines.append(f'<div class="metric"><span class="k">DCF MoS</span><span class="v" style="color:{"var(--green)" if mos_d and not math.isnan(mos_d) and mos_d > 0 else "var(--red)" if mos_d and not math.isnan(mos_d) else "var(--text2)"}">{_pct(mos_d)}</span></div>')
    lines.append(f'<div class="metric"><span class="k">Reverse DCF Growth</span><span class="v">{_pct(rdcf)}</span></div>')
    lines.append(f'<div class="metric"><span class="k">Magic Formula Rank</span><span class="v">#{_fmt(mf_rank, ".0f", na="—")}</span></div>')
    lines.append('</div>')

    # Moat section
    moat_rating = row.get("moat", "None")
    moat_types_str = str(row.get("moat_types", ""))
    trend = str(row.get("moat_trend", "stable"))
    trend_icon, trend_color = MOAT_TREND_ICONS.get(trend, ("?", "#555"))

    lines.append(f'<div style="margin-top:6px;font-size:0.85rem;">')
    lines.append(f'<strong>Moat:</strong> {moat_rating} ')
    lines.append(f'<span style="color:{trend_color}">{trend_icon} {trend}</span> ')
    if moat_types_str and moat_types_str != "None identified":
        for mt in moat_types_str.split(", "):
            lines.append(f'<span class="moat-tag">{escape(mt.replace("_", " "))}</span>')
    lines.append('</div>')

    # Red flags
    flags_str = str(row.get("red_flags", ""))
    if flags_str:
        flags_list = [f for f in flags_str.split("; ") if f.strip()]
        if flags_list:
            lines.append('<div class="flags"><strong>Red Flags:</strong> ')
            for f in flags_list:
                lines.append(f'<span class="flag-item">{escape(f)}</span>')
            lines.append('</div>')

    lines.append('</div>')  # close stock-card
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Rankings table builder
# ═══════════════════════════════════════════════

def _rankings_table_html(df, table_id="rankings") -> str:
    """Sortable rankings table across all stocks."""
    lines = []
    lines.append(f'<table id="{table_id}">')
    lines.append('<thead><tr>')

    cols = [
        ("#", True), ("Ticker", False), ("Name", False), ("Sector", False),
        ("Score", True), ("Verdict", False),
        ("PE", True), ("ROCE%", True), ("D/E", True), ("Rev CAGR%", True),
        ("Piotroski", True), ("Altman Z", True), ("FCF Conv", True),
        ("Moat", False), ("MF Rank", True), ("Coffee", True),
    ]

    for i, (label, numeric) in enumerate(cols):
        sort_call = f' onclick="sortTable(\'{table_id}\',{i},{str(numeric).lower()},event)" style="cursor:pointer" title="Click to sort, Shift+Click to multi-sort"'
        lines.append(f'<th{sort_call}>{label}</th>')
    lines.append('</tr></thead><tbody>')

    def _dv(val, fallback=0):
        """Safe data-val: replace nan/inf/None with fallback."""
        if val is None:
            return fallback
        try:
            if math.isnan(val) or math.isinf(val):
                return fallback
        except TypeError:
            pass
        return val

    for rank in range(len(df)):
        row = df.iloc[rank]
        verdict = row.get("verdict", "REJECT")
        fg, _ = VERDICT_COLORS.get(verdict, ("#aaa", "#333"))
        total = row.get("total_score", 0)
        is_coffee = bool(row.get("coffee_can"))

        lines.append('<tr>')
        lines.append(f'<td data-val="{rank + 1}">{rank + 1}</td>')
        lines.append(f'<td><a href="#{escape(str(row.get("ticker", "")))}">{escape(str(row.get("ticker", "")))}</a></td>')
        lines.append(f'<td>{escape(str(row.get("name", "")))}</td>')
        lines.append(f'<td>{escape(str(row.get("sector", "")))}</td>')
        lines.append(f'<td data-val="{_dv(total)}" style="font-weight:700;color:{_score_color(total, 100)}">{_fmt(total, ".1f")}</td>')
        lines.append(f'<td>{_verdict_badge(verdict)}</td>')
        lines.append(f'<td data-val="{_dv(row.get("pe"), 9999)}">{_fmt(row.get("pe"))}</td>')
        lines.append(f'<td data-val="{_dv(row.get("roce_pct"), -999)}">{_pct(row.get("roce_pct"))}</td>')
        lines.append(f'<td data-val="{_dv(row.get("debt_to_equity"), 999)}">{_fmt(row.get("debt_to_equity"), ".2f")}</td>')
        lines.append(f'<td data-val="{_dv(row.get("revenue_cagr_3y"), -999)}">{_pct(row.get("revenue_cagr_3y"))}</td>')
        lines.append(f'<td data-val="{_dv(row.get("piotroski_score"), 0)}">{_fmt(row.get("piotroski_score"), ".0f")}/9</td>')
        lines.append(f'<td data-val="{_dv(row.get("altman_z"), -999)}">{_fmt(row.get("altman_z"), ".2f")}</td>')
        lines.append(f'<td data-val="{_dv(row.get("fcf_conversion"), -999)}">{_fmt(row.get("fcf_conversion"), ".2f")}</td>')
        lines.append(f'<td>{escape(str(row.get("moat", "None")))}</td>')
        lines.append(f'<td data-val="{_dv(row.get("magic_formula_rank"), 9999)}">{_fmt(row.get("magic_formula_rank"), ".0f")}</td>')
        lines.append(f'<td data-val="{1 if is_coffee else 0}">{"&#9749;" if is_coffee else ""}</td>')
        lines.append('</tr>')

    lines.append('</tbody></table>')
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Filter reference panel
# ═══════════════════════════════════════════════

def _filter_reference_html() -> str:
    """Render the FILTER_REFERENCE config as an HTML panel."""
    lines = ['<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:12px;">']

    for fid, fdef in sorted(FILTER_REFERENCE.items()):
        pts = fdef["max_points"]
        pts_str = f"{pts}/10" if pts > 0 else "Binary Reject"
        lines.append('<div class="filter-ref">')
        lines.append(f'<h4>Filter {fid}: {escape(fdef["name"])} ({pts_str})</h4>')
        lines.append(f'<p>{escape(fdef["description"])}</p>')
        lines.append(f'<span class="filter-src">Sources: {escape(fdef["source"])}</span>')
        lines.append('<ul>')
        for sc in fdef["sub_components"]:
            lines.append(f'<li>{escape(sc)}</li>')
        lines.append('</ul></div>')

    lines.append('</div>')
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Dashboard stats
# ═══════════════════════════════════════════════

def _dashboard_html(df) -> str:
    """Top-level stats cards."""
    total = len(df)
    sectors = df["sector"].nunique() if "sector" in df.columns else 0
    avg_score = df["total_score"].mean() if "total_score" in df.columns else 0
    median_score = df["total_score"].median() if "total_score" in df.columns else 0

    gems = len(df[df["verdict"] == "GEM"])
    strong = len(df[df["verdict"] == "STRONG"])
    acceptable = len(df[df["verdict"] == "ACCEPTABLE"])
    watchlist = len(df[df["verdict"] == "WATCHLIST"])
    rejected = len(df[df["verdict"] == "REJECT"])

    coffee = df["coffee_can"].sum() if "coffee_can" in df.columns else 0
    avg_piotroski = df["piotroski_score"].mean() if "piotroski_score" in df.columns else 0

    lines = ['<div class="grid grid-5">']
    cards = [
        (str(total), "Stocks Screened"),
        (str(sectors), "Sectors"),
        (f"{avg_score:.1f}", "Avg Score /100"),
        (f"{median_score:.1f}", "Median Score"),
        (f"{avg_piotroski:.1f}/9", "Avg Piotroski"),
    ]
    for num, label in cards:
        lines.append(f'<div class="stat-card"><div class="num">{num}</div><div class="label">{label}</div></div>')
    lines.append('</div>')

    # Verdict chips
    lines.append('<div class="verdict-row">')
    for v, count in [("GEM", gems), ("STRONG", strong), ("ACCEPTABLE", acceptable), ("WATCHLIST", watchlist), ("REJECT", rejected)]:
        fg, bg = VERDICT_COLORS[v]
        lines.append(f'<div class="verdict-chip" style="background:{bg};color:{fg};border:1px solid {fg}">{v}: {count}</div>')
    if coffee:
        lines.append(f'<div class="verdict-chip" style="background:#1b3a1b;color:#00e676;border:1px solid #00e676">&#9749; Coffee Can: {int(coffee)}</div>')
    lines.append('</div>')

    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Sector summary table
# ═══════════════════════════════════════════════

def _sector_summary_html(df) -> str:
    """Table showing per-sector aggregates."""
    lines = ['<table><thead><tr>']
    lines.append('<th>Sector</th><th>Stocks</th><th>Avg Score</th><th>Best</th><th>GEM</th><th>STRONG</th><th>Avg ROCE%</th><th>Avg Piotroski</th>')
    lines.append('</tr></thead><tbody>')

    for sector, grp in df.groupby("sector"):
        n = len(grp)
        avg = grp["total_score"].mean()
        best_row = grp.loc[grp["total_score"].idxmax()]
        best_name = best_row.get("name", best_row.get("ticker", ""))
        best_score = best_row["total_score"]
        gems = (grp["verdict"] == "GEM").sum()
        strongs = (grp["verdict"] == "STRONG").sum()
        avg_roce = grp["roce_pct"].mean()
        avg_f = grp["piotroski_score"].mean()

        lines.append('<tr>')
        lines.append(f'<td><strong>{escape(str(sector))}</strong></td>')
        lines.append(f'<td>{n}</td>')
        lines.append(f'<td style="color:{_score_color(avg, 100)}">{avg:.1f}</td>')
        lines.append(f'<td>{escape(str(best_name)[:20])} ({best_score:.1f})</td>')
        lines.append(f'<td>{"&#x2B50; " + str(gems) if gems else "0"}</td>')
        lines.append(f'<td>{strongs}</td>')
        lines.append(f'<td>{_pct(avg_roce)}</td>')
        lines.append(f'<td>{avg_f:.1f}/9</td>')
        lines.append('</tr>')

    lines.append('</tbody></table>')
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Top picks section
# ═══════════════════════════════════════════════

def _top_picks_html(df) -> str:
    """Section with detailed cards for top-rated stocks."""
    top = df[df["verdict"].isin(["GEM", "STRONG"])].head(15)
    if top.empty:
        top = df.head(5)

    lines = []
    for i in range(len(top)):
        lines.append(_stock_card_html(top.iloc[i]))
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Build main report
# ═══════════════════════════════════════════════

def build_report(df: pd.DataFrame, output_path: str | None = None) -> str:
    """
    Generate the full HTML report from screened DataFrame.
    Returns the path to the main report file.
    """
    if df.empty:
        print("No data to generate report.")
        return ""

    df = df.sort_values("total_score", ascending=False).reset_index(drop=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = output_path or MAIN_REPORT

    sectors = sorted(df["sector"].unique())

    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NSE Stock Screener &mdash; 100-Point Report</title>
{_css()}
</head>
<body>
<div class="container">

<h1>NSE Stock Screener &mdash; 100-Point System</h1>
<p class="meta">Generated: {now} &bull; 10 Filters &bull; Buffett &middot; Piotroski &middot; Greenblatt &middot; Dorsey &middot; Altman &middot; Damodaran</p>
""")

    # Tab bar
    html_parts.append("""
<div class="tab-bar">
    <div class="tab active" data-tab="tab-dashboard" onclick="showTab('tab-dashboard')">Dashboard</div>
    <div class="tab" data-tab="tab-rankings" onclick="showTab('tab-rankings')">Rankings</div>
    <div class="tab" data-tab="tab-picks" onclick="showTab('tab-picks')">Top Picks</div>
    <div class="tab" data-tab="tab-managers" onclick="showTab('tab-managers')">Fund Managers</div>
    <div class="tab" data-tab="tab-sectors" onclick="showTab('tab-sectors')">By Sector</div>
    <div class="tab" data-tab="tab-allstocks" onclick="showTab('tab-allstocks')">All Stocks</div>
    <div class="tab" data-tab="tab-framework" onclick="showTab('tab-framework')">Framework</div>
</div>
""")

    # ── Tab 1: Dashboard ──
    html_parts.append('<div id="tab-dashboard" class="tab-panel active">')
    html_parts.append('<h2>Dashboard</h2>')
    html_parts.append(_dashboard_html(df))
    html_parts.append('<h3>Sector Overview</h3>')
    html_parts.append(_sector_summary_html(df))
    html_parts.append('</div>')

    # ── Tab 2: Rankings ──
    html_parts.append('<div id="tab-rankings" class="tab-panel">')
    html_parts.append('<h2>Full Rankings (sortable)</h2>')
    html_parts.append('<p class="meta">Click column headers to sort.</p>')
    html_parts.append(_rankings_table_html(df))
    html_parts.append('</div>')

    # ── Tab 3: Top Picks ──
    html_parts.append('<div id="tab-picks" class="tab-panel">')
    html_parts.append('<h2>Top Picks &mdash; GEM &amp; STRONG</h2>')
    html_parts.append(_top_picks_html(df))
    html_parts.append('</div>')

    # ── Tab 4: Fund Managers ──
    html_parts.append('<div id="tab-managers" class="tab-panel">')
    html_parts.append('<h2>Fund Manager Picks &mdash; Qualitative Overlay</h2>')
    html_parts.append('<p class="meta">Top 10 Indian fund managers\' strategies applied to GEM, STRONG &amp; ACCEPTABLE stocks. '
                     'This is a qualitative lens over the quantitative screener &mdash; stocks endorsed by multiple managers carry higher conviction.</p>')
    html_parts.append(_fund_manager_picks_html(df))
    html_parts.append('</div>')

    # ── Tab 5: By Sector ──
    html_parts.append('<div id="tab-sectors" class="tab-panel">')
    html_parts.append('<h2>Sector Breakdown</h2>')

    for sector in sectors:
        sec_df = df[df["sector"] == sector].sort_values("total_score", ascending=False)
        n = len(sec_df)
        avg = sec_df["total_score"].mean()
        html_parts.append(f'<h3>{escape(sector)} ({n} stocks, avg {avg:.1f}/100)</h3>')

        # Mini rankings table for sector
        html_parts.append(f'<table><thead><tr>'
                          f'<th>#</th><th>Ticker</th><th>Score</th><th>Verdict</th>'
                          f'<th>PE</th><th>ROCE%</th><th>D/E</th><th>Piotroski</th><th>Moat</th>'
                          f'</tr></thead><tbody>')

        for rank in range(len(sec_df)):
            row = sec_df.iloc[rank]
            verdict = row.get("verdict", "REJECT")
            total = row.get("total_score", 0)
            html_parts.append(f'<tr>'
                              f'<td>{rank + 1}</td>'
                              f'<td><a href="#{escape(str(row.get("ticker", "")))}">{escape(str(row.get("ticker", "")))}</a></td>'
                              f'<td style="color:{_score_color(total, 100)};font-weight:700">{total:.1f}</td>'
                              f'<td>{_verdict_badge(verdict)}</td>'
                              f'<td>{_fmt(row.get("pe"))}</td>'
                              f'<td>{_pct(row.get("roce_pct"))}</td>'
                              f'<td>{_fmt(row.get("debt_to_equity"), ".2f")}</td>'
                              f'<td>{_fmt(row.get("piotroski_score"), ".0f")}/9</td>'
                              f'<td>{escape(str(row.get("moat", "None")))}</td>'
                              f'</tr>')

        html_parts.append('</tbody></table>')

    html_parts.append('</div>')

    # ── Tab 6: All Stocks (detailed cards) ──
    html_parts.append('<div id="tab-allstocks" class="tab-panel">')
    html_parts.append('<h2>All Stocks &mdash; Detailed Analysis</h2>')
    for i in range(len(df)):
        row = df.iloc[i]
        ticker = str(row.get("ticker", ""))
        html_parts.append(f'<div id="{escape(ticker)}">')
        html_parts.append(_stock_card_html(row))
        html_parts.append('</div>')
    html_parts.append('</div>')

    # ── Tab 7: Framework ──
    html_parts.append('<div id="tab-framework" class="tab-panel">')
    html_parts.append('<h2>Scoring Framework &mdash; 10 Filters + Red Flags</h2>')
    html_parts.append('<p class="meta">100-point system: 10 dimensions &times; 10 points each. Filter 11 is a binary reject gate.</p>')

    # Verdict definitions
    html_parts.append('<h3>Verdict Thresholds</h3>')
    html_parts.append('<div class="verdict-row">')
    for v, vdef in VERDICTS.items():
        fg, bg = VERDICT_COLORS[v]
        html_parts.append(f'<div class="verdict-chip" style="background:{bg};color:{fg};border:1px solid {fg}">{v} &ge; {vdef["min"]}</div>')
    html_parts.append('</div>')

    html_parts.append('<h3>Filter Definitions</h3>')
    html_parts.append(_filter_reference_html())

    # Coffee Can criteria
    html_parts.append('<h3>Coffee Can Criteria (Saurabh Mukherjea)</h3>')
    html_parts.append('<div class="filter-ref">')
    html_parts.append('<p>Buy and hold for 10 years. Eligible if: Revenue CAGR &ge; 10%, ROCE &ge; 15%, D/E &le; 1.0.</p>')
    html_parts.append('</div>')

    # Magic Formula
    html_parts.append('<h3>Magic Formula Cross-Check (Joel Greenblatt)</h3>')
    html_parts.append('<div class="filter-ref">')
    html_parts.append('<p>Combined rank of Earnings Yield (EBIT/EV) and ROIC (ROCE proxy). Lower rank = better value + quality combo. Used as a sanity check, not a scoring input.</p>')
    html_parts.append('</div>')

    html_parts.append('</div>')

    # Close
    html_parts.append(f"""
</div><!-- container -->
{_js()}
</body>
</html>""")

    html = "\n".join(html_parts)

    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nHTML report saved: {out}")
    print(f"  {len(df)} stocks across {df['sector'].nunique()} sectors")
    return out


# ═══════════════════════════════════════════════
# Standalone mode (re-read from DataFrame pickle or re-run)
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    print("Report generator — run screener.py first to generate data, then this will be called automatically.")
    print("Or use: python screener.py")
