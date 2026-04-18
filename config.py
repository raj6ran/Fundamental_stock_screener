"""
Stock Screener Configuration — 10-Filter, 100-Point System
============================================================
World-class fundamental screening framework.
Sources: Buffett, Damodaran, Greenblatt, Piotroski, Mukherjea,
         Marks, Dorsey, Lynch, Altman, Mauboussin.

ALL filter definitions with descriptions live here for review.
"""

# ─────────────────────────────────────────────
# EXCHANGE SETTINGS
# ─────────────────────────────────────────────
EXCHANGES = {
    "NSE": {"suffix": ".NS", "currency": "INR", "cap_unit": "Cr"},
    "TSX": {"suffix": ".TO", "currency": "CAD", "cap_unit": "M"},
}
DEFAULT_EXCHANGE = "NSE"

# ═══════════════════════════════════════════════════════════════
# 100-POINT SCORING  (10 dimensions x 10 pts each)
# ═══════════════════════════════════════════════════════════════
#
#  Dim  1   Valuation           /10   Sector PE/PB, PEG, EV/EBITDA, P/S, MoS, Reverse DCF
#  Dim  2   Profitability       /10   ROE, ROCE, ROA, margins, Owner Earnings
#  Dim  3   Growth Quality      /10   Revenue/profit CAGR, incremental ROCE, consistency
#  Dim  4   Financial Health    /10   Altman Z, D/E, current ratio, interest coverage
#  Dim  5   Cash Flow           /10   FCF yield, FCF conversion, OCF/NI, capex ratio
#  Dim  6   Business Moat       /10   7 moat types, moat trend, ROCE durability
#  Dim  7   Earnings Quality    /10   Piotroski F-Score, accrual ratio, cash-backing
#  Dim  8   Institutional       /10   Holdings, analyst targets, insider activity
#  Dim  9   Sector & Macro      /10   Tailwinds, threats, diversification, cyclicality
#  Dim 10   Management          /10   Capital allocation, payout, discipline, dilution
#
#  Filter 11  Red Flags         -> instant REJECT (binary)
#
# ═══════════════════════════════════════════════════════════════

TOTAL_MAX_SCORE = 100

VERDICTS = {
    "GEM":        {"min": 75, "label": "GEM -- Strong Buy"},
    "STRONG":     {"min": 65, "label": "STRONG -- Buy / Accumulate"},
    "ACCEPTABLE": {"min": 55, "label": "ACCEPTABLE -- Hold"},
    "WATCHLIST":  {"min": 40, "label": "WATCHLIST -- Monitor"},
    "REJECT":     {"min": 0,  "label": "REJECT -- Avoid"},
}

# ═══════════════════════════════════════════════════════════════
# FILTER 1: VALUATION -- sector-aware PE/PB + reverse DCF
# ═══════════════════════════════════════════════════════════════
# Source: Damodaran (sector norms), Graham (number), Mauboussin (reverse DCF)
#
# Each sector has its own PE/PB norms because business models differ.
# PE 30 is cheap for FMCG (stable earners) but expensive for Metals.
# Reverse DCF: solve for the growth rate the market implies.
# If implied growth >> historical growth, stock is overpriced.

SECTOR_PE_NORMS = {
    "Automobile and Auto Components":     {"avg": 22, "cheap": 14, "expensive": 30},
    "Capital Goods":                      {"avg": 25, "cheap": 16, "expensive": 35},
    "Chemicals":                          {"avg": 30, "cheap": 20, "expensive": 42},
    "Construction Materials":             {"avg": 25, "cheap": 15, "expensive": 38},
    "Consumer Durables":                  {"avg": 45, "cheap": 28, "expensive": 65},
    "Consumer Services":                  {"avg": 40, "cheap": 25, "expensive": 60},
    "Diversified":                        {"avg": 20, "cheap": 12, "expensive": 30},
    "Fast Moving Consumer Goods":         {"avg": 45, "cheap": 30, "expensive": 60},
    "Fertilizers & Agrochemicals":        {"avg": 15, "cheap": 8,  "expensive": 25},
    "Financial Services":                 {"avg": 15, "cheap": 10, "expensive": 22},
    "Forest Materials":                   {"avg": 12, "cheap": 7,  "expensive": 20},
    "Healthcare":                         {"avg": 30, "cheap": 22, "expensive": 42},
    "Information Technology":             {"avg": 28, "cheap": 20, "expensive": 38},
    "Media, Entertainment & Publication": {"avg": 22, "cheap": 12, "expensive": 35},
    "Metals & Mining":                    {"avg": 10, "cheap": 6,  "expensive": 16},
    "Oil, Gas & Consumable Fuels":        {"avg": 12, "cheap": 8,  "expensive": 18},
    "Real Estate":                        {"avg": 25, "cheap": 15, "expensive": 40},
    "Retailing":                          {"avg": 50, "cheap": 30, "expensive": 75},
    "Services":                           {"avg": 28, "cheap": 18, "expensive": 40},
    "Telecommunication":                  {"avg": 20, "cheap": 12, "expensive": 30},
    "Textiles":                           {"avg": 18, "cheap": 10, "expensive": 28},
    "Utilities":                          {"avg": 14, "cheap": 8,  "expensive": 22},
}

SECTOR_PB_NORMS = {
    "Automobile and Auto Components":     {"avg": 5,   "cheap": 2,   "expensive": 10},
    "Capital Goods":                      {"avg": 5,   "cheap": 2,   "expensive": 10},
    "Chemicals":                          {"avg": 5,   "cheap": 2,   "expensive": 10},
    "Construction Materials":             {"avg": 4,   "cheap": 1.5, "expensive": 8},
    "Consumer Durables":                  {"avg": 10,  "cheap": 4,   "expensive": 20},
    "Consumer Services":                  {"avg": 8,   "cheap": 3,   "expensive": 18},
    "Diversified":                        {"avg": 3,   "cheap": 1,   "expensive": 6},
    "Fast Moving Consumer Goods":         {"avg": 12,  "cheap": 6,   "expensive": 25},
    "Fertilizers & Agrochemicals":        {"avg": 3,   "cheap": 1,   "expensive": 6},
    "Financial Services":                 {"avg": 2.5, "cheap": 1,   "expensive": 4},
    "Forest Materials":                   {"avg": 2,   "cheap": 0.8, "expensive": 4},
    "Healthcare":                         {"avg": 5,   "cheap": 2,   "expensive": 10},
    "Information Technology":             {"avg": 8,   "cheap": 4,   "expensive": 15},
    "Media, Entertainment & Publication": {"avg": 3,   "cheap": 1,   "expensive": 6},
    "Metals & Mining":                    {"avg": 1.5, "cheap": 0.7, "expensive": 3},
    "Oil, Gas & Consumable Fuels":        {"avg": 2,   "cheap": 1,   "expensive": 4},
    "Real Estate":                        {"avg": 2.5, "cheap": 1.2, "expensive": 5},
    "Retailing":                          {"avg": 12,  "cheap": 5,   "expensive": 25},
    "Services":                           {"avg": 6,   "cheap": 2,   "expensive": 12},
    "Telecommunication":                  {"avg": 3,   "cheap": 1,   "expensive": 6},
    "Textiles":                           {"avg": 3,   "cheap": 1.5, "expensive": 6},
    "Utilities":                          {"avg": 2,   "cheap": 1,   "expensive": 4},
}

