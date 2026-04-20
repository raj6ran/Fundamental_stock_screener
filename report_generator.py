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

/* Collapsible framework sections */
.fw-section { margin:16px 0; }
.fw-section-header { display:flex; align-items:center; gap:8px; cursor:pointer; padding:10px 14px; background:var(--surface); border:1px solid var(--border); border-radius:8px; transition:all 0.2s; user-select:none; }
.fw-section-header:hover { border-color:var(--accent); background:#1c2128; }
.fw-section-header.open { border-radius:8px 8px 0 0; border-bottom-color:transparent; }
.fw-section-header.open + .fw-section-body { border:1px solid var(--border); border-top:none; border-radius:0 0 8px 8px; padding:16px; }
.fw-section-body { padding:0 16px; }
.fw-chevron { font-size:0.7rem; color:var(--accent); width:14px; text-align:center; transition:transform 0.2s; }

/* Framework pills (consensus table) */
.fw-pills { display:flex; flex-wrap:wrap; gap:4px; }
.fw-pill { display:inline-block; padding:2px 8px; border-radius:4px; font-size:0.72rem; font-weight:600; letter-spacing:0.3px; white-space:nowrap; }
.fw-pill-pass { background:#1b3a1b; border:1px solid var(--green); color:var(--green); }
.fw-pill-partial { background:#2a2600; border:1px solid var(--amber); color:var(--amber); }

/* Filter bar */
.fw-filters { display:flex; flex-wrap:wrap; gap:12px; align-items:center; margin:12px 0 16px; padding:12px 16px; background:var(--surface); border:1px solid var(--border); border-radius:8px; }
.fw-filters label { display:flex; align-items:center; gap:6px; color:var(--text2); font-size:0.82rem; font-weight:600; }
.fw-filters select { background:#0d1117; color:var(--text); border:1px solid var(--border); border-radius:4px; padding:4px 8px; font-size:0.82rem; cursor:pointer; min-width:100px; }
.fw-filters select:hover { border-color:var(--accent); }
.fw-filters select:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 1px var(--accent); }
.fw-reset-btn { background:transparent; color:var(--accent); border:1px solid var(--accent); border-radius:4px; padding:4px 12px; font-size:0.82rem; cursor:pointer; transition:all 0.2s; }
.fw-reset-btn:hover { background:var(--accent); color:var(--bg); }
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

function toggleSection(header) {
    var body = header.nextElementSibling;
    var chevron = header.querySelector('.fw-chevron');
    if (body.style.display === 'none') {
        body.style.display = 'block';
        header.classList.add('open');
        chevron.innerHTML = '&#9660;';
    } else {
        body.style.display = 'none';
        header.classList.remove('open');
        chevron.innerHTML = '&#9654;';
    }
}

function filterConsensus() {
    var verdict = document.getElementById('flt_verdict').value;
    var fwMin = parseInt(document.getElementById('flt_fwcount').value) || 0;
    var sector = document.getElementById('flt_sector').value;
    var framework = document.getElementById('flt_framework').value;
    var table = document.getElementById('fw_consensus');
    if (!table) return;
    var rows = table.querySelectorAll('tbody tr');
    for (var i = 0; i < rows.length; i++) {
        var r = rows[i];
        var show = true;
        if (verdict && r.getAttribute('data-verdict') !== verdict) show = false;
        if (fwMin > 0 && parseInt(r.getAttribute('data-fwcount')) < fwMin) show = false;
        if (sector && r.getAttribute('data-sector') !== sector) show = false;
        if (framework) {
            var fws = r.getAttribute('data-fw') || '';
            if (fws.split('|').indexOf(framework) < 0) show = false;
        }
        r.style.display = show ? '' : 'none';
    }
}

function resetFilters() {
    document.getElementById('flt_verdict').value = '';
    document.getElementById('flt_fwcount').value = '0';
    document.getElementById('flt_sector').value = '';
    document.getElementById('flt_framework').value = '';
    filterConsensus();
}
</script>
"""


# ═══════════════════════════════════════════════
# Investment Frameworks — Published & Verifiable
# ═══════════════════════════════════════════════
# Every framework below has an auditable source:
# a published book, academic paper, or annual study.
# No speculative criteria. No internet commentary.

FRAMEWORKS = [
    {
        "name": "Graham Value",
        "author": "Benjamin Graham",
        "source": "The Intelligent Investor (1949), Security Analysis (1934)",
        "criteria": "PE < 15, PB < 1.5, PE×PB < 22.5, current ratio > 2, D/E < 0.5, positive earnings, margin of safety > 0. Pass ≥ 3/6 criteria",
        "verdict": "PASS/FAIL",
    },
    {
        "name": "Piotroski F-Score",
        "author": "Joseph Piotroski",
        "source": "Journal of Accounting Research (2000) — 'Value Investing: The Use of Historical Financial Statement Information'",
        "criteria": "9 binary tests: ROA > 0, ΔROA > 0, OCF > 0, OCF > NI, ΔLeverage < 0, ΔCurrent Ratio > 0, no dilution, ΔGross Margin > 0, ΔAsset Turnover > 0",
        "verdict": "STRONG (7-9) / MODERATE (4-6) / WEAK (0-3)",
    },
    {
        "name": "Altman Z-Score",
        "author": "Edward Altman",
        "source": "Journal of Finance (1968) — 'Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy'",
        "criteria": "Z = 1.2(WC/TA) + 1.4(RE/TA) + 3.3(EBIT/TA) + 0.6(MCap/TL) + Rev/TA",
        "verdict": "SAFE (>2.99) / GREY (1.81–2.99) / DISTRESS (<1.81)",
    },
    {
        "name": "Magic Formula",
        "author": "Joel Greenblatt",
        "source": "The Little Book That Beats the Market (2005)",
        "criteria": "Combined rank of Earnings Yield (EBIT/EV) + ROIC (EBIT/Capital Employed). Lower combined rank = better",
        "verdict": "TOP DECILE / TOP QUARTILE / BOTTOM",
    },
    {
        "name": "Coffee Can",
        "author": "Saurabh Mukherjea",
        "source": "Coffee Can Investing (2018, Penguin)",
        "criteria": "Revenue CAGR ≥ 10%, ROCE ≥ 15%, D/E ≤ 1.0. Hold 10 years, no churn",
        "verdict": "ELIGIBLE / NOT ELIGIBLE",
    },
    {
        "name": "QGLP",
        "author": "Raamdeo Agrawal",
        "source": "Motilal Oswal Wealth Creation Study (annual, 1996–present)",
        "criteria": "Quality: ROCE ≥ 15%, ROE ≥ 15%. Growth: earnings CAGR ≥ 15%. Longevity: durable moat, non-eroding. Price: PE ≤ 1.5× sector norm",
        "verdict": "Q✓ G✓ L✓ P✓ = PASS / else = FAIL subset",
    },
    {
        "name": "Lynch PEG",
        "author": "Peter Lynch",
        "source": "One Up on Wall Street (1989), Beating the Street (1993)",
        "criteria": "PEG < 1.0 ideal, < 1.5 acceptable. Revenue growing, low debt, positive cash flow",
        "verdict": "BARGAIN (PEG<1) / FAIR (1–1.5) / OVERPRICED (>1.5)",
    },
    {
        "name": "Buffett Moat",
        "author": "Warren Buffett",
        "source": "Berkshire Hathaway Annual Letters (1957–present)",
        "criteria": "Consistent ROE ≥ 15% (10yr), durable competitive advantage, owner earnings positive, low debt, high FCF conversion, competent capital allocation",
        "verdict": "FRANCHISE / GOOD BUSINESS / AVOID",
    },
    {
        "name": "Dorsey Moat",
        "author": "Pat Dorsey",
        "source": "The Little Book That Builds Wealth (2008) — Morningstar Director of Equity Research",
        "criteria": "5 moat sources: cost advantage, switching costs, network effects, intangible assets, efficient scale. ROIC > WACC consistently. Moat trend: widening/stable/eroding",
        "verdict": "WIDE / NARROW / NONE + trend direction",
    },
    {
        "name": "DCF Intrinsic Value",
        "author": "Aswath Damodaran",
        "source": "Investment Valuation (Wiley, multiple editions), NYU Stern published models",
        "criteria": "10yr DCF with company-specific CAGR, 12% discount rate, 3% terminal growth. Reverse DCF to check market-implied growth. Margin of Safety = (Intrinsic − Price) / Intrinsic",
        "verdict": "UNDERVALUED (MoS > 15%) / FAIR (±15%) / OVERVALUED (MoS < −15%)",
    },
]


def _match_frameworks(row) -> list[dict]:
    """Match a stock row against 10 published investment frameworks.
    Returns list of dicts with framework_idx, result, reasons, status."""
    picks = []
    score = row.get("total_score", 0)
    pe = row.get("pe")
    pb = row.get("pb")
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
    incr_roce = row.get("incremental_roce")
    altman_z = row.get("altman_z")
    current_ratio = row.get("current_ratio")
    magic_rank = row.get("magic_formula_rank")
    magic_pct = row.get("magic_formula_percentile")
    eps = row.get("eps")
    bvps = row.get("book_value")

    v = _is_valid_number
    pe_norm = SECTOR_PE_NORMS.get(sector, {}).get("avg", 25)

    # ── 0. Graham Value ──
    # Source: The Intelligent Investor, Ch. 14 — defensive investor criteria
    g_reasons = []
    g_pe = v(pe) and pe < 15
    g_pb = v(pb) and pb < 1.5
    g_pepb = v(pe) and v(pb) and pe * pb < 22.5
    g_de = v(de) and de < 0.5
    g_cr = v(current_ratio) and current_ratio > 2
    g_eps = v(eps) and eps > 0
    g_mos = v(mos_g) and mos_g > 0
    if g_pe:
        g_reasons.append(f"PE {pe:.1f} < 15")
    if g_pb:
        g_reasons.append(f"PB {pb:.2f} < 1.5")
    if g_pepb:
        g_reasons.append(f"PE×PB = {pe * pb:.1f} < 22.5")
    if g_de:
        g_reasons.append(f"D/E {de:.2f} < 0.5")
    if g_cr:
        g_reasons.append(f"Current ratio {current_ratio:.2f} > 2")
    if g_eps:
        g_reasons.append(f"EPS ₹{eps:.1f} positive")
    if g_mos:
        g_reasons.append(f"Graham MoS +{mos_g:.0f}%")
    if g_cr:
        g_reasons.append(f"Current ratio {current_ratio:.2f} > 2")
    passed = sum([g_pe, g_pb or g_pepb, g_de, g_cr, g_eps, g_mos])
    if passed >= 3:
        status = "PASS" if passed >= 5 else "PARTIAL"
        picks.append({"framework_idx": 0, "reasons": g_reasons, "status": status,
                       "result": f"{passed}/6 criteria met"})

    # ── 1. Piotroski F-Score ──
    # Source: Piotroski (2000), 9 binary tests
    if v(piotroski):
        p_reasons = [f"F-Score {piotroski:.0f}/9"]
        if v(ocf_ni) and ocf_ni > 1.0:
            p_reasons.append(f"OCF/NI {ocf_ni:.2f} — cash-backed")
        if v(roce) and v(incr_roce):
            if incr_roce > 0:
                p_reasons.append(f"Improving ROCE (Δ {incr_roce:.1f}%)")
        if piotroski >= 7:
            picks.append({"framework_idx": 1, "reasons": p_reasons, "status": "STRONG",
                           "result": f"F-Score {piotroski:.0f}/9 — Strong"})
        elif piotroski >= 4:
            picks.append({"framework_idx": 1, "reasons": p_reasons, "status": "MODERATE",
                           "result": f"F-Score {piotroski:.0f}/9 — Moderate"})

    # ── 2. Altman Z-Score ──
    # Source: Altman (1968), exact formula
    if v(altman_z):
        z_reasons = [f"Z-Score {altman_z:.2f}"]
        if altman_z > 2.99:
            z_reasons.append("Safe zone — low bankruptcy risk")
            picks.append({"framework_idx": 2, "reasons": z_reasons, "status": "SAFE",
                           "result": f"Z = {altman_z:.2f} — Safe"})
        elif altman_z > 1.81:
            z_reasons.append("Grey zone — moderate risk, monitor")
            picks.append({"framework_idx": 2, "reasons": z_reasons, "status": "GREY",
                           "result": f"Z = {altman_z:.2f} — Grey Zone"})
        # Distress stocks are flagged but not shown as "picks"

    # ── 3. Magic Formula ──
    # Source: Greenblatt (2005), combined rank of Earnings Yield + ROIC
    if v(magic_pct):
        mf_reasons = [f"Magic Formula percentile: {magic_pct:.0f}%"]
        if v(roce):
            mf_reasons.append(f"ROIC proxy (ROCE): {roce:.1f}%")
        if magic_pct >= 90:
            picks.append({"framework_idx": 3, "reasons": mf_reasons, "status": "TOP DECILE",
                           "result": f"Top {100 - magic_pct:.0f}% — Top Decile"})
        elif magic_pct >= 75:
            picks.append({"framework_idx": 3, "reasons": mf_reasons, "status": "TOP QUARTILE",
                           "result": f"Top {100 - magic_pct:.0f}% — Top Quartile"})

    # ── 4. Coffee Can ──
    # Source: Mukherjea (2018), exact criteria from book
    cc_reasons = []
    if v(rev_cagr):
        cc_reasons.append(f"Rev CAGR {rev_cagr:.1f}% {'≥' if rev_cagr >= 10 else '<'} 10%")
    if v(roce):
        cc_reasons.append(f"ROCE {roce:.1f}% {'≥' if roce >= 15 else '<'} 15%")
    if v(de):
        cc_reasons.append(f"D/E {de:.2f} {'≤' if de <= 1.0 else '>'} 1.0")
    if coffee_can:
        picks.append({"framework_idx": 4, "reasons": cc_reasons, "status": "ELIGIBLE",
                       "result": "All 3 criteria met — Coffee Can Eligible"})

    # ── 5. QGLP ──
    # Source: Motilal Oswal Wealth Creation Study (published annually)
    q_ok = v(roce) and roce >= 15 and v(roe) and roe >= 15
    g_ok = (v(rev_cagr) and rev_cagr >= 15) or (v(profit_cagr) and profit_cagr >= 15)
    l_ok = moat in ("Wide", "Narrow") and moat_trend != "eroding"
    p_ok = v(pe) and pe <= pe_norm * 1.5
    qglp_reasons = []
    qglp_flags = []
    if q_ok:
        qglp_reasons.append(f"Q✓ ROCE {roce:.1f}%, ROE {roe:.1f}%")
        qglp_flags.append("Q")
    if g_ok:
        gval = rev_cagr if v(rev_cagr) and rev_cagr >= 15 else profit_cagr
        qglp_reasons.append(f"G✓ CAGR {gval:.1f}%")
        qglp_flags.append("G")
    if l_ok:
        qglp_reasons.append(f"L✓ {moat} moat, {moat_trend}")
        qglp_flags.append("L")
    if p_ok:
        qglp_reasons.append(f"P✓ PE {pe:.1f} ≤ {pe_norm * 1.5:.0f}")
        qglp_flags.append("P")
    if len(qglp_flags) >= 3:
        tag = "".join(qglp_flags)
        status = "PASS" if len(qglp_flags) == 4 else "PARTIAL"
        picks.append({"framework_idx": 5, "reasons": qglp_reasons, "status": status,
                       "result": f"{tag} ({len(qglp_flags)}/4)"})

    # ── 6. Lynch PEG ──
    # Source: One Up on Wall Street (1989), Beating the Street (1993)
    if v(peg) and peg > 0:
        lynch_reasons = [f"PEG {peg:.2f}"]
        if v(rev_cagr):
            lynch_reasons.append(f"Rev CAGR {rev_cagr:.1f}%")
        if v(de) and de < 1.0:
            lynch_reasons.append(f"D/E {de:.2f} — low debt")
        if v(fcf_conv) and fcf_conv > 0.5:
            lynch_reasons.append(f"FCF conversion {fcf_conv:.2f}")
        if peg < 1.0:
            picks.append({"framework_idx": 6, "reasons": lynch_reasons, "status": "BARGAIN",
                           "result": f"PEG {peg:.2f} < 1.0 — Bargain"})
        elif peg < 1.5:
            picks.append({"framework_idx": 6, "reasons": lynch_reasons, "status": "FAIR",
                           "result": f"PEG {peg:.2f} < 1.5 — Fair Value"})

    # ── 7. Buffett Moat ──
    # Source: Berkshire Hathaway Annual Letters — consistent ROE, moat, owner earnings
    buff_reasons = []
    b_roe = v(roe) and roe >= 15
    b_moat = moat in ("Wide", "Narrow") and moat_trend != "eroding"
    b_de = v(de) and de < 1.0
    b_fcf = v(fcf_conv) and fcf_conv > 0.8
    b_ocf = v(ocf_ni) and ocf_ni > 0.8
    if b_roe:
        buff_reasons.append(f"ROE {roe:.1f}% ≥ 15% — consistent returns")
    if b_moat:
        buff_reasons.append(f"{moat} moat ({moat_trend}) — durable advantage")
    if b_de:
        buff_reasons.append(f"D/E {de:.2f} — conservative leverage")
    if b_fcf:
        buff_reasons.append(f"FCF conversion {fcf_conv:.2f} — owner earnings")
    if b_ocf:
        buff_reasons.append(f"OCF/NI {ocf_ni:.2f} — cash-backed")
    passed_b = sum([b_roe, b_moat, b_de, b_fcf or b_ocf])
    if passed_b >= 3:
        status = "FRANCHISE" if passed_b == 4 else "GOOD BUSINESS"
        picks.append({"framework_idx": 7, "reasons": buff_reasons, "status": status,
                       "result": f"{passed_b}/4 Buffett criteria"})

    # ── 8. Dorsey Moat ──
    # Source: The Little Book That Builds Wealth (2008)
    if moat in ("Wide", "Narrow"):
        d_reasons = [f"Moat: {moat}", f"Trend: {moat_trend}"]
        if v(moat_score):
            d_reasons.append(f"Moat score: {moat_score:.0f}/10")
        if v(roce):
            d_reasons.append(f"ROCE {roce:.1f}% — ROIC proxy")
        status = "WIDE" if moat == "Wide" else "NARROW"
        trend_tag = " ↑" if moat_trend == "widening" else " →" if moat_trend == "stable" else " ↓"
        picks.append({"framework_idx": 8, "reasons": d_reasons, "status": status,
                       "result": f"{moat} Moat{trend_tag}"})

    # ── 9. DCF Intrinsic Value ──
    # Source: Damodaran, Investment Valuation (Wiley)
    dcf_reasons = []
    has_dcf = v(mos_d)
    has_graham = v(mos_g)
    if has_graham:
        dcf_reasons.append(f"Graham MoS: {'+' if mos_g > 0 else ''}{mos_g:.0f}%")
    if has_dcf:
        dcf_reasons.append(f"DCF MoS: {'+' if mos_d > 0 else ''}{mos_d:.0f}%")
    best_mos = mos_d if has_dcf else mos_g if has_graham else None
    if v(best_mos):
        if best_mos > 15:
            picks.append({"framework_idx": 9, "reasons": dcf_reasons, "status": "UNDERVALUED",
                           "result": f"MoS +{best_mos:.0f}% — Undervalued"})
        elif best_mos > -15:
            picks.append({"framework_idx": 9, "reasons": dcf_reasons, "status": "FAIR VALUE",
                           "result": f"MoS {best_mos:+.0f}% — Fair Value"})

    return picks


def _framework_badge(status: str) -> str:
    """Color-coded badge for framework verdict."""
    colors = {
        # Pass/Eligible
        "PASS":         ("#00e676", "#1b5e20"),
        "ELIGIBLE":     ("#00e676", "#1b5e20"),
        "FRANCHISE":    ("#00e676", "#1b5e20"),
        "WIDE":         ("#00e676", "#1b5e20"),
        "STRONG":       ("#00e676", "#1b5e20"),
        "SAFE":         ("#00e676", "#1b5e20"),
        "TOP DECILE":   ("#00e676", "#1b5e20"),
        "BARGAIN":      ("#00e676", "#1b5e20"),
        "UNDERVALUED":  ("#00e676", "#1b5e20"),
        # Partial/Moderate
        "PARTIAL":      ("#64dd17", "#33691e"),
        "MODERATE":     ("#64dd17", "#33691e"),
        "GOOD BUSINESS": ("#64dd17", "#33691e"),
        "NARROW":       ("#64dd17", "#33691e"),
        "GREY":         ("#ffab00", "#4e3a00"),
        "TOP QUARTILE": ("#64dd17", "#33691e"),
        "FAIR":         ("#ffab00", "#4e3a00"),
        "FAIR VALUE":   ("#ffab00", "#4e3a00"),
    }
    fg, bg = colors.get(status, ("#aaa", "#333"))
    return f'<span class="badge" style="background:{bg};color:{fg};border:1px solid {fg}">{escape(status)}</span>'


def _frameworks_html(df) -> str:
    """Build the Investment Frameworks tab content with collapsible sections,
    one-row-per-ticker consensus table, dropdown filters, and multi-sort."""
    qualified = df[df["verdict"].isin(["GEM", "STRONG", "ACCEPTABLE"])].copy()

    all_picks = []
    for i in range(len(qualified)):
        row = qualified.iloc[i]
        matches = _match_frameworks(row)
        for m in matches:
            fw = FRAMEWORKS[m["framework_idx"]]
            all_picks.append({
                "ticker": row.get("ticker", ""),
                "name": row.get("name", ""),
                "sector": row.get("sector", ""),
                "score": row.get("total_score", 0),
                "verdict": row.get("verdict", ""),
                "framework": fw["name"],
                "author": fw["author"],
                "result": m["result"],
                "reasons": "; ".join(m["reasons"]),
                "status": m["status"],
            })

    if not all_picks:
        return '<p class="meta">No stocks matched any framework criteria in this run.</p>'

    # ── Deduplicate by (ticker, framework) ──
    from collections import defaultdict, Counter
    seen = set()
    unique_picks = []
    for p in all_picks:
        key = (p["ticker"], p["framework"])
        if key not in seen:
            seen.add(key)
            unique_picks.append(p)

    # ── Build per-ticker data for consensus table ──
    ticker_data: dict[str, dict] = {}
    for p in unique_picks:
        tk = p["ticker"]
        if tk not in ticker_data:
            ticker_data[tk] = {
                "ticker": tk,
                "name": p["name"],
                "sector": p["sector"],
                "score": p["score"],
                "verdict": p["verdict"],
                "frameworks": [],
            }
        ticker_data[tk]["frameworks"].append({
            "name": p["framework"],
            "result": p["result"],
            "status": p["status"],
        })

    lines = []

    # ════════════════════════════════════════════════
    # Section 1: Multi-Framework Consensus (DEFAULT OPEN)
    # ════════════════════════════════════════════════
    lines.append('<div class="fw-section">')
    lines.append('<div class="fw-section-header open" onclick="toggleSection(this)">')
    lines.append('<span class="fw-chevron">&#9660;</span>')
    lines.append('<h3 style="display:inline;margin:0">Multi-Framework Consensus</h3>')
    lines.append('</div>')
    lines.append('<div class="fw-section-body" style="display:block">')
    lines.append('<p class="meta">One row per stock. Stocks passing 7+/10 frameworks are rare multi-dimensional quality signals. '
                 'Click headers to sort, Shift+Click for multi-column sort.</p>')

    # ── Filter bar ──
    sectors = sorted({d["sector"] for d in ticker_data.values()})
    verdicts = sorted({d["verdict"] for d in ticker_data.values()})
    fw_counts = sorted({len(d["frameworks"]) for d in ticker_data.values()}, reverse=True)
    fw_names_all = sorted({f["name"] for d in ticker_data.values() for f in d["frameworks"]})

    lines.append('<div class="fw-filters">')
    lines.append('<label>Verdict <select id="flt_verdict" onchange="filterConsensus()">'
                 '<option value="">All</option>')
    for v in verdicts:
        lines.append(f'<option value="{escape(v)}">{escape(v)}</option>')
    lines.append('</select></label>')

    lines.append('<label>Fw Count ≥ <select id="flt_fwcount" onchange="filterConsensus()">'
                 '<option value="0">All</option>')
    for fc in fw_counts:
        if fc >= 2:
            lines.append(f'<option value="{fc}">{fc}+</option>')
    lines.append('</select></label>')

    lines.append('<label>Sector <select id="flt_sector" onchange="filterConsensus()">'
                 '<option value="">All</option>')
    for s in sectors:
        lines.append(f'<option value="{escape(s)}">{escape(s)}</option>')
    lines.append('</select></label>')

    lines.append('<label>Framework <select id="flt_framework" onchange="filterConsensus()">'
                 '<option value="">All</option>')
    for fn in fw_names_all:
        lines.append(f'<option value="{escape(fn)}">{escape(fn)}</option>')
    lines.append('</select></label>')

    lines.append('<button class="fw-reset-btn" onclick="resetFilters()">Reset</button>')
    lines.append('</div>')

    # ── Consensus table: one row per ticker ──
    cons_sorted = sorted(ticker_data.values(), key=lambda d: (-len(d["frameworks"]), -d["score"]))

    lines.append('<table id="fw_consensus">')
    lines.append('<thead><tr>')
    cons_cols = [("Stock", False), ("Sector", False), ("Score", True),
                 ("Verdict", False), ("Fw Count", True), ("Frameworks", False)]
    for ci, (label, numeric) in enumerate(cons_cols):
        sort_call = f' onclick="sortTable(\'fw_consensus\',{ci},{str(numeric).lower()},event)" style="cursor:pointer"'
        lines.append(f'<th{sort_call}>{label}</th>')
    lines.append('</tr></thead><tbody>')

    for d in cons_sorted:
        t_score = d["score"]
        fc = len(d["frameworks"])
        fc_color = "var(--green)" if fc >= 7 else "var(--accent)" if fc >= 5 else "var(--text2)"

        # Build framework pills — show name + result as compact badges
        fw_pills = []
        for f in sorted(d["frameworks"], key=lambda x: x["name"]):
            status_cls = "fw-pill-pass" if f["status"] in ("PASS", "STRONG", "SAFE", "ELIGIBLE",
                "FRANCHISE", "WIDE", "UNDERVALUED", "BARGAIN", "TOP DECILE") else "fw-pill-partial"
            fw_pills.append(f'<span class="fw-pill {status_cls}" title="{escape(f["result"])}">'
                            f'{escape(f["name"])}: {escape(f["result"])}</span>')

        # data-fw attribute stores framework names for filtering
        fw_names_str = "|".join(f["name"] for f in d["frameworks"])

        lines.append(f'<tr data-verdict="{escape(d["verdict"])}" data-fwcount="{fc}" '
                     f'data-sector="{escape(d["sector"])}" data-fw="{escape(fw_names_str)}">')
        lines.append(f'<td><a href="#{escape(d["ticker"])}">{escape(d["ticker"])}</a><br>'
                     f'<span style="font-size:0.75rem;color:var(--text2)">{escape(d["name"])}</span></td>')
        lines.append(f'<td>{escape(d["sector"])}</td>')
        lines.append(f'<td data-val="{t_score}" style="color:{_score_color(t_score, 100)};font-weight:700">{t_score:.1f}</td>')
        lines.append(f'<td>{_verdict_badge(d["verdict"])}</td>')
        lines.append(f'<td data-val="{fc}" style="text-align:center;font-weight:700;color:{fc_color}">{fc}/10</td>')
        lines.append(f'<td><div class="fw-pills">{"".join(fw_pills)}</div></td>')
        lines.append('</tr>')

    lines.append('</tbody></table>')
    lines.append('</div></div>')  # close section body + section

    # ════════════════════════════════════════════════
    # Section 2: Results by Framework (COLLAPSED)
    # ════════════════════════════════════════════════
    by_framework: dict[str, list] = defaultdict(list)
    for p in unique_picks:
        by_framework[p["framework"]].append(p)

    lines.append('<div class="fw-section">')
    lines.append('<div class="fw-section-header" onclick="toggleSection(this)">')
    lines.append('<span class="fw-chevron">&#9654;</span>')
    lines.append(f'<h3 style="display:inline;margin:0">Results by Framework '
                 f'<span style="color:var(--text2);font-weight:400">({len(FRAMEWORKS)} frameworks)</span></h3>')
    lines.append('</div>')
    lines.append('<div class="fw-section-body" style="display:none">')

    for fw in FRAMEWORKS:
        fw_name = fw["name"]
        fw_picks = by_framework.get(fw_name, [])
        fw_picks.sort(key=lambda p: -p["score"])
        count = len(fw_picks)

        lines.append(f'<h4 style="margin-top:16px;color:var(--accent)">{escape(fw_name)} '
                     f'<span style="color:var(--text2);font-weight:400">'
                     f'— {escape(fw["author"])} ({count} stocks)</span></h4>')

        if not fw_picks:
            lines.append('<p class="meta">No qualifying stocks pass this framework.</p>')
            continue

        table_id = f'fw_{fw_name.replace(" ", "_").replace("-", "_").lower()}'
        lines.append(f'<table id="{table_id}">')
        lines.append('<thead><tr>')
        fw_cols = [("Ticker", False), ("Name", False), ("Sector", False),
                   ("Score", True), ("Verdict", False), ("Result", False), ("Status", False), ("Detail", False)]
        for ci, (label, numeric) in enumerate(fw_cols):
            sort_call = f' onclick="sortTable(\'{table_id}\',{ci},{str(numeric).lower()},event)" style="cursor:pointer"'
            lines.append(f'<th{sort_call}>{label}</th>')
        lines.append('</tr></thead><tbody>')

        for p in fw_picks:
            t_score = p["score"]
            lines.append('<tr>')
            lines.append(f'<td><a href="#{escape(p["ticker"])}">{escape(p["ticker"])}</a></td>')
            lines.append(f'<td>{escape(p["name"])}</td>')
            lines.append(f'<td>{escape(p["sector"])}</td>')
            lines.append(f'<td data-val="{t_score}" style="color:{_score_color(t_score, 100)};font-weight:700">{t_score:.1f}</td>')
            lines.append(f'<td>{_verdict_badge(p["verdict"])}</td>')
            lines.append(f'<td style="font-weight:600;font-size:0.85rem">{escape(p["result"])}</td>')
            lines.append(f'<td>{_framework_badge(p["status"])}</td>')
            lines.append(f'<td style="font-size:0.8rem;color:var(--text2)">{escape(p["reasons"])}</td>')
            lines.append('</tr>')

        lines.append('</tbody></table>')

    lines.append('</div></div>')  # close section body + section

    # ════════════════════════════════════════════════
    # Section 3: Framework Reference Cards (COLLAPSED)
    # ════════════════════════════════════════════════
    lines.append('<div class="fw-section">')
    lines.append('<div class="fw-section-header" onclick="toggleSection(this)">')
    lines.append('<span class="fw-chevron">&#9654;</span>')
    lines.append(f'<h3 style="display:inline;margin:0">Framework Reference Cards '
                 f'<span style="color:var(--text2);font-weight:400">({len(FRAMEWORKS)} published frameworks)</span></h3>')
    lines.append('</div>')
    lines.append('<div class="fw-section-body" style="display:none">')
    lines.append('<p class="meta" style="margin-top:8px">Every criterion below is from a published book, academic paper, or annual study. '
                 'No speculative or internet-derived rules.</p>')
    lines.append('<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px;">')
    for fw in FRAMEWORKS:
        lines.append('<div class="filter-ref">')
        lines.append(f'<h4 style="margin-bottom:2px">{escape(fw["name"])}</h4>')
        lines.append(f'<p style="color:var(--text2);font-size:0.82rem;margin:2px 0">'
                     f'<strong>{escape(fw["author"])}</strong> — {escape(fw["source"])}</p>')
        lines.append(f'<p style="font-size:0.85rem;margin:4px 0"><strong>Criteria:</strong> {escape(fw["criteria"])}</p>')
        lines.append(f'<p style="font-size:0.82rem;margin:2px 0;color:var(--text2)"><strong>Verdict:</strong> {escape(fw["verdict"])}</p>')
        lines.append('</div>')
    lines.append('</div>')
    lines.append('</div></div>')  # close section body + section

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
    <div class="tab" data-tab="tab-sectors" onclick="showTab('tab-sectors')">By Sector</div>
    <div class="tab" data-tab="tab-allstocks" onclick="showTab('tab-allstocks')">All Stocks</div>
    <div class="tab" data-tab="tab-framework" onclick="showTab('tab-framework')">Frameworks</div>
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

    # ── Tab 4: By Sector ──

    html_parts.append('<div id="tab-sectors" class="tab-panel">')
    html_parts.append('<h2>Sector Breakdown</h2>')

    # Collapsible sector sections
    html_parts.append('<script>function toggleSectorCollapse(idx){var b=document.getElementById("sector-body-"+idx);var h=document.getElementById("sector-header-"+idx);if(b.style.display==="none"){b.style.display="block";h.classList.add("open");}else{b.style.display="none";h.classList.remove("open");}}</script>')

    for i, sector in enumerate(sectors):
        sec_df = df[df["sector"] == sector].sort_values("total_score", ascending=False)
        n = len(sec_df)
        avg = sec_df["total_score"].mean()
        html_parts.append(f'<div class="fw-section">')
        html_parts.append(f'<div class="fw-section-header" id="sector-header-{i}" onclick="toggleSectorCollapse({i})">'
                          f'<span class="fw-chevron">&#x25BC;</span>'
                          f'<span style="font-size:1.1em;font-weight:600">{escape(sector)}</span>'
                          f'<span style="color:#888;font-size:0.95em">({n} stocks, avg {avg:.1f}/100)</span>'
                          f'</div>')
        html_parts.append(f'<div class="fw-section-body" id="sector-body-{i}" style="display:none;">')
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
        html_parts.append('</div></div>')

    html_parts.append('</div>')

    # ── Tab 5: All Stocks (detailed cards) ──
    html_parts.append('<div id="tab-allstocks" class="tab-panel">')
    html_parts.append('<h2>All Stocks &mdash; Detailed Analysis</h2>')
    for i in range(len(df)):
        row = df.iloc[i]
        ticker = str(row.get("ticker", ""))
        html_parts.append(f'<div id="{escape(ticker)}">')
        html_parts.append(_stock_card_html(row))
        html_parts.append('</div>')
    html_parts.append('</div>')

    # ── Tab 6: Frameworks (combined: investment frameworks + scoring reference) ──
    html_parts.append('<div id="tab-framework" class="tab-panel">')

    # ── Section A: Investment Frameworks ──
    html_parts.append('<h2>Investment Frameworks &mdash; Published &amp; Verifiable</h2>')
    html_parts.append('<p class="meta">10 published stock-picking frameworks from academic papers, books, and annual studies. '
                     'Every criterion is auditable &mdash; no speculative or internet-derived rules. '
                     'Stocks passing 7+/10 frameworks are rare multi-dimensional quality signals.</p>')
    html_parts.append(_frameworks_html(df))

    html_parts.append('<hr style="border-color:var(--border);margin:32px 0">')

    # ── Section B: Scoring Framework Reference ──
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