# Cyclical sectors need normalised PE (avg over cycle, not TTM)
# Source: Howard Marks -- "The Most Important Thing"
CYCLICAL_SECTORS = {
    "Metals & Mining", "Oil, Gas & Consumable Fuels",
    "Automobile and Auto Components", "Real Estate",
    "Construction Materials", "Fertilizers & Agrochemicals",
}


# ═══════════════════════════════════════════════════════════════
# FILTER 2: PROFITABILITY
# ═══════════════════════════════════════════════════════════════
# Source: Buffett (ROE), Mukherjea (ROCE), Greenblatt (ROIC)
#
# ROCE > 15% sustained = quality. ROE > 20% = excellent.
# Owner Earnings = Net Income + D&A - Maintenance CapEx.

PROFITABILITY = {
    "roe_min": 12,              "roe_excellent": 25,
    "roce_min": 15,             "roce_excellent": 25,
    "roa_min": 5,               "roa_excellent": 12,
    "operating_margin_min": 12, "operating_margin_excellent": 25,
    "net_margin_min": 8,        "net_margin_excellent": 20,
}


# ═══════════════════════════════════════════════════════════════
# FILTER 3: GROWTH QUALITY
# ═══════════════════════════════════════════════════════════════
# Source: Lynch (PEG), Srinivasan (compounders), Mukherjea (ROIIC)
#
# Incremental ROCE = delta NOPAT / delta invested capital.
# ROCE 20% but ROIIC 8% = running out of quality reinvestment.

GROWTH = {
    "revenue_cagr_min": 10,     "revenue_cagr_excellent": 20,
    "profit_cagr_min": 12,      "profit_cagr_excellent": 25,
    "incremental_roce_min": 12, "incremental_roce_excellent": 25,
}


# ═══════════════════════════════════════════════════════════════
# FILTER 4: FINANCIAL HEALTH
# ═══════════════════════════════════════════════════════════════
# Source: Altman (Z-Score), Graham (conservative balance sheet)
#
# Altman Z = 1.2*WC/TA + 1.4*RE/TA + 3.3*EBIT/TA + 0.6*MCap/TL + Rev/TA
# Z > 2.99 = safe, 1.81-2.99 = grey, < 1.81 = distress

FINANCIAL_HEALTH = {
    "debt_to_equity_max": 1.0,  "de_threshold_high": 1.5,
    "current_ratio_min": 1.0,   "current_ratio_good": 1.5,
    "interest_coverage_min": 3, "interest_coverage_good": 6,
    "altman_z_safe": 2.99,      "altman_z_distress": 1.81,
}


# ═══════════════════════════════════════════════════════════════
# FILTER 5: CASH FLOW
# ═══════════════════════════════════════════════════════════════
# Source: Greenblatt (FCF yield), Srinivasan (cash > earnings)
#
# FCF Conversion = FCF / Net Income. Must be > 80%.
# Companies reporting profits without generating cash are suspect.

CASH_FLOW = {
    "fcf_conversion_min": 0.6,    "fcf_conversion_good": 0.9,
    "fcf_yield_min": 2,           "fcf_yield_good": 6,
    "ocf_to_net_income_min": 0.8, "ocf_to_net_income_good": 1.2,
}


# ═══════════════════════════════════════════════════════════════
# FILTER 6: BUSINESS MOAT -- 7 recognised types
# ═══════════════════════════════════════════════════════════════
# Source: Pat Dorsey (Morningstar), Buffett, Porter
#
# Moat trend: eroding moat (declining ROCE + rising revenue =
# competing on price) is WORSE than no moat.

MOAT_THRESHOLDS = {
    "cost_advantage_opm":       20,    # OPM % for cost advantage (no hint)
    "cost_advantage_mcap_cr":   50000, # Min market cap for cost advantage (no hint)
    "cost_advantage_hint_opm":  15,    # OPM % for cost advantage (with sector hint)
    "network_effect_rev_g":     15,    # Revenue CAGR % for network effect
    "switching_cost_roce":      20,    # ROCE % for switching cost
    "intangible_opm":           18,    # OPM % for intangible (no hint)
    "intangible_pb":            5,     # PB for intangible (no hint)
    "intangible_hint_opm":      15,    # OPM % for intangible (with hint)
    "distribution_mcap_cr":     20000, # Min market cap for distribution moat
    "data_advantage_opm":       15,    # OPM % for data advantage
}

MOAT_TYPES = {
    "cost_advantage":    "Lowest cost producer / economies of scale",
    "network_effect":    "Value increases with more users",
    "switching_cost":    "Painful for customers to switch",
    "intangible_assets": "Brand, patents, IP, licences",
    "regulatory":        "Government licence / legal monopoly",
    "distribution":      "Unmatched distribution network",
    "data_advantage":    "Proprietary data creating feedback loops",
}

SECTOR_MOAT_HINTS = {
    "Automobile and Auto Components":     ["intangible_assets", "cost_advantage", "distribution"],
    "Capital Goods":                      ["regulatory", "cost_advantage", "switching_cost"],
    "Chemicals":                          ["cost_advantage", "intangible_assets", "switching_cost"],
    "Construction Materials":             ["cost_advantage", "distribution", "regulatory"],
    "Consumer Durables":                  ["intangible_assets", "distribution", "switching_cost"],
    "Consumer Services":                  ["intangible_assets", "network_effect", "switching_cost"],
    "Diversified":                        ["cost_advantage", "distribution", "regulatory"],
    "Fast Moving Consumer Goods":         ["intangible_assets", "distribution", "cost_advantage"],
    "Fertilizers & Agrochemicals":        ["regulatory", "cost_advantage", "distribution"],
    "Financial Services":                 ["switching_cost", "network_effect", "regulatory"],
    "Forest Materials":                   ["cost_advantage", "regulatory"],
    "Healthcare":                         ["intangible_assets", "regulatory", "distribution"],
    "Information Technology":             ["switching_cost", "intangible_assets", "data_advantage"],
    "Media, Entertainment & Publication": ["intangible_assets", "network_effect", "data_advantage"],
    "Metals & Mining":                    ["cost_advantage", "regulatory"],
    "Oil, Gas & Consumable Fuels":        ["regulatory", "cost_advantage", "distribution"],
    "Real Estate":                        ["regulatory", "distribution", "cost_advantage"],
    "Retailing":                          ["distribution", "intangible_assets", "network_effect"],
    "Services":                           ["switching_cost", "intangible_assets", "data_advantage"],
    "Telecommunication":                  ["network_effect", "regulatory", "distribution"],
    "Textiles":                           ["cost_advantage", "distribution", "intangible_assets"],
    "Utilities":                          ["regulatory", "cost_advantage", "distribution"],
}


# ═══════════════════════════════════════════════════════════════
# FILTER 7: EARNINGS QUALITY -- Piotroski + Accruals
# ═══════════════════════════════════════════════════════════════
# Source: Piotroski (F-Score), Beneish (M-Score concept)
#
# Piotroski F-Score (0-9): 9 binary tests. Scores 8-9
# outperform by 7.5% annually.
# Accrual Ratio = (NI - OCF) / Total Assets.
# High accruals (> 10%) = paper earnings = red flag.

EARNINGS_QUALITY = {
    "piotroski_excellent": 8,
    "piotroski_good": 6,
    "piotroski_weak": 3,
    "accrual_ratio_max": 0.10,
    "accrual_ratio_ideal": 0.0,
}


# ═══════════════════════════════════════════════════════════════
# FILTER 8: INSTITUTIONAL BACKING
# ═══════════════════════════════════════════════════════════════
# Source: Lynch (follow smart money but verify)

INSTITUTIONAL = {
    "institutional_holding_min": 20,
    "insider_holding_min": 10,
}


# ═══════════════════════════════════════════════════════════════
# FILTER 9: SECTOR & MACRO
# ═══════════════════════════════════════════════════════════════
# Source: Dalio (macro), Marathon AM (capital cycles)

SECTOR_TAILWINDS = {
    "Automobile and Auto Components": 7, "Capital Goods": 9, "Chemicals": 7,
    "Construction Materials": 7, "Consumer Durables": 8, "Consumer Services": 8,
    "Diversified": 6, "Fast Moving Consumer Goods": 7,
    "Fertilizers & Agrochemicals": 6, "Financial Services": 7,
    "Forest Materials": 5, "Healthcare": 8, "Information Technology": 7,
    "Media, Entertainment & Publication": 7, "Metals & Mining": 5,
    "Oil, Gas & Consumable Fuels": 6, "Real Estate": 8, "Retailing": 8,
    "Services": 7, "Telecommunication": 7, "Textiles": 6, "Utilities": 7,
}

SECTOR_DIVERSIFICATION = {
    "Automobile and Auto Components": 5, "Capital Goods": 5, "Chemicals": 6,
    "Construction Materials": 4, "Consumer Durables": 7, "Consumer Services": 7,
    "Diversified": 8, "Fast Moving Consumer Goods": 7,
    "Fertilizers & Agrochemicals": 4, "Financial Services": 5,
    "Forest Materials": 3, "Healthcare": 6, "Information Technology": 7,
    "Media, Entertainment & Publication": 5, "Metals & Mining": 3,
    "Oil, Gas & Consumable Fuels": 4, "Real Estate": 3, "Retailing": 6,
    "Services": 6, "Telecommunication": 4, "Textiles": 5, "Utilities": 4,
}

SECTOR_THREATS = {
    "Automobile and Auto Components": 5, "Capital Goods": 7, "Chemicals": 6,
    "Construction Materials": 6, "Consumer Durables": 6, "Consumer Services": 6,
    "Diversified": 5, "Fast Moving Consumer Goods": 8,
    "Fertilizers & Agrochemicals": 5, "Financial Services": 6,
    "Forest Materials": 4, "Healthcare": 7, "Information Technology": 6,
    "Media, Entertainment & Publication": 5, "Metals & Mining": 4,
    "Oil, Gas & Consumable Fuels": 5, "Real Estate": 5, "Retailing": 6,
    "Services": 6, "Telecommunication": 5, "Textiles": 5, "Utilities": 6,
}


# ═══════════════════════════════════════════════════════════════
# FILTER 10: MANAGEMENT QUALITY
# ═══════════════════════════════════════════════════════════════
# Source: Buffett, Munger (capital allocation + integrity)

MANAGEMENT = {
    "payout_ratio_ideal_min": 15,
    "payout_ratio_ideal_max": 60,
}


# ═══════════════════════════════════════════════════════════════
# RED FLAGS -- any one triggers instant REJECT
# ═══════════════════════════════════════════════════════════════
# Source: Altman (distress), Graham (safety), Lynch (warnings)

RED_FLAGS = {
    "pe_max": 60,
    "debt_to_equity_max": 2.0,
    "interest_coverage_min": 1.5,
    "profit_declining_quarters": 3,
    "market_cap_min_cr": 500,
    "promoter_pledge_max": 50,
    "altman_z_min": 1.81,
    "piotroski_min": 2,
    "accrual_ratio_max": 0.25,
}


# ═══════════════════════════════════════════════════════════════
# SECTOR-SPECIFIC ADJUSTMENTS
# ═══════════════════════════════════════════════════════════════
# Financial companies (banks, NBFCs, insurance, AMCs) use leverage
# as their core business model.  Standard industrial metrics for
# D/E, FCF, IC, Altman Z, and Piotroski are structurally biased
# against them.  Source: Damodaran "Valuing Financial Service Firms".
#
# Capital-intensive regulated sectors (Utilities, Telecom) carry
# higher leverage than industrials but with stable, predictable
# cash flows.  D/E 2-3× is standard.

FINANCIAL_SECTORS = {"Financial Services"}

# Regulated capex-heavy sectors where D/E up to 3× is standard
HIGH_LEVERAGE_SECTORS = {"Utilities", "Telecommunication"}

# Red-flag checks to SKIP for financial-sector companies.
# None = skip that check entirely.
RED_FLAGS_FINANCIAL_SKIP = {
    "debt_to_equity_max",       # Leverage IS the business model
    "interest_coverage_min",    # Interest expense is operating cost (NIM matters)
    "altman_z_min",             # Original model not designed for financials (Altman 1968)
    "piotroski_min",            # Structurally biased (leverage, CR, asset-turnover tests)
    "accrual_ratio_max",        # Distorted by loan-book changes in OCF
    "negative_fcf",             # Loan-book growth shows as negative OCF/FCF
}

# Higher D/E threshold for regulated capital-intensive sectors
RED_FLAGS_HIGH_LEVERAGE_DE_MAX = 3.0

# ── Financial-sector scoring overrides ──
# D/E scoring: For an NBFC/bank, D/E 3× = well-capitalised, D/E 8× = over-leveraged
FINANCIAL_DE_IDEAL = 3.0
FINANCIAL_DE_WORST = 8.0

# ROA norms: Banks 1-2% is good; NBFCs 2-3%+ is excellent.
FINANCIAL_ROA_MIN = 1.0
FINANCIAL_ROA_EXCELLENT = 3.0

# Coffee Can: Mukherjea uses D/E ≤ 1.0 for industrials.
# For financials a well-capitalised NBFC with D/E ≤ 5 qualifies.
COFFEE_CAN_FINANCIAL_DE_MAX = 5.0


# ─────────────────────────────────────────────
# INTRINSIC VALUE
# ─────────────────────────────────────────────
DCF_PARAMS = {
    "discount_rate": 0.12,
    "terminal_growth_rate": 0.03,
    "projection_years": 10,
    "margin_of_safety": 0.25,
    "fade_start_year": 5,
}

GRAHAM_NUMBER_MULTIPLIER = 22.5

# ─────────────────────────────────────────────
# COFFEE CAN CRITERIA
# ─────────────────────────────────────────────
COFFEE_CAN = {
    "revenue_cagr_min": 10,
    "roce_min": 15,
    "debt_to_equity_max": 1.0,
}


# ═══════════════════════════════════════════════════════════════
# SECTOR DEFINITIONS -- NSE
# ═══════════════════════════════════════════════════════════════

NSE_SECTORS = {
    # ─────────────────────────────────────────────
    # 1. Automobile and Auto Components
    # ─────────────────────────────────────────────
    "Automobile and Auto Components": {
        "description": "Passenger & Commercial Vehicle OEMs, Auto Parts, Tyres, Batteries, EV",
        "stocks": [
            "MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS",
            "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "FORCEMOT.NS", "OLECTRA.NS",
            "MOTHERSON.NS", "BOSCHLTD.NS", "BHARATFORG.NS", "BALKRISIND.NS", "SONACOMS.NS",
            "TIINDIA.NS", "SUNDRMFAST.NS", "ENDURANCE.NS", "UNOMINDA.NS", "CRAFTSMAN.NS",
            "MRF.NS", "APOLLOTYRE.NS", "CEATLTD.NS", "JKTYRE.NS", "EXIDEIND.NS",
            "AMARARAJA.NS", "SCHAEFFLER.NS", "SKFINDIA.NS", "TIMKEN.NS", "SUPRAJIT.NS",
            "GABRIEL.NS", "LUMAXTECH.NS", "SANDHAR.NS", "JTEKTINDIA.NS", "VARROC.NS",
            "SWARAJENG.NS", "MAHINDCIE.NS", "TATAMTRDVR.NS", "JAMNAAUTO.NS", "JBMA.NS",
            "FIEM.NS", "ANANDAS.NS", "SETCO.NS", "WABCOINDIA.NS", "WHEELS.NS",
            "JTLIND.NS", "MINDA.NS", "VSTTILLERS.NS", "RACL.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 2. Capital Goods
    # ─────────────────────────────────────────────
    "Capital Goods": {
        "description": "Engineering, Defence, Railways, Electricals, Shipbuilding, Industrial Machinery",
        "stocks": [
            "LT.NS", "ABB.NS", "SIEMENS.NS", "HAL.NS", "BEL.NS",
            "CUMMINSIND.NS", "THERMAX.NS", "BHEL.NS", "CGPOWER.NS", "KAYNES.NS",
            "COCHINSHIP.NS", "MAZDOCK.NS", "GRSE.NS", "BDL.NS", "BEML.NS",
            "ASTRAMICRO.NS", "HONEYWELL.NS", "TRIVENITUR.NS", "ELECON.NS", "KENNAMETAL.NS",
            "VOLTAMP.NS", "ACE.NS", "AIAENG.NS", "TITAGARH.NS", "KEC.NS",
            "ENGINERSIN.NS", "PRAJ.NS", "ELGIEQUIP.NS", "RVNL.NS", "IRCON.NS",
            "GRINFRA.NS", "ESCORTS.NS", "KPIL.NS", "NBCC.NS", "MANINFRA.NS",
            "JKINFRA.NS", "HCC.NS", "PNC.NS", "GPPL.NS", "HGINFRA.NS",
            "NCC.NS", "HUDCO.NS", "ISGEC.NS", "GMRINFRA.NS", "JSWINFRA.NS",
            "MAZDA.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 3. Chemicals
    # ─────────────────────────────────────────────
    "Chemicals": {
        "description": "Specialty Chemicals, Agrochemicals, Polymers, Paints",
        "stocks": [
            "PIDILITIND.NS", "ASIANPAINT.NS", "SRF.NS", "ATUL.NS", "PIIND.NS",
            "NAVINFLUOR.NS", "FLUOROCHEM.NS", "TATACHEM.NS", "CLEAN.NS", "DEEPAKNTR.NS",
            "AARTIIND.NS", "GALAXYSURF.NS", "SUMICHEM.NS", "UPL.NS", "BASF.NS",
            "LXCHEM.NS", "ALKYLAMINE.NS", "FINEORG.NS", "SUDARSCHEM.NS", "VINATIORGA.NS",
            "NOCIL.NS", "ROSSARI.NS", "APCOTEXIND.NS", "CHEMPLAST.NS", "GUJALKALI.NS",
            "IONEXCHANG.NS", "BALAMINES.NS", "NEOGEN.NS", "ANUPAM.NS", "RALLIS.NS",
            "BERGEPAINT.NS", "KANSAINER.NS", "GODREJIND.NS", "TIRUMALCHM.NS", "ORIENTCEM.NS",
            "EPIGRAL.NS", "IGPL.NS", "GHCL.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 4. Construction Materials
    # ─────────────────────────────────────────────
    "Construction Materials": {
        "description": "Cement, Building Materials, Pipes, Ceramics",
        "stocks": [
            "ULTRACEMCO.NS", "SHREECEM.NS", "AMBUJACEM.NS", "ACC.NS", "DALBHARAT.NS",
            "JKCEMENT.NS", "RAMCOCEM.NS", "INDIACEM.NS", "NUVOCO.NS", "BIRLACEM.NS",
            "STARCEM.NS", "HEIDELBERG.NS", "SAGCEM.NS", "DECCAN.NS", "FINOLEX.NS",
            "KAJARIACER.NS", "CERA.NS", "ORIENTBELL.NS", "SOMANY.NS", "HSIL.NS",
            "JKLAKSHMI.NS", "SAGAR.NS", "KESORAMIND.NS", "PRISMJOINS.NS", "JKIL.NS",
            "SRHHYPOLTD.NS", "HINDWAREAP.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 5. Consumer Durables
    # ─────────────────────────────────────────────
    "Consumer Durables": {
        "description": "Electronics, Appliances, Jewellery, Watches, Lighting",
        "stocks": [
            "ORIENTELEC.NS", "TITAN.NS", "HAVELLS.NS", "VOLTAS.NS", "POLYCAB.NS",
            "DIXON.NS", "BLUESTAR.NS", "CROMPTON.NS", "WHIRLPOOL.NS", "AMBER.NS",
            "VGUARD.NS", "SYMPHONY.NS", "IFBIND.NS", "TTKPRESTIG.NS", "BAJAJELEC.NS",
            "STOVEKRAFT.NS", "BAJAJCON.NS", "BATAINDIA.NS", "RELAXO.NS", "BOROSIL.NS",
            "SAFARI.NS", "VIPIND.NS", "CAMPUS.NS", "PAGEIND.NS", "RAYMOND.NS",
            "MANYAVAR.NS", "HONAUT.NS", "DOMS.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 6. Consumer Services
    # ─────────────────────────────────────────────
    "Consumer Services": {
        "description": "Hotels, Restaurants, Tourism, QSR, Education, E-commerce",
        "stocks": [
            "IRCTC.NS", "INDIGO.NS", "WONDERLA.NS", "INDHOTEL.NS", "MHRIL.NS",
            "CARTRADE.NS", "LEMONTRE.NS", "CHALET.NS", "JUBLFOOD.NS", "DEVYANI.NS",
            "SAPPHIRE.NS", "WESTLIFE.NS", "ZOMATO.NS", "BARBEQUE.NS", "NAUKRI.NS",
            "JUSTDIAL.NS", "NAVNETEDUL.NS", "APTECH.NS", "MAHSEAMLES.NS", "GATI.NS",
            "THOMASCOOK.NS", "EASEMYTRIP.NS", "PVRINOX.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 7. Diversified
    # ─────────────────────────────────────────────
    "Diversified": {
        "description": "Diversified Conglomerates, Multi-sector Holdings",
        "stocks": [
            "GRASIM.NS", "ADANIENT.NS", "3MINDIA.NS", "DCMSHRIRAM.NS", "RPSGVENT.NS",
            "TVSSCS.NS", "BHARATRAS.NS", "BAJAJHLDNG.NS", "EDELWEISS.NS", "PIRAMALENT.NS",
            "WOCKPHARMA.NS", "CG.NS", "ESSELPRO.NS", "NBVENTURES.NS", "SHILCHAR.NS",
            "KIRLOSENG.NS", "INGERRAND.NS", "GREAVESCOT.NS", "EVERESTIND.NS", "HBLPOWER.NS",
            "AARTIDRUGS.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 8. Fast Moving Consumer Goods
    # ─────────────────────────────────────────────
    "Fast Moving Consumer Goods": {
        "description": "Food, Beverages, Personal Care, Household Products",
        "stocks": [
            "GILLETTE.NS", "PGHH.NS", "VBL.NS", "CCL.NS", "ITC.NS",
            "TATACONSUM.NS", "EMAMILTD.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS",
            "DABUR.NS", "MARICO.NS", "GODREJCP.NS", "COLPAL.NS", "JYOTHYLAB.NS",
            "RADICO.NS", "BIKAJI.NS", "ZYDUSWELL.NS", "HATSUN.NS", "GODFRYPHLP.NS",
            "MCDOWELL-N.NS", "UBL.NS", "BALRAMCHIN.NS", "EIDPARRY.NS", "KRBL.NS",
            "PATANJALI.NS", "DODLA.NS", "AVANTIFEED.NS", "HERITGFOOD.NS", "VADILALIND.NS",
            "APLLTD.NS", "BECTORFOOD.NS", "AWL.NS", "RAJESHEXPO.NS", "VSTIND.NS",
            "VENKEYS.NS", "PRATAAP.NS", "BCONCEPTS.NS", "UFLEX.NS", "JUBLPHARMA.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 9. Fertilizers & Agrochemicals
    # ─────────────────────────────────────────────
    "Fertilizers & Agrochemicals": {
        "description": "Fertilizers, Crop Protection, Seeds, Agrochemicals",
        "stocks": [
            "DEEPAKFERT.NS", "ZUARIIND.NS", "COROMANDEL.NS", "CHAMBLFERT.NS", "GNFC.NS",
            "GSFC.NS", "NFL.NS", "RCF.NS", "FACT.NS", "MANGCHEFER.NS",
            "KSCL.NS", "DHANUKA.NS", "BAYERCROP.NS", "INSECTICID.NS", "SHARDACROP.NS",
            "ASTEC.NS", "KAVERI.NS", "DHAMPURSUG.NS", "NATCOPHARM.NS", "GODREJAGRO.NS",
            "ADVENZYMES.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 10. Financial Services
    # ─────────────────────────────────────────────
    "Financial Services": {
        "description": "Banks, NBFCs, Insurance, AMCs, Brokerages, Exchanges",
        "stocks": [
            "POLICYBZR.NS", "PAYTM.NS", "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS",
            "AXISBANK.NS", "INDUSINDBK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "BANDHANBNK.NS",
            "RBLBANK.NS", "AUBANK.NS", "SBIN.NS", "BANKBARODA.NS", "PNB.NS",
            "CANBK.NS", "UNIONBANK.NS", "IOB.NS", "CENTRALBK.NS", "INDIANB.NS",
            "IDBI.NS", "MAHABANK.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS",
            "SHRIRAMFIN.NS", "M&MFIN.NS", "MUTHOOTFIN.NS", "MANAPPURAM.NS", "POONAWALLA.NS",
            "FIVESTAR.NS", "CREDITACC.NS", "HDFCLIFE.NS", "SBILIFE.NS", "ICICIPRULI.NS",
            "ICICIGI.NS", "LICI.NS", "STARHEALTH.NS", "NIACL.NS", "GICRE.NS",
            "HDFCAMC.NS", "NIPPONIND.NS", "UTIAMC.NS", "KFINTECH.NS", "ANGELONE.NS",
            "BSE.NS", "CDSL.NS", "MCX.NS", "CRISIL.NS", "MOTILALOFS.NS",
            "LICHSGFIN.NS", "PNBHOUSING.NS", "CANFINHOME.NS", "AAVAS.NS", "RECLTD.NS",
            "IRFC.NS", "PFC.NS", "SBICARD.NS", "ABCAPITAL.NS", "SUNDARMFIN.NS",
            "EQUITASBNK.NS", "UJJIVANSFB.NS", "KARURVYSYA.NS", "CUB.NS", "SOUTHBANK.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 11. Forest Materials
    # ─────────────────────────────────────────────
    "Forest Materials": {
        "description": "Paper, Packaging, Wood Products, Pulp",
        "stocks": [
            "GRINDWELL.NS", "CARBORUNIV.NS", "TARSONS.NS", "SUPREMEIND.NS", "ASTRAL.NS",
            "PRINCEPIPE.NS", "APOLLOPIPE.NS", "SUPRPIPES.NS", "CENTURYPLY.NS", "GREENPLY.NS",
            "HIL.NS", "GPIL.NS", "NILKAMAL.NS", "HINDPAPER.NS", "TNPL.NS",
            "STARPAPER.NS", "JKPAPER.NS", "WSTCSTPAPR.NS", "EPL.NS", "HUHTAMAKI.NS",
            "MOLD-TEK.NS", "ESTER.NS", "COSMOFILMS.NS", "JINDALPOLY.NS", "EMAMIPAP.NS",
            "RUCHIRA.NS", "SESHAPAPER.NS", "RITCO.NS", "SATIA.NS", "ORIENTPPR.NS",
            "BALKRISHNA.NS", "TCPLPACK.NS", "WINPRO.NS", "AGI.NS", "SHAILY.NS",
            "MONTECARLO.NS", "PSPPROJECT.NS", "VESUVIUS.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 12. Healthcare
    # ─────────────────────────────────────────────
    "Healthcare": {
        "description": "Pharmaceuticals, Hospitals, Diagnostics, API, Medical Devices",
        "stocks": [
            "SOLARA.NS", "IOLCP.NS", "LALPATHLAB.NS", "ASTRAZEN.NS", "MAXHEALTH.NS",
            "BIOCON.NS", "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS",
            "ZYDUSLIFE.NS", "AUROPHARMA.NS", "LUPIN.NS", "TORNTPHARM.NS", "ALKEM.NS",
            "APOLLOHOSP.NS", "FORTIS.NS", "MEDANTA.NS", "YATHARTH.NS", "RAINBOW.NS",
            "METROPOLIS.NS", "THYROCARE.NS", "KRSNAA.NS", "VIJAYA.NS", "GLENMARK.NS",
            "IPCALAB.NS", "NATCOPHARMA.NS", "LAURUSLABS.NS", "SYNGENE.NS", "MANKIND.NS",
            "JBCHEPHARM.NS", "GRANULES.NS", "AJANTPHARM.NS", "ERIS.NS", "ABBOTINDIA.NS",
            "PFIZER.NS", "GLAXO.NS", "SANOFI.NS", "POLYMED.NS", "MEDPLUS.NS",
            "GLAND.NS", "CONCORD.NS", "SUVENPHAR.NS", "PPLPHARMA.NS", "CAPLIPOINT.NS",
            "NEULANDLAB.NS", "MARKSANS.NS", "SHILPAMED.NS", "GLORIALAB.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 13. Information Technology
    # ─────────────────────────────────────────────
    "Information Technology": {
        "description": "IT Services, Software Products, BPO, SaaS, Digital Platforms",
        "stocks": [
            "DATAPATTNS.NS", "MAPMYINDIA.NS", "NIITLTD.NS", "ROUTE.NS", "RATEGAIN.NS",
            "HAPPSTMNDS.NS", "LATENTVIEW.NS", "MPHASIS.NS", "CIGNITITEC.NS", "TCS.NS",
            "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS",
            "PERSISTENT.NS", "COFORGE.NS", "LTTS.NS", "TATAELXSI.NS", "KPITTECH.NS",
            "CYIENT.NS", "ZENSAR.NS", "BIRLASOFT.NS", "INTELLECT.NS", "NEWGEN.NS",
            "MASTEK.NS", "OFSS.NS", "ECLERX.NS", "TANLA.NS", "AFFLE.NS",
            "SONATSOFTW.NS", "FIRSTSOURCE.NS", "TATATECH.NS", "3IINFOLTD.NS", "CMSINFO.NS",
            "NUCLEUS.NS", "QUICKHEAL.NS", "BSOFT.NS", "NETWEB.NS", "SASKEN.NS",
            "EMUDHRA.NS", "SUBEXLTD.NS", "RAMCOSYS.NS", "INFIBEAM.NS", "SAKSOFT.NS",
            "AURIONPRO.NS", "HEXAWARE.NS", "MSTCLTD.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 14. Media, Entertainment & Publication
    # ─────────────────────────────────────────────
    "Media, Entertainment & Publication": {
        "description": "Broadcasting, OTT, Film Production, Publishing, Gaming",
        "stocks": [
            "ZEEL.NS", "SUNTV.NS", "TV18BRDCST.NS", "NETWORK18.NS", "NDTV.NS",
            "NAZARA.NS", "SAREGAMA.NS", "HATHWAY.NS", "DEN.NS", "GTPL.NS",
            "DBCORP.NS", "JAGRAN.NS", "TVTODAY.NS", "BALAJITELE.NS", "SHEMAROO.NS",
            "TIPSINDLTD.NS", "DISH.NS", "WARNERMEDIA.NS", "MIRAE.NS", "HMVL.NS",
            "SANDESH.NS", "PRSMJOHNSN.NS", "EROSMEDIA.NS", "UFO.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 15. Metals & Mining
    # ─────────────────────────────────────────────
    "Metals & Mining": {
        "description": "Steel, Aluminium, Copper, Mining, Metal Products, Ferro Alloys",
        "stocks": [
            "APLAPOLLO.NS", "RATNAMANI.NS", "RAIN.NS", "PENIND.NS", "JSWSTEEL.NS",
            "WELCORP.NS", "JINDALSAW.NS", "JSPL.NS", "JSWHL.NS", "TATAMETALIK.NS",
            "TATASTEEL.NS", "HINDALCO.NS", "VEDL.NS", "NMDC.NS", "JINDALSTEL.NS",
            "NATIONALUM.NS", "HINDZINC.NS", "SAIL.NS", "MOIL.NS", "KIOCL.NS",
            "GRAVITA.NS", "HINDCOPPER.NS", "MIDHANI.NS", "GODAWARI.NS", "SHYAMMETL.NS",
            "SARDAEN.NS", "GALLANTT.NS", "TINPLATE.NS", "RAJRATAN.NS", "MANAKSIA.NS",
            "JSL.NS", "LLOYDSME.NS", "NFASL.NS", "COALINDIA.NS", "MISHRA.NS",
            "HLEGLAS.NS", "ORIENTREF.NS", "WELBONDGR.NS", "MTARTECH.NS", "SANDUMA.NS",
            "PRAKASH.NS", "STEELCAS.NS", "KALYANI.NS", "MUKANDLTD.NS", "SHYAMCENT.NS",
            "UNIPARTS.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 16. Oil, Gas & Consumable Fuels
    # ─────────────────────────────────────────────
    "Oil, Gas & Consumable Fuels": {
        "description": "Oil Exploration, Refining, Gas Distribution, Coal",
        "stocks": [
            "RELIANCE.NS", "CASTROLIND.NS", "ONGC.NS", "BPCL.NS", "IOC.NS",
            "GAIL.NS", "HINDPETRO.NS", "PETRONET.NS", "IGL.NS", "MGL.NS",
            "GUJGASLTD.NS", "GSPL.NS", "ATGL.NS", "OIL.NS", "MRPL.NS",
            "CHENNPETRO.NS", "AEGISCHEM.NS", "GULFOILLUB.NS", "GANDHAR.NS", "HEMIPROP.NS",
            "SUPPETRO.NS", "SELAN.NS", "HINDOILEXP.NS", "HOEC.NS", "DEEPINDS.NS",
            "CAIRN.NS", "GEL.NS", "JCHAC.NS", "CPCL.NS", "HPCL.NS",
            "TIDEWATER.NS", "SEAMECLTD.NS", "GULFPETRO.NS", "MAHANAGAR.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 17. Real Estate
    # ─────────────────────────────────────────────
    "Real Estate": {
        "description": "Real Estate Developers, REITs, Property Management",
        "stocks": [
            "MAXESTATES.NS", "AARVINFRA.NS", "MAHLIFE.NS", "DLF.NS", "GODREJPROP.NS",
            "OBEROIRLTY.NS", "PRESTIGE.NS", "LODHA.NS", "PHOENIXLTD.NS", "BRIGADE.NS",
            "SOBHA.NS", "SUNTECK.NS", "KOLTEPATIL.NS", "ANANTRAJ.NS", "PURVA.NS",
            "EMBASSY.NS", "MINDSPACE.NS", "BIRET.NS", "RUSTOMJEE.NS", "SIGNATURE.NS",
            "KEYSTONE.NS", "SURAJEST.NS", "IBREALEST.NS", "ASHIANA.NS", "SHRIRAMPRP.NS",
            "AHLUCONT.NS", "ARIHANT.NS", "ELDEHSG.NS", "MAHINDLIFE.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 18. Retailing
    # ─────────────────────────────────────────────
    "Retailing": {
        "description": "Brick & Mortar Retail, E-commerce, Fashion Retail, Grocery",
        "stocks": [
            "KALYANKJIL.NS", "SENCO.NS", "ETHOS.NS", "METROBRAND.NS", "SHOPERSTOP.NS",
            "TRENT.NS", "DMART.NS", "NYKAA.NS", "KHADIM.NS", "GLOBUSSPR.NS",
            "SWIGGY.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 19. Services
    # ─────────────────────────────────────────────
    "Services": {
        "description": "Professional Services, Staffing, BPO, Consulting, Engineering Services",
        "stocks": [
            "BLUEDART.NS", "DELHIVERY.NS", "ALLCARGO.NS", "TCI.NS", "QUESS.NS",
            "TEAMLEASE.NS", "SIS.NS", "ICRA.NS", "CARERATING.NS", "BLS.NS",
            "CONCOR.NS", "BOROLTD.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 20. Telecommunication
    # ─────────────────────────────────────────────
    "Telecommunication": {
        "description": "Telecom Operators, Tower Companies, Telecom Infrastructure",
        "stocks": [
            "RAILTEL.NS", "VINDHYATEL.NS", "PARACABLES.NS", "NELCO.NS", "GTLINFRA.NS",
            "BHARTIARTL.NS", "IDEA.NS", "TTML.NS", "INDUSTOWER.NS", "TATACOMM.NS",
            "HFCL.NS", "STERLITE.NS", "GTL.NS", "TEJAS.NS", "ONMOBILE.NS",
            "XLERATE.NS", "CENTUM.NS", "NELCAST.NS", "ITI.NS", "MTNL.NS",
            "BSNL.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 21. Textiles
    # ─────────────────────────────────────────────
    "Textiles": {
        "description": "Textiles, Garments, Home Furnishings, Innerwear, Fabrics",
        "stocks": [
            "CENTURYTEX.NS", "TRIDENT.NS", "MIRZAINT.NS", "ARVIND.NS", "WELSPUNLIV.NS",
            "HIMATSEIDE.NS", "VTL.NS", "KPRMILL.NS", "GOKALDAS.NS", "KITEX.NS",
            "LUXIND.NS", "DOLLAR.NS", "RUPA.NS", "TCNSBRANDS.NS", "SSWL.NS",
            "SUTLEJ.NS", "DONEAR.NS", "SPENTEX.NS", "BANSWRAS.NS", "HIRECT.NS",
            "VARDHACRLC.NS", "GRAUER.NS", "NANDAN.NS", "NAHAR.NS", "SURYALAXMI.NS",
            "GARFIBRES.NS", "SUPER.NS", "SINTEX.NS", "METRO.NS", "VMART.NS",
            "INDORAMA.NS", "FILATEX.NS", "RAJTV.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 22. Utilities
    # ─────────────────────────────────────────────
    "Utilities": {
        "description": "Power Generation, Transmission, Distribution, Renewables, Water",
        "stocks": [
            "SUZLON.NS", "ADANIPOWER.NS", "NTPC.NS", "POWERGRID.NS", "TATAPOWER.NS",
            "NHPC.NS", "JSWENERGY.NS", "SJVN.NS", "TORNTPOWER.NS", "CESC.NS",
            "ADANIGREEN.NS", "INOXWIND.NS", "WAAREE.NS", "KPIGREEN.NS", "GIPCL.NS",
            "IREDA.NS", "POWERMECH.NS", "RPOWER.NS", "JPPOWER.NS", "VABIOTECH.NS",
            "IEX.NS", "NLCINDIA.NS", "KALPATPOWR.NS", "GENUS.NS", "HPL.NS",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════
#  FILTER REFERENCE -- one-place summary for review
# ═══════════════════════════════════════════════════════════════

FILTER_REFERENCE = {
    1: {
        "name": "Valuation",
        "max_points": 10,
        "source": "Damodaran, Graham, Mauboussin",
        "description": (
            "Sector-aware PE/PB scoring. PEG, EV/EBITDA, P/S ratios. "
            "Graham Number and company-specific DCF intrinsic value. "
            "Reverse DCF to check what growth the market implies. "
            "Margin of safety = how much below intrinsic value."
        ),
        "sub_components": [
            "PE vs sector norms (cheap/avg/expensive)",
            "PB vs sector norms",
            "PEG ratio (< 1 ideal)",
            "EV/EBITDA (< 8 ideal)",
            "P/S ratio (< 2 ideal)",
            "Margin of Safety (Graham Number)",
            "Reverse DCF implied growth vs actual growth",
        ],
    },
    2: {
        "name": "Profitability",
        "max_points": 10,
        "source": "Buffett, Greenblatt, Mukherjea",
        "description": (
            "How efficiently does the company convert capital into profit? "
            "ROE > 15% = good. ROCE > 20% = Buffett territory. "
            "Owner Earnings = Net Income + D&A - Maintenance CapEx."
        ),
        "sub_components": [
            "ROE (min 12%, excellent 25%)",
            "ROCE (min 15%, excellent 25%)",
            "ROA (min 5%, excellent 12%)",
            "Operating Margin (min 12%, excellent 25%)",
            "Net Margin (min 8%, excellent 20%)",
            "Owner Earnings yield",
        ],
    },
    3: {
        "name": "Growth Quality",
        "max_points": 10,
        "source": "Lynch, Srinivasan, Mukherjea (ROIIC)",
        "description": (
            "Revenue CAGR shows demand. Profit CAGR shows leverage. "
            "Incremental ROCE (ROIIC) = delta NOPAT / delta invested capital. "
            "A company with ROCE 20% but ROIIC 8% is running out of "
            "high-return reinvestment opportunities."
        ),
        "sub_components": [
            "Revenue CAGR 3yr (min 10%, excellent 20%)",
            "Profit CAGR 3yr (min 12%, excellent 25%)",
            "Incremental ROCE / ROIIC",
            "Quarterly profit direction (improving/mixed/declining)",
            "Earnings consistency (YoY volatility)",
        ],
    },
    4: {
        "name": "Financial Health",
        "max_points": 10,
        "source": "Altman, Graham, Marks",
        "description": (
            "Balance sheet fortress. Altman Z-Score predicts bankruptcy "
            "within 2 years. Low debt, high interest coverage, adequate liquidity."
        ),
        "sub_components": [
            "Altman Z-Score (> 2.99 safe, < 1.81 distress)",
            "Debt-to-Equity (< 1.0 ideal)",
            "Interest Coverage (> 3x good, > 6x excellent)",
            "Current Ratio (> 1.5 good)",
        ],
    },
    5: {
        "name": "Cash Flow",
        "max_points": 10,
        "source": "Greenblatt, Srinivasan, Buffett",
        "description": (
            "Cash is truth; earnings are opinion. FCF Conversion = FCF / NI. "
            "Must be > 80%. FCF yield = how cheap on a cash basis."
        ),
        "sub_components": [
            "Free Cash Flow positive (binary)",
            "FCF Conversion Ratio (FCF / Net Income)",
            "FCF Yield % (FCF / Market Cap)",
            "OCF / Net Income ratio",
            "CapEx intensity (CapEx / Revenue)",
        ],
    },
    6: {
        "name": "Business Moat",
        "max_points": 10,
        "source": "Dorsey (Morningstar), Buffett, Porter",
        "description": (
            "Sustainable competitive advantage. 7 moat types. "
            "Moat TREND: widening (rising ROCE + margins) vs "
            "eroding (declining ROCE + growing revenue = price war)."
        ),
        "sub_components": [
            "Number of moat types identified (0-7)",
            "ROCE strength (durability proxy)",
            "Operating margin strength (pricing power)",
            "Revenue growth (demand signal)",
            "Moat trend: widening / stable / eroding",
        ],
    },
    7: {
        "name": "Earnings Quality",
        "max_points": 10,
        "source": "Piotroski (Stanford), Beneish, Mukherjea",
        "description": (
            "Piotroski F-Score: 9 binary tests (0-9). Top scores "
            "outperform by 7.5% annually. Accrual Ratio = (NI - OCF) / TA. "
            "High accruals = paper earnings = manipulation risk."
        ),
        "sub_components": [
            "Piotroski F-Score (0-9)",
            "Accrual Ratio (lower is better, negative = quality)",
            "OCF > Net Income (cash backs earnings)",
            "Gross margin trend (improving = efficiency)",
        ],
    },
    8: {
        "name": "Institutional Backing",
        "max_points": 10,
        "source": "Lynch, Institutional theory",
        "description": (
            "Smart money validation. High institutional ownership = due "
            "diligence done. Analyst target = external valuation check."
        ),
        "sub_components": [
            "Institutional holding % (20-70% ideal)",
            "Insider holding % (> 10% = skin in the game)",
            "Analyst recommendation (buy/hold/sell)",
            "Analyst target vs current price (upside %)",
        ],
    },
    9: {
        "name": "Sector & Macro",
        "max_points": 10,
        "source": "Dalio (macro), Marathon AM (capital cycles)",
        "description": (
            "Structural tailwinds, disruption risk, diversification. "
            "Cyclicals get normalised PE. Capital cycle awareness."
        ),
        "sub_components": [
            "Sector tailwinds (policy, TAM, macro)",
            "Diversification (revenue mix, geographic spread)",
            "Future threats (disruption, regulation, competition)",
            "Company growth premium/discount vs sector",
            "Cyclicality adjustment",
        ],
    },
    10: {
        "name": "Management Quality",
        "max_points": 10,
        "source": "Buffett, Munger, Fisher",
        "description": (
            "Quantitative proxy for management quality. Capital "
            "allocation (ROCE), shareholder returns, financial "
            "discipline, margin trend, no dilution."
        ),
        "sub_components": [
            "ROCE consistency (capital allocation)",
            "Dividend payout ratio (15-60% ideal)",
            "Debt discipline (D/E low or declining)",
            "Margin trend (expanding/stable/contracting)",
            "Share dilution (shares outstanding trend)",
            "FCF positive (cash generative)",
        ],
    },
    11: {
        "name": "Red Flags (Binary Reject)",
        "max_points": 0,
        "source": "Altman, Graham, Piotroski, Mukherjea",
        "description": (
            "Binary kill-switches. A single red flag = uninvestable."
        ),
        "sub_components": [
            "PE > 60 (extreme overvaluation)",
            "D/E > 2.0 (overleveraged)",
            "Interest Coverage < 1.5x (debt stress)",
            "Profit declining 3+ consecutive quarters",
            "Negative free cash flow",
            "Market Cap < 500 Cr (micro-cap risk)",
            "Current year net loss",
            "Altman Z-Score < 1.81 (bankruptcy risk)",
            "Piotroski F-Score <= 2 (worst quality)",
            "Accrual Ratio > 25% (accounting fraud risk)",
        ],
    },
}
