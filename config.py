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
            "AJAXENGG.NS", "ALICON.NS", "APOLLOTYRE.NS", "ARE&M.NS", "ASAHIINDIA.NS",
            "ASAL.NS", "ASHOKLEY.NS", "ASKAUTOLTD.NS", "ATHERENERG.NS", "ATLASCYCLE.NS",
            "ATULAUTO.NS", "AUTOAXLES.NS", "AUTOIND.NS", "BAJAJ-AUTO.NS", "BALKRISIND.NS",
            "BANCOINDIA.NS", "BELRISE.NS", "BHARATFORG.NS", "BHARATGEAR.NS", "BHARATSE.NS",
            "BOSCHLTD.NS", "CARRARO.NS", "CEATLTD.NS", "CIEINDIA.NS", "CRAFTSMAN.NS",
            "DIVGIITTS.NS", "EICHERMOT.NS", "ELGIRUBCO.NS", "ENDURANCE.NS", "EXIDEIND.NS",
            "FIEMIND.NS", "FMGOETZE.NS", "FORCEMOT.NS", "GABRIEL.NS", "GNA.NS",
            "GRPLTD.NS", "HARRMALAYA.NS", "HEROMOTOCO.NS", "HINDCOMPOS.NS", "HITECHGEAR.NS",
            "HYUNDAI.NS", "IGARASHI.NS", "INDNIPPON.NS", "INDOFARM.NS", "JAMNAAUTO.NS",
            "JAYBARMARU.NS", "JBMA.NS", "JKTYRE.NS", "JMA.NS", "JTEKTINDIA.NS",
            "JTLIND.NS", "JWL.NS", "KROSS.NS", "LGBBROSLTD.NS", "LUMAXIND.NS",
            "LUMAXTECH.NS", "M&M.NS", "MARUTI.NS", "MENONBE.NS", "MINDACORP.NS",
            "MODIRUBBER.NS", "MOTHERSON.NS", "MRF.NS", "MSUMI.NS", "MUNJALAU.NS",
            "MUNJALSHOW.NS", "NDRAUTO.NS", "OLAELEC.NS", "OLECTRA.NS", "OMAXAUTO.NS",
            "PAVNAIND.NS", "PIXTRANS.NS", "PPAP.NS", "PRECAM.NS", "PRICOLLTD.NS",
            "PRITIKAUTO.NS", "RACLGEAR.NS", "REMSONSIND.NS", "RICOAUTO.NS", "RML.NS",
            "ROLEXRINGS.NS", "RUBFILA.NS", "SAMPANN.NS", "SANDHAR.NS", "SANSERA.NS",
            "SCHAEFFLER.NS", "SEDEMAC.NS", "SETCO.NS", "SHANTIGEAR.NS", "SHARDAMOTR.NS",
            "SHIVAMAUTO.NS", "SHRIPISTON.NS", "SINTERCOM.NS", "SJS.NS", "SKFINDIA.NS",
            "SMLMAH.NS", "SONACOMS.NS", "STERTOOLS.NS", "STUDDS.NS", "SUBROS.NS",
            "SUNCLAY.NS", "SUNDRMBRAK.NS", "SUNDRMFAST.NS", "SUPRAJIT.NS", "SWARAJENG.NS",
            "TALBROAUTO.NS", "TENNIND.NS", "TIINDIA.NS", "TIMKEN.NS", "TMCV.NS",
            "TMPV.NS", "TOLINS.NS", "TVSHLTD.NS", "TVSMOTOR.NS", "TVSSRICHAK.NS",
            "UCAL.NS", "UNOMINDA.NS", "URAVIDEF.NS", "VARROC.NS", "VSTTILLERS.NS",
            "WHEELS.NS", "ZFCVINDIA.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 2. Capital Goods
    # ─────────────────────────────────────────────
    "Capital Goods": {
        "description": "Engineering, Defence, Railways, Electricals, Shipbuilding, Industrial Machinery",
        "stocks": [
            "A2ZINFRA.NS", "AARON.NS", "AARTECH.NS", "ABB.NS", "ABINFRA.NS",
            "ACE.NS", "ACL.NS", "ADOR.NS", "AEQUS.NS", "AFCONS.NS",
            "AFFORDABLE.NS", "AIAENG.NS", "AKASH.NS", "ANUP.NS", "APCL.NS",
            "APOLLO.NS", "ARIS.NS", "AROGRANITE.NS", "ARROWGREEN.NS", "ASHOKA.NS",
            "ASTRAMICRO.NS", "ATAM.NS", "ATLANTAA.NS", "ATLANTAELE.NS", "AVALON.NS",
            "AVROIND.NS", "AXISCADES.NS", "AZAD.NS", "BAJAJINDEF.NS", "BAJEL.NS",
            "BALUFORGE.NS", "BDL.NS", "BEL.NS", "BEML.NS", "BHEL.NS",
            "BIGBLOC.NS", "BIRLACORPN.NS", "BIRLANU.NS", "BLKASHYAP.NS", "BRNL.NS",
            "BUILDPRO.NS", "BVCL.NS", "CAPACITE.NS", "CCCL.NS", "CEIGALL.NS",
            "CEMPRO.NS", "CGPOWER.NS", "COCHINSHIP.NS", "CUMMINSIND.NS", "DBEIL.NS",
            "DBL.NS", "DCM.NS", "DCMSIL.NS", "DCXINDIA.NS", "DDEVPLSTIK.NS",
            "DECCANCE.NS", "DEEDEV.NS", "DELTAMAGNT.NS", "DENORA.NS", "DIFFNKG.NS",
            "DUCON.NS", "DYNAMATECH.NS", "EIMCOELECO.NS", "EKC.NS", "ELECON.NS",
            "ELGIEQUIP.NS", "ELLEN.NS", "ENGINERSIN.NS", "EPACKPEB.NS", "ESABINDIA.NS",
            "ESCORTS.NS", "FINPIPE.NS", "GALAPREC.NS", "GANGAFORGE.NS", "GARUDA.NS",
            "GAYAHWS.NS", "GAYAPROJ.NS", "GKENERGY.NS", "GLOBECIVIL.NS", "GMMPFAUDLR.NS",
            "GMRAIRPORT.NS", "GPPL.NS", "GPTINFRA.NS", "GRAPHITE.NS", "GRINFRA.NS",
            "GRSE.NS", "GUJAPOLLO.NS", "GVKPIL.NS", "GVPIL.NS", "GVT&D.NS",
            "HAL.NS", "HAPPYFORGE.NS", "HARSHA.NS", "HCC.NS", "HECPROJECT.NS",
            "HEG.NS", "HGINFRA.NS", "HILINFRA.NS", "HILTON.NS", "HMT.NS",
            "HONDAPOWER.NS", "HUDCO.NS", "ICEMAKE.NS", "IDEAFORGE.NS", "IFGLEXPOR.NS",
            "IL&FSENGG.NS", "IL&FSTRANS.NS", "INDIANHUME.NS", "INDOTECH.NS", "INOXINDIA.NS",
            "INTERARCH.NS", "INTLCONV.NS", "IRB.NS", "IRCON.NS", "ISGEC.NS",
            "JAICORPLTD.NS", "JAYKAY.NS", "JINDALPHOT.NS", "JISLDVREQS.NS", "JISLJALEQS.NS",
            "JNKINDIA.NS", "JSWCEMENT.NS", "JSWINFRA.NS", "JYOTICNC.NS", "JYOTISTRUC.NS",
            "KABRAEXTRU.NS", "KAKATCEM.NS", "KALYANIFRG.NS", "KAUSHALYA.NS", "KAYNES.NS",
            "KCP.NS", "KEC.NS", "KINGFA.NS", "KIRLOSBROS.NS", "KIRLOSIND.NS",
            "KIRLPNU.NS", "KNRCON.NS", "KPIL.NS", "KRIDHANINF.NS", "KRISHNADEF.NS",
            "KRITI.NS", "KSB.NS", "KSHINTL.NS", "LATTEYS.NS", "LIKHITHA.NS",
            "LINDEINDIA.NS", "LLOYDSENGG.NS", "LMW.NS", "LOKESHMACH.NS", "LT.NS",
            "MACPOWER.NS", "MADHAV.NS", "MADHUCON.NS", "MAHEPC.NS", "MAMATA.NS",
            "MANGLMCEM.NS", "MANINFRA.NS", "MANUGRAPH.NS", "MARKOLINES.NS", "MAZDA.NS",
            "MAZDOCK.NS", "MBLINFRA.NS", "MEIL.NS", "MEP.NS", "MHLXMIRU.NS",
            "MIDWESTLTD.NS", "MMFL.NS", "MOLDTECH.NS", "NAHARPOLY.NS", "NBCC.NS",
            "NCC.NS", "NCLIND.NS", "NIBE.NS", "NIBL.NS", "NIRAJ.NS",
            "NOIDATOLL.NS", "NRBBEARING.NS", "OMINFRAL.NS", "OMNI.NS", "ORIENTALTL.NS",
            "ORIENTCER.NS", "OSWALPUMPS.NS", "PARAS.NS", "PASUPTAC.NS", "PATELENG.NS",
            "PEARLPOLY.NS", "PIGL.NS", "PILITA.NS", "PNC.NS", "PNCINFRA.NS",
            "POKARNA.NS", "POWERINDIA.NS", "PPL.NS", "PRAJIND.NS", "PRECWIRE.NS",
            "PREMEXPLN.NS", "PREMIER.NS", "PREMIERPOL.NS", "PTCIL.NS", "QPOWER.NS",
            "RAJOOENG.NS", "RAMCOIND.NS", "RAMKY.NS", "REFEX.NS", "RHIM.NS",
            "RIIL.NS", "RITES.NS", "RKEC.NS", "RKFORGE.NS", "RMDRIP.NS",
            "ROSSELLIND.NS", "ROSSTECH.NS", "ROTO.NS", "RPEL.NS", "RPPINFRA.NS",
            "RVNL.NS", "RVTH.NS", "SADBHAV.NS", "SADBHIN.NS", "SAHYADRI.NS",
            "SALASAR.NS", "SANCO.NS", "SAURASHCEM.NS", "SBCL.NS", "SCHNEIDER.NS",
            "SEJALLTD.NS", "SEPC.NS", "SETL.NS", "SGIL.NS", "SHAKTIPUMP.NS",
            "SHREDIGCEM.NS", "SIEMENS.NS", "SIGIND.NS", "SIMPLEXINF.NS", "SKFINDUS.NS",
            "SKIPPER.NS", "SOLARINDS.NS", "SOMICONVEY.NS", "SPMLINFRA.NS", "SRM.NS",
            "STARCEMENT.NS", "SUPREMEINF.NS", "SWELECTES.NS", "SWSOLAR.NS", "TAINWALCHM.NS",
            "TARAPUR.NS", "TARIL.NS", "TARMAT.NS", "TDPOWERSYS.NS", "TEXMOPIPES.NS",
            "TEXRAIL.NS", "THEJO.NS", "THERMAX.NS", "TICL.NS", "TIJARIA.NS",
            "TIMETECHNO.NS", "TIRUPATIFL.NS", "TITAGARH.NS", "TOKYOPLAST.NS", "TPHQ.NS",
            "TPLPLASTEH.NS", "TRANSRAILL.NS", "TRF.NS", "TRITURBINE.NS", "UEL.NS",
            "UNIDT.NS", "UNIMECH.NS", "UNIVASTU.NS", "UNIVPHOTO.NS", "URJA.NS",
            "USK.NS", "VASCONEQ.NS", "VIKRAN.NS", "VISAKAIND.NS", "VOLTAMP.NS",
            "VPRPL.NS", "WALCHANNAG.NS", "WELENT.NS", "WENDT.NS", "WINDMACHIN.NS",
            "WSI.NS", "YUKEN.NS", "ZENTEC.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 3. Chemicals
    # ─────────────────────────────────────────────
    "Chemicals": {
        "description": "Specialty Chemicals, Agrochemicals, Polymers, Paints",
        "stocks": [
            "AARTIIND.NS", "AARTISURF.NS", "ACI.NS", "ADVANCE.NS", "AETHER.NS",
            "AGARIND.NS", "AKSHARCHEM.NS", "ALKALI.NS", "ALKYLAMINE.NS", "AMNPLST.NS",
            "ANDHRSUGAR.NS", "ANURAS.NS", "APCOTEXIND.NS", "ARIES.NS", "ARVEE.NS",
            "ASAHISONG.NS", "ASIANPAINT.NS", "ATUL.NS", "BALAMINES.NS", "BASF.NS",
            "BEPL.NS", "BERGEPAINT.NS", "BESTAGRO.NS", "BHAGCHEM.NS", "BHAGERIA.NS",
            "BODALCHEM.NS", "CAMLINFINE.NS", "CHEMBOND.NS", "CHEMBONDCH.NS", "CHEMCON.NS",
            "CHEMFAB.NS", "CHEMPLASTS.NS", "CLEAN.NS", "DCW.NS", "DEEPAKNTR.NS",
            "DHARMAJ.NS", "DIAMINESQ.NS", "DICIND.NS", "DMCC.NS", "DSFCL.NS",
            "DYNPRO.NS", "EPIGRAL.NS", "EXCELINDUS.NS", "FAIRCHEMOR.NS", "FCL.NS",
            "FINEORG.NS", "FISCHER.NS", "FLUOROCHEM.NS", "FOSECOIND.NS", "GALAXYSURF.NS",
            "GANESHBE.NS", "GEMAROMA.NS", "GHCL.NS", "GODAVARIB.NS", "GODREJIND.NS",
            "GUJALKALI.NS", "GULPOLY.NS", "HERANBA.NS", "HINDCON.NS", "HPAL.NS",
            "HPIL.NS", "HSCL.NS", "IGCL.NS", "IGPL.NS", "INDIAGLYCO.NS",
            "INDOAMIN.NS", "INDOBORAX.NS", "IONEXCHANG.NS", "IPL.NS", "ISHANCH.NS",
            "IVP.NS", "JGCHEM.NS", "JOCIL.NS", "JUBLINGREA.NS", "KANORICHEM.NS",
            "KANSAINER.NS", "KIRIINDUS.NS", "KOTHARIPET.NS", "KRONOX.NS", "LORDSCHLO.NS",
            "LXCHEM.NS", "MANALIPETC.NS", "MANORG.NS", "MOL.NS", "NACLIND.NS",
            "NAVINFLUOR.NS", "NEOGEN.NS", "NOCIL.NS", "OAL.NS", "OCCLLTD.NS",
            "ORIENTCEM.NS", "PAUSHAKLTD.NS", "PIDILITIND.NS", "PIIND.NS", "PLASTIBLEN.NS",
            "PLATIND.NS", "PODDARMENT.NS", "PRIMO.NS", "PRIVISCL.NS", "PUNJABCHEM.NS",
            "RALLIS.NS", "ROSSARI.NS", "SADHNANIQ.NS", "SANGINITA.NS", "SEYAIND.NS",
            "SHIVALIK.NS", "SHREEPUSHK.NS", "SPLPETRO.NS", "SRF.NS", "STALLION.NS",
            "STYRENIX.NS", "SUDARCOLOR.NS", "SUDARSCHEM.NS", "SUMICHEM.NS", "TATACHEM.NS",
            "TATVA.NS", "TECILCHEM.NS", "TINNARUBR.NS", "TIRUMALCHM.NS", "TNPETRO.NS",
            "UPL.NS", "VALIANTORG.NS", "VIDHIING.NS", "VIKASECO.NS", "VINATIORGA.NS",
            "VISHNU.NS", "VITAL.NS", "YASHO.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 4. Construction Materials
    # ─────────────────────────────────────────────
    "Construction Materials": {
        "description": "Cement, Building Materials, Pipes, Ceramics",
        "stocks": [
            "ACC.NS", "AMBUJACEM.NS", "CERA.NS", "DALBHARAT.NS", "HEIDELBERG.NS",
            "HINDWAREAP.NS", "INDIACEM.NS", "JKCEMENT.NS", "JKIL.NS", "JKLAKSHMI.NS",
            "KAJARIACER.NS", "KESORAMIND.NS", "NUVOCO.NS", "ORIENTBELL.NS", "RAMCOCEM.NS",
            "SAGCEM.NS", "SHREECEM.NS", "SRHHYPOLTD.NS", "ULTRACEMCO.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 5. Consumer Durables
    # ─────────────────────────────────────────────
    "Consumer Durables": {
        "description": "Electronics, Appliances, Jewellery, Watches, Lighting",
        "stocks": [
            "ADVAIT.NS", "ALLTIME.NS", "AMBER.NS", "AMBICAAGAR.NS", "APARINDS.NS",
            "ASIANTILES.NS", "AURIGROW.NS", "BAJAJCON.NS", "BAJAJELEC.NS", "BATAINDIA.NS",
            "BBL.NS", "BLUESTARCO.NS", "BORORENEW.NS", "BOSCH-HCIL.NS", "BPL.NS",
            "BUTTERFLY.NS", "CAMPUS.NS", "CARYSIL.NS", "CELLO.NS", "CORDSCABLE.NS",
            "CROMPTON.NS", "DIACABS.NS", "DIXON.NS", "DOMS.NS", "DYCL.NS",
            "ELIN.NS", "EMMVEE.NS", "EPACK.NS", "EUREKAFORB.NS", "EVEREADY.NS",
            "EXXARO.NS", "FINCABLES.NS", "FOCUS.NS", "GENUSPOWER.NS", "HARDWYN.NS",
            "HAVELLS.NS", "HBLENGINE.NS", "HONAUT.NS", "IFBIND.NS", "IKIO.NS",
            "INDIGOPNTS.NS", "KAMOPAINTS.NS", "KECL.NS", "KEI.NS", "KHAITANLTD.NS",
            "LAOPALA.NS", "LEXUS.NS", "LGEINDIA.NS", "MANYAVAR.NS", "MIRCELECTR.NS",
            "MODISONLTD.NS", "MURUDCERA.NS", "NIPPOBATRY.NS", "NITCO.NS", "NITIRAJ.NS",
            "ORIENTELEC.NS", "PAGEIND.NS", "PGEL.NS", "PITTIENG.NS", "PLAZACABLE.NS",
            "POLYCAB.NS", "PREMIERENE.NS", "PROSTARM.NS", "QUADFUTURE.NS", "RAMRAT.NS",
            "RAYMOND.NS", "REGENCERAM.NS", "RELAXO.NS", "RISHABH.NS", "RRKABEL.NS",
            "S&SPOWER.NS", "SAATVIKGL.NS", "SAFARI.NS", "SALZERELEC.NS", "SERVOTECH.NS",
            "SHALPAINTS.NS", "SHILCTECH.NS", "SIRCA.NS", "SOLEX.NS", "SOMANYCERA.NS",
            "SONAMLTD.NS", "SPECTRUM.NS", "STOVEKRAFT.NS", "SYMPHONY.NS", "SYRMA.NS",
            "TITAN.NS", "TTKPRESTIG.NS", "UNIVCABLES.NS", "UTLSOLAR.NS", "VETO.NS",
            "VGUARD.NS", "VIDYAWIRES.NS", "VIKRAMSOLR.NS", "VIPIND.NS", "VOLTAS.NS",
            "WAAREEENER.NS", "WAAREEINDO.NS", "WEBELSOLAR.NS", "WEL.NS", "WHIRLPOOL.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 6. Consumer Services
    # ─────────────────────────────────────────────
    "Consumer Services": {
        "description": "Hotels, Restaurants, Tourism, QSR, Education, E-commerce",
        "stocks": [
            "AARVI.NS", "ADVANIHOTR.NS", "ADVENTHTL.NS", "AHLEAST.NS", "AIROLAM.NS",
            "APOLSINHOT.NS", "ASIANHOTNR.NS", "AWFIS.NS", "BLUECOAST.NS", "BRIGHOTEL.NS",
            "BYKE.NS", "CARTRADE.NS", "CCHHL.NS", "CHALET.NS", "CLEDUCATE.NS",
            "COFFEEDAY.NS", "CPCAP.NS", "CPEDU.NS", "CRIZAC.NS", "DELTACORP.NS",
            "DEVX.NS", "DEVYANI.NS", "DREAMFOLKS.NS", "EASEMYTRIP.NS", "EIHAHOTELS.NS",
            "EIHOTEL.NS", "EUROPRATIK.NS", "GLOBAL.NS", "GREENLAM.NS", "GSLSU.NS",
            "HAVISHA.NS", "HLVLTD.NS", "IMAGICAA.NS", "INDHOTEL.NS", "INDIGO.NS",
            "INDIQUBE.NS", "IRCTC.NS", "ITCHOTELS.NS", "ITDC.NS", "IXIGO.NS",
            "JARO.NS", "JUBLFOOD.NS", "JUNIPER.NS", "JUSTDIAL.NS", "KAMATHOTEL.NS",
            "KAYA.NS", "KEEPLEARN.NS", "LCCINFOTEC.NS", "LEMONTREE.NS", "MAHSEAMLES.NS",
            "MHRIL.NS", "MTEDUCARE.NS", "NAUKRI.NS", "NAVNETEDUL.NS", "NIITMTS.NS",
            "ORIENTHOT.NS", "PARKHOTELS.NS", "PRITI.NS", "PVRINOX.NS", "PWL.NS",
            "RBA.NS", "RESPONIND.NS", "RHL.NS", "ROHLTD.NS", "SAMHI.NS",
            "SAPPHIRE.NS", "SFL.NS", "SINCLAIR.NS", "SMARTWORKS.NS", "SPECIALITY.NS",
            "STANLEY.NS", "TAJGVK.NS", "TBOTEK.NS", "TGBHOTELS.NS", "THELEELA.NS",
            "THOMASCOOK.NS", "TOUCHWOOD.NS", "TRAVELFOOD.NS", "TREEHOUSE.NS", "UFBL.NS",
            "UMESLTD.NS", "URBANCO.NS", "VENTIVE.NS", "VHLTD.NS", "WAKEFIT.NS",
            "WESTLIFE.NS", "WEWORK.NS", "WONDERLA.NS", "YATRA.NS", "ZEELEARN.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 7. Diversified
    # ─────────────────────────────────────────────
    "Diversified": {
        "description": "Diversified Conglomerates, Multi-sector Holdings",
        "stocks": [
            "3MINDIA.NS", "AARTIDRUGS.NS", "ADANIENT.NS", "ANIKINDS.NS", "BAJAJHLDNG.NS",
            "BALMLAWRIE.NS", "BFINVEST.NS", "BHARATRAS.NS", "CHOLAHLDNG.NS", "DCMSHRIRAM.NS",
            "EDELWEISS.NS", "EVERESTIND.NS", "GFLLIMITED.NS", "GRASIM.NS", "GREAVESCOT.NS",
            "INGERRAND.NS", "JMFINANCIL.NS", "KIRLOSENG.NS", "MAXIND.NS", "PILANIINVS.NS",
            "RANEHOLDIN.NS", "RPSGVENT.NS", "SINDHUTRAD.NS", "STEL.NS", "TATAINVEST.NS",
            "TTKHLTCARE.NS", "TVSSCS.NS", "WOCKPHARMA.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 8. Fast Moving Consumer Goods
    # ─────────────────────────────────────────────
    "Fast Moving Consumer Goods": {
        "description": "Food, Beverages, Personal Care, Household Products",
        "stocks": [
            "ABDL.NS", "ADFFOODS.NS", "AGRITECH.NS", "AJOONI.NS", "APEX.NS",
            "APLLTD.NS", "ASALCBR.NS", "ASPINWALL.NS", "AVADHSUGAR.NS", "AVANTIFEED.NS",
            "AVTNPL.NS", "AWL.NS", "BAJAJHIND.NS", "BALRAMCHIN.NS", "BANARISUG.NS",
            "BBTC.NS", "BCLIND.NS", "BCONCEPTS.NS", "BECTORFOOD.NS", "BIKAJI.NS",
            "BRITANNIA.NS", "BSHSL.NS", "CCL.NS", "CLSEL.NS", "COASTCORP.NS",
            "COLPAL.NS", "CUPID.NS", "DABUR.NS", "DALMIASUG.NS", "DANGEE.NS",
            "DAVANGERE.NS", "DBOL.NS", "DCMSRIND.NS", "DIAMONDYD.NS", "DODLA.NS",
            "DTIL.NS", "DWARKESH.NS", "EIDPARRY.NS", "EIFFL.NS", "EMAMILTD.NS",
            "FOODSIN.NS", "GAEL.NS", "GANESHCP.NS", "GANGESSECU.NS", "GILLANDERS.NS",
            "GILLETTE.NS", "GMBREW.NS", "GODFRYPHLP.NS", "GODREJCP.NS", "GOKUL.NS",
            "GOKULAGRO.NS", "GOPAL.NS", "GRMOVER.NS", "GROBTEA.NS", "HALDER.NS",
            "HATSUN.NS", "HERITGFOOD.NS", "HINDUNILVR.NS", "HMAAGRO.NS", "HNDFDS.NS",
            "HONASA.NS", "IFBAGRO.NS", "INDOUS.NS", "ITC.NS", "JAYAGROGN.NS",
            "JAYSREETEA.NS", "JHS.NS", "JUBLCPL.NS", "JUBLPHARMA.NS", "JYOTHYLAB.NS",
            "KCPSUGIND.NS", "KMSUGAR.NS", "KNAGRI.NS", "KOHINOOR.NS", "KOTARISUG.NS",
            "KRBL.NS", "KRISHIVAL.NS", "KRITINUT.NS", "KWIL.NS", "LTFOODS.NS",
            "MAGADSUGAR.NS", "MANORAMA.NS", "MARICO.NS", "MAWANASUG.NS", "MCLEODRUSS.NS",
            "MEGASTAR.NS", "MGEL.NS", "MKPL.NS", "MODINATUR.NS", "MUKKA.NS",
            "NARMADA.NS", "NATHBIOGEN.NS", "NESTLEIND.NS", "NGIL.NS", "NKIND.NS",
            "NORBTEAEXP.NS", "ORKLAINDIA.NS", "OSWALSEEDS.NS", "PARAGMILK.NS", "PATANJALI.NS",
            "PGHH.NS", "PICCADIL.NS", "PKTEA.NS", "PONNIERODE.NS", "PRUDMOULI.NS",
            "RADICO.NS", "RAJESHEXPO.NS", "RAJSREESUG.NS", "RANASUG.NS", "REGAAL.NS",
            "RENUKA.NS", "RKDL.NS", "ROML.NS", "SAKHTISUG.NS", "SANSTAR.NS",
            "SANWARIA.NS", "SARVESHWAR.NS", "SCPL.NS", "SDBL.NS", "SHANTI.NS",
            "SHK.NS", "SKMEGGPROD.NS", "SUKHJITS.NS", "SULA.NS", "SUNDROP.NS",
            "TASTYBITE.NS", "TATACONSUM.NS", "TI.NS", "TRIVENI.NS", "TRUALT.NS",
            "UBL.NS", "UFLEX.NS", "UGARSUGAR.NS", "UNITDSPR.NS", "UNITEDTEA.NS",
            "UTTAMSUGAR.NS", "VADILALIND.NS", "VBL.NS", "VENKEYS.NS", "VISHWARAJ.NS",
            "VSTIND.NS", "ZYDUSWELL.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 9. Fertilizers & Agrochemicals
    # ─────────────────────────────────────────────
    "Fertilizers & Agrochemicals": {
        "description": "Fertilizers, Crop Protection, Seeds, Agrochemicals",
        "stocks": [
            "ADVENZYMES.NS", "AGROPHOS.NS", "ASTEC.NS", "BAYERCROP.NS", "BOHRAIND.NS",
            "CHAMBLFERT.NS", "COROMANDEL.NS", "DEEPAKFERT.NS", "DHAMPURSUG.NS", "DHANUKA.NS",
            "FACT.NS", "GNFC.NS", "GODREJAGRO.NS", "GSFC.NS", "INSECTICID.NS",
            "KHAICHEM.NS", "KRISHANA.NS", "KSCL.NS", "MADRASFERT.NS", "MBAPL.NS",
            "NAGAFERT.NS", "NATCOPHARM.NS", "NFL.NS", "NOVAAGRI.NS", "PARADEEP.NS",
            "RAMAPHO.NS", "RCF.NS", "SHARDACROP.NS", "SIKKO.NS", "SPIC.NS",
            "ZUARI.NS", "ZUARIIND.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 10. Financial Services
    # ─────────────────────────────────────────────
    "Financial Services": {
        "description": "Banks, NBFCs, Insurance, AMCs, Brokerages, Exchanges",
        "stocks": [
            "21STCENMGM.NS", "360ONE.NS", "5PAISA.NS", "AADHARHFC.NS", "AAVAS.NS",
            "ABCAPITAL.NS", "ABSLAMC.NS", "AFIL.NS", "AFSL.NS", "AIIL.NS",
            "ALGOQUANT.NS", "ALMONDZ.NS", "ANANDRATHI.NS", "ANGELONE.NS", "APTUS.NS",
            "ARIHANTCAP.NS", "ARMANFIN.NS", "ARSSBL.NS", "AUBANK.NS", "AVONMORE.NS",
            "AXISBANK.NS", "AYE.NS", "BAIDFIN.NS", "BAJAJFINSV.NS", "BAJAJHFL.NS",
            "BAJFINANCE.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BANKINDIA.NS", "BIRLAMONEY.NS",
            "BLBLIMITED.NS", "BLUECHIP.NS", "BSE.NS", "CANBK.NS", "CANFINHOME.NS",
            "CANHLIFE.NS", "CAPITALSFB.NS", "CAPTRUST.NS", "CDSL.NS", "CENTRALBK.NS",
            "CENTRUM.NS", "CGCL.NS", "CHOICEIN.NS", "CHOLAFIN.NS", "CIFL.NS",
            "CONSOFINVT.NS", "CORALFINAC.NS", "CRAMC.NS", "CREDITACC.NS", "CREST.NS",
            "CRISIL.NS", "CSBBANK.NS", "CSLFINANCE.NS", "CUB.NS", "DAMCAPITAL.NS",
            "DBSTOCKBRO.NS", "DCBBANK.NS", "DCMFINSERV.NS", "DELPHIFX.NS", "DHANBANK.NS",
            "DHUNINV.NS", "DOLATALGO.NS", "DVL.NS", "EMKAY.NS", "EQUITASBNK.NS",
            "ESAFSFB.NS", "FEDERALBNK.NS", "FEDFINA.NS", "FINKURVE.NS", "FINOPB.NS",
            "FIVESTAR.NS", "FUSION.NS", "GATECH.NS", "GCSL.NS", "GEOJITFSL.NS",
            "GICHSGFIN.NS", "GICRE.NS", "GKWLIMITED.NS", "GLFL.NS", "GODIGIT.NS",
            "GROWW.NS", "HBSL.NS", "HDBFS.NS", "HDFCAMC.NS", "HDFCBANK.NS",
            "HDFCLIFE.NS", "HEXATRADEX.NS", "HOMEFIRST.NS", "HYBRIDFIN.NS", "ICDSLTD.NS",
            "ICICIAMC.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "IDBI.NS",
            "IDFCFIRSTB.NS", "IFCI.NS", "IIFL.NS", "IIFLCAPS.NS", "IITL.NS",
            "INDBANK.NS", "INDIANB.NS", "INDIASHLTR.NS", "INDOSTAR.NS", "INDOTHAI.NS",
            "INDUSINDBK.NS", "INVENTURE.NS", "IOB.NS", "IRFC.NS", "IVC.NS",
            "J&KBANK.NS", "JIOFIN.NS", "JPOLYINVST.NS", "JSFB.NS", "KARURVYSYA.NS",
            "KEYFINSERV.NS", "KFINTECH.NS", "KHANDSE.NS", "KOTAKBANK.NS", "KTKBANK.NS",
            "LAXMIINDIA.NS", "LFIC.NS", "LICHSGFIN.NS", "LICI.NS", "LTF.NS",
            "M&MFIN.NS", "MAHABANK.NS", "MAHAPEXLTD.NS", "MANAPPURAM.NS", "MANBA.NS",
            "MANCREDIT.NS", "MASFIN.NS", "MASKINVEST.NS", "MASTERTR.NS", "MCX.NS",
            "MFSL.NS", "MONARCH.NS", "MONEYBOXX.NS", "MOTILALOFS.NS", "MOTOGENFIN.NS",
            "MUFIN.NS", "MUTHOOTCAP.NS", "MUTHOOTFIN.NS", "MUTHOOTMF.NS", "NAM-INDIA.NS",
            "NBIFIN.NS", "NDGL.NS", "NIACL.NS", "NIVABUPA.NS", "NORTHARC.NS",
            "NSIL.NS", "NUVAMA.NS", "ONELIFECAP.NS", "OSWALGREEN.NS", "PAISALO.NS",
            "PALASHSECU.NS", "PAYTM.NS", "PFC.NS", "PFS.NS", "PIRAMALFIN.NS",
            "PNB.NS", "PNBGILTS.NS", "PNBHOUSING.NS", "POLICYBZR.NS", "POONAWALLA.NS",
            "PRIMESECU.NS", "PRUDENT.NS", "PSB.NS", "RADIANTCMS.NS", "RBLBANK.NS",
            "RECLTD.NS", "RELIGARE.NS", "REPCOHOME.NS", "RHFL.NS", "SAMMAANCAP.NS",
            "SATIN.NS", "SBFC.NS", "SBICARD.NS", "SBILIFE.NS", "SBIN.NS",
            "SGFIN.NS", "SHAREINDIA.NS", "SHRIRAMFIN.NS", "SILINV.NS", "SMCGLOBAL.NS",
            "SOUTHBANK.NS", "SPANDANA.NS", "SRGHFL.NS", "STARHEALTH.NS", "STARTECK.NS",
            "STEELCITY.NS", "SUNDARMFIN.NS", "SURYODAY.NS", "SUVIDHAA.NS", "SYSTMTXC.NS",
            "TATACAP.NS", "TCIFINANCE.NS", "TEAMGTY.NS", "TFCILTD.NS", "TFL.NS",
            "THEINVEST.NS", "TMB.NS", "TRU.NS", "UCOBANK.NS", "UGROCAP.NS",
            "UJJIVANSFB.NS", "UNIONBANK.NS", "UTIAMC.NS", "UTKARSHBNK.NS", "UYFINCORP.NS",
            "VHL.NS", "VIJIFIN.NS", "VLSFINANCE.NS", "WEALTH.NS", "WELINV.NS",
            "WILLAMAGOR.NS", "YESBANK.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 11. Forest Materials
    # ─────────────────────────────────────────────
    "Forest Materials": {
        "description": "Paper, Packaging, Wood Products, Pulp",
        "stocks": [
            "ADL.NS", "AGI.NS", "APOLLOPIPE.NS", "ARCHIDPLY.NS", "ASTRAL.NS",
            "BALKRISHNA.NS", "CARBORUNIV.NS", "CENTURYPLY.NS", "CHEVIOT.NS", "EMAMIPAP.NS",
            "EPL.NS", "ESTER.NS", "GLOSTERLTD.NS", "GPIL.NS", "GREENPANEL.NS",
            "GREENPLY.NS", "GRINDWELL.NS", "HUHTAMAKI.NS", "JINDALPOLY.NS", "JKPAPER.NS",
            "MONTECARLO.NS", "NILKAMAL.NS", "ORIENTPPR.NS", "PRINCEPIPE.NS", "PSPPROJECT.NS",
            "RITCO.NS", "RUCHIRA.NS", "RUSHIL.NS", "SATIA.NS", "SESHAPAPER.NS",
            "SHAILY.NS", "STARPAPER.NS", "STYLAMIND.NS", "SUPREMEIND.NS", "TARSONS.NS",
            "TCPLPACK.NS", "TNPL.NS", "VESUVIUS.NS", "WIPL.NS", "WSTCSTPAPR.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 12. Healthcare
    # ─────────────────────────────────────────────
    "Healthcare": {
        "description": "Pharmaceuticals, Hospitals, Diagnostics, API, Medical Devices",
        "stocks": [
            "AAREYDRUGS.NS", "AARTIPHARM.NS", "ABBOTINDIA.NS", "ACUTAAS.NS", "AGARWALEYE.NS",
            "AHCL.NS", "AJANTPHARM.NS", "AKUMS.NS", "ALBERTDAVD.NS", "ALEMBICLTD.NS",
            "ALIVUS.NS", "ALKEM.NS", "ALPA.NS", "AMANTA.NS", "AMRUTANJAN.NS",
            "ANTHEM.NS", "ANUHPHR.NS", "APOLLOHOSP.NS", "ARTEMISMED.NS", "ASTERDM.NS",
            "ASTRAZEN.NS", "AUROPHARMA.NS", "BAFNAPH.NS", "BAJAJHCARE.NS", "BALAXI.NS",
            "BALPHARMA.NS", "BETA.NS", "BIOCON.NS", "BIOFILCHEM.NS", "BLISSGVS.NS",
            "BLUEJET.NS", "BROOKS.NS", "CAPLIPOINT.NS", "CIPLA.NS", "COHANCE.NS",
            "CONCORDBIO.NS", "CORONA.NS", "DCAL.NS", "DIVISLAB.NS", "DRREDDY.NS",
            "EMCURE.NS", "ENTERO.NS", "ERIS.NS", "FDC.NS", "FORTIS.NS",
            "GKSL.NS", "GLAND.NS", "GLAXO.NS", "GLENMARK.NS", "GPTHEALTH.NS",
            "GRANULES.NS", "GUFICBIO.NS", "GUJTHEM.NS", "HALEOSLABS.NS", "HCG.NS",
            "HESTERBIO.NS", "HIKAL.NS", "IKS.NS", "INDGN.NS", "INDOCO.NS",
            "INDRAMEDCO.NS", "INDSWFTLAB.NS", "INNOVACAP.NS", "IOLCP.NS", "IPCALAB.NS",
            "JAGSNPHARM.NS", "JBCHEPHARM.NS", "JLHL.NS", "JSLL.NS", "KILITCH.NS",
            "KIMS.NS", "KOPRAN.NS", "KREBSBIO.NS", "KRSNAA.NS", "LALPATHLAB.NS",
            "LASA.NS", "LAURUSLABS.NS", "LAXMIDENTL.NS", "LINCOLN.NS", "LOTUSEYE.NS",
            "LUPIN.NS", "LYKALABS.NS", "MANGALAM.NS", "MANKIND.NS", "MARKSANS.NS",
            "MAXHEALTH.NS", "MEDANTA.NS", "MEDIASSIST.NS", "MEDICAMEQ.NS", "MEDICO.NS",
            "MEDPLUS.NS", "METROPOLIS.NS", "MOREPENLAB.NS", "NATCAPSUQ.NS", "NECLIFE.NS",
            "NEPHROPLUS.NS", "NEULANDLAB.NS", "NGLFINE.NS", "NH.NS", "NURECA.NS",
            "ONESOURCE.NS", "ORCHPHARMA.NS", "ORTINGLOBE.NS", "PANACEABIO.NS", "PAR.NS",
            "PARKHOSPS.NS", "PFIZER.NS", "PGHL.NS", "POLYMED.NS", "PPLPHARMA.NS",
            "RAINBOW.NS", "RPGLIFE.NS", "RUBICON.NS", "SAILIFE.NS", "SAKAR.NS",
            "SANOFI.NS", "SANOFICONR.NS", "SENORES.NS", "SHALBY.NS", "SHILPAMED.NS",
            "SIGACHI.NS", "SMSPHARMA.NS", "SOLARA.NS", "SPARC.NS", "STAR.NS",
            "SUDEEPPHRM.NS", "SUNPHARMA.NS", "SUPRIYA.NS", "SURAKSHA.NS", "SUVEN.NS",
            "SYNCOMF.NS", "SYNGENE.NS", "TAKE.NS", "THEMISMED.NS", "THYROCARE.NS",
            "TORNTPHARM.NS", "UNICHEMLAB.NS", "VAISHALI.NS", "VALIANTLAB.NS", "VENUSREM.NS",
            "VIJAYA.NS", "VIMTALABS.NS", "VINEETLAB.NS", "VIVIMEDLAB.NS", "VIYASH.NS",
            "WANBURY.NS", "WINDLAS.NS", "YATHARTH.NS", "ZIMLAB.NS", "ZOTA.NS",
            "ZYDUSLIFE.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 13. Information Technology
    # ─────────────────────────────────────────────
    "Information Technology": {
        "description": "IT Services, Software Products, BPO, SaaS, Digital Platforms",
        "stocks": [
            "3IINFOLTD.NS", "63MOONS.NS", "ACCELYA.NS", "ADROITINFO.NS", "ADSL.NS",
            "AFFLE.NS", "AIRAN.NS", "ALLDIGI.NS", "AMAGI.NS", "APTECHT.NS",
            "AURIONPRO.NS", "AURUM.NS", "BBOX.NS", "BCG.NS", "BSOFT.NS",
            "CALSOFT.NS", "CAMS.NS", "CAPILLARY.NS", "CCAVENUE.NS", "CEREBRAINT.NS",
            "CIGNITITEC.NS", "CMSINFO.NS", "COFORGE.NS", "COMPUSOFT.NS", "CONTROLPR.NS",
            "CPPLUS.NS", "CTE.NS", "CURAA.NS", "CYBERTECH.NS", "CYIENT.NS",
            "DATAMATICS.NS", "DATAPATTNS.NS", "DCI.NS", "DEVIT.NS", "DIGISPICE.NS",
            "DIGITIDE.NS", "DLINKINDIA.NS", "DRCSYSTEMS.NS", "DSSL.NS", "E2E.NS",
            "EBGNG.NS", "ECLERX.NS", "EMUDHRA.NS", "EQUIPPP.NS", "EXCELSOFT.NS",
            "EXPLEOSOL.NS", "FCSSOFT.NS", "FRACTAL.NS", "FSL.NS", "GENESYS.NS",
            "GOLDTECH.NS", "GSS.NS", "GTECJAINX.NS", "GVPTECH.NS", "HAPPSTMNDS.NS",
            "HCL-INSYS.NS", "HCLTECH.NS", "HEXT.NS", "HGM.NS", "HGS.NS",
            "INFOBEAN.NS", "INFY.NS", "INNOVANA.NS", "INSPIRISYS.NS", "INTELLECT.NS",
            "INTENTECH.NS", "IRIS.NS", "IVALUE.NS", "IZMO.NS", "KELLTONTEC.NS",
            "KPITTECH.NS", "KSOLVES.NS", "LATENTVIEW.NS", "LTM.NS", "LTTS.NS",
            "MAPMYINDIA.NS", "MASTEK.NS", "MATRIMONY.NS", "MCLOUD.NS", "MINDTECK.NS",
            "MOBIKWIK.NS", "MOSCHIP.NS", "MPHASIS.NS", "MSTCLTD.NS", "NETWEB.NS",
            "NEWGEN.NS", "NIITLTD.NS", "NINSYS.NS", "NUCLEUS.NS", "OFSS.NS",
            "ONEPOINT.NS", "ONWARDTEC.NS", "ORCHASP.NS", "ORIENTTECH.NS", "PALREDTEC.NS",
            "PANACHE.NS", "PERSISTENT.NS", "PINELABS.NS", "PROTEAN.NS", "QUICKHEAL.NS",
            "RAMCOSYS.NS", "RATEGAIN.NS", "RELIABLE.NS", "ROUTE.NS", "RSSOFTWARE.NS",
            "RSYSTEMS.NS", "SAKSOFT.NS", "SASKEN.NS", "SECMARK.NS", "SECURKLOUD.NS",
            "SIGMA.NS", "SIGMAADV.NS", "SILVERTUC.NS", "SMARTLINK.NS", "SOFTTECH.NS",
            "SONATSOFTW.NS", "SPCENET.NS", "STYL.NS", "SUBEXLTD.NS", "TANLA.NS",
            "TATAELXSI.NS", "TATATECH.NS", "TCS.NS", "TECHM.NS", "TERASOFT.NS",
            "TRACXN.NS", "TREJHARA.NS", "TRIGYN.NS", "UNIECOM.NS", "VERANDA.NS",
            "VIRINCHI.NS", "VLEGOV.NS", "WEWIN.NS", "WIPRO.NS", "XCHANGING.NS",
            "XELPMOC.NS", "XTGLOBAL.NS", "ZAGGLE.NS", "ZENSARTECH.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 14. Media, Entertainment & Publication
    # ─────────────────────────────────────────────
    "Media, Entertainment & Publication": {
        "description": "Broadcasting, OTT, Film Production, Publishing, Gaming",
        "stocks": [
            "AQYLON.NS", "BAGFILMS.NS", "BALAJITELE.NS", "BTML.NS", "CINELINE.NS",
            "CINEVISTA.NS", "CREATIVEYE.NS", "DBCORP.NS", "DEN.NS", "DGCONTENT.NS",
            "DISHTV.NS", "DNAMEDIA.NS", "ENIL.NS", "GTPL.NS", "HATHWAY.NS",
            "HMVL.NS", "JAGRAN.NS", "MUKTAARTS.NS", "NAZARA.NS", "NDLVENTURE.NS",
            "NDTV.NS", "NETWORK18.NS", "ORTEL.NS", "PFOCUS.NS", "PRSMJOHNSN.NS",
            "RADAAN.NS", "RADIOCITY.NS", "RKSWAMY.NS", "SANDESH.NS", "SAREGAMA.NS",
            "SHEMAROO.NS", "SIGNPOST.NS", "SILLYMONKS.NS", "SITINET.NS", "SUNTV.NS",
            "TIPSFILMS.NS", "TIPSMUSIC.NS", "TVTODAY.NS", "TVVISION.NS", "UFO.NS",
            "VERTOZ.NS", "ZEEL.NS", "ZEEMEDIA.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 15. Metals & Mining
    # ─────────────────────────────────────────────
    "Metals & Mining": {
        "description": "Steel, Aluminium, Copper, Mining, Metal Products, Ferro Alloys",
        "stocks": [
            "20MICRONS.NS", "AEROENTER.NS", "AEROFLEX.NS", "AHLADA.NS", "ANKITMETAL.NS",
            "APLAPOLLO.NS", "ARFIN.NS", "ASHAPURMIN.NS", "BANSALWIRE.NS", "BEDMUTHA.NS",
            "BHAGYANGR.NS", "BHARATCOAL.NS", "BHARATWIRE.NS", "BMWVENTLTD.NS", "CENTEXT.NS",
            "COALINDIA.NS", "CUBEXTUB.NS", "DPWIRES.NS", "ELECTCAST.NS", "ELECTHERM.NS",
            "EUROBOND.NS", "GALLANTT.NS", "GANDHITUBE.NS", "GEEKAYWIRE.NS", "GMDCLTD.NS",
            "GOODLUCK.NS", "GRAVITA.NS", "HARIOMPIPE.NS", "HINDALCO.NS", "HINDCOPPER.NS",
            "HINDZINC.NS", "HISARMETAL.NS", "HITECH.NS", "HLEGLAS.NS", "IMFA.NS",
            "IMPEXFERRO.NS", "INCREDIBLE.NS", "JAIBALAJI.NS", "JAINREC.NS", "JASH.NS",
            "JAYNECOIND.NS", "JINDALSAW.NS", "JINDALSTEL.NS", "JSL.NS", "JSWHL.NS",
            "JSWSTEEL.NS", "KALYANI.NS", "KAMDHENU.NS", "KIOCL.NS", "KRITIKA.NS",
            "KSL.NS", "LAKPRE.NS", "LLOYDSME.NS", "MAANALU.NS", "MAHASTEEL.NS",
            "MAITHANALL.NS", "MANAKALUCO.NS", "MANAKCOAT.NS", "MANAKSIA.NS", "MANAKSTEEL.NS",
            "MANINDS.NS", "MBEL.NS", "MCL.NS", "MIDHANI.NS", "MMP.NS",
            "MOIL.NS", "MSPL.NS", "MTARTECH.NS", "MUKANDLTD.NS", "MWL.NS",
            "NATIONALUM.NS", "NMDC.NS", "NSLNISP.NS", "ORISSAMINE.NS", "PENIND.NS",
            "POCL.NS", "PRAKASH.NS", "PRAKASHSTL.NS", "RAIN.NS", "RAJMET.NS",
            "RAJRATAN.NS", "RAMASTEEL.NS", "RATNAMANI.NS", "RATNAVEER.NS", "RHETAN.NS",
            "RUDRA.NS", "SAGARDEEP.NS", "SAIL.NS", "SALSTEEL.NS", "SAMBHV.NS",
            "SANDUMA.NS", "SARDAEN.NS", "SCODATUBES.NS", "SHAH.NS", "SHAHALLOYS.NS",
            "SHANKARA.NS", "SHIVAUM.NS", "SHYAMCENT.NS", "SHYAMMETL.NS", "SMLT.NS",
            "SOUTHWEST.NS", "STEELCAS.NS", "STEELXIND.NS", "SUNFLAG.NS", "SUPREMEENG.NS",
            "SURAJLTD.NS", "SURYAROSNI.NS", "TATASTEEL.NS", "TEGA.NS", "TEMBO.NS",
            "TIIL.NS", "UNIPARTS.NS", "USHAMART.NS", "VASWANI.NS", "VEDL.NS",
            "VENUSPIPES.NS", "VISASTEEL.NS", "VMSTMT.NS", "VRAJ.NS", "VSSL.NS",
            "VSTL.NS", "WELCORP.NS", "ZENITHSTL.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 16. Oil, Gas & Consumable Fuels
    # ─────────────────────────────────────────────
    "Oil, Gas & Consumable Fuels": {
        "description": "Oil Exploration, Refining, Gas Distribution, Coal",
        "stocks": [
            "AAKASH.NS", "ABAN.NS", "AEGISLOG.NS", "ALPHAGEO.NS", "ANTELOPUS.NS",
            "ASIANENE.NS", "ATGL.NS", "BPCL.NS", "CASTROLIND.NS", "CHENNPETRO.NS",
            "CONFIPET.NS", "DEEPINDS.NS", "DOLPHIN.NS", "GAIL.NS", "GANDHAR.NS",
            "GOACARBON.NS", "GOCLCORP.NS", "GUJGASLTD.NS", "GULFOILLUB.NS", "GULFPETRO.NS",
            "HEMIPROP.NS", "HINDOILEXP.NS", "HINDPETRO.NS", "IGL.NS", "IOC.NS",
            "JINDRILL.NS", "MGL.NS", "MRPL.NS", "OIL.NS", "OILCOUNTUB.NS",
            "ONGC.NS", "PANAMAPET.NS", "PCBL.NS", "PETRONET.NS", "PRABHA.NS",
            "RELIANCE.NS", "SEAMECLTD.NS", "SOTL.NS", "VEEDOL.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 17. Real Estate
    # ─────────────────────────────────────────────
    "Real Estate": {
        "description": "Real Estate Developers, REITs, Property Management",
        "stocks": [
            "3PLAND.NS", "AGIIL.NS", "AHLUCONT.NS", "AJMERA.NS", "AMJLAND.NS",
            "ANANTRAJ.NS", "ANSALAPI.NS", "ARIHANT.NS", "ARIHANTSUP.NS", "ARKADE.NS",
            "ARTNIRMAN.NS", "ARVSMART.NS", "ASHIANA.NS", "ATALREAL.NS", "BLAL.NS",
            "BRIGADE.NS", "COUNCODOS.NS", "DBREALTY.NS", "DLF.NS", "EFCIL.NS",
            "ELDEHSG.NS", "EMAMIREAL.NS", "EMBDL.NS", "GANESHHOU.NS", "GEECEE.NS",
            "GENCON.NS", "GODREJPROP.NS", "GOLDENTOBC.NS", "HDIL.NS", "HUBTOWN.NS",
            "KALPATARU.NS", "KOLTEPATIL.NS", "LANCORHOL.NS", "LODHA.NS", "LOTUSDEV.NS",
            "LPDC.NS", "MAHLIFE.NS", "MARATHON.NS", "MAXESTATES.NS", "MODIS.NS",
            "NAVKARURB.NS", "NESCO.NS", "NILAINFRA.NS", "NILASPACES.NS", "OBEROIRLTY.NS",
            "OMAXE.NS", "PANSARI.NS", "PARSVNATH.NS", "PENINLAND.NS", "PHOENIXLTD.NS",
            "PRAENG.NS", "PRESTIGE.NS", "PROZONER.NS", "PURVA.NS", "PVP.NS",
            "RAYMONDREL.NS", "RUSTOMJEE.NS", "RVHL.NS", "SBGLP.NS", "SCILAL.NS",
            "SHRADHA.NS", "SHRIRAMPPS.NS", "SIGNATURE.NS", "SOBHA.NS", "SUMIT.NS",
            "SUNTECK.NS", "SUPREME.NS", "SURAJEST.NS", "TARC.NS", "TEXINFRA.NS",
            "TREL.NS", "UNITECH.NS", "VIPULLTD.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 18. Retailing
    # ─────────────────────────────────────────────
    "Retailing": {
        "description": "Brick & Mortar Retail, E-commerce, Fashion Retail, Grocery",
        "stocks": [
            "ABFRL.NS", "ABLBL.NS", "ARCHIES.NS", "AVL.NS", "CNL.NS",
            "DMART.NS", "EMIL.NS", "ETERNAL.NS", "ETHOSLTD.NS", "FEL.NS",
            "FELDVR.NS", "FIRSTCRY.NS", "FLFL.NS", "GLOBUSSPR.NS", "HEADSUP.NS",
            "INDIAMART.NS", "ISFT.NS", "KALYANKJIL.NS", "KHADIM.NS", "KSR.NS",
            "LANDMARK.NS", "LIBERTSHOE.NS", "MEESHO.NS", "METROBRAND.NS", "MUFTI.NS",
            "NYKAA.NS", "OSIAHYPER.NS", "PATELRMART.NS", "PRAXIS.NS", "PVSL.NS",
            "REDTAPE.NS", "RETAIL.NS", "SENCO.NS", "SHOPERSTOP.NS", "SPENCERS.NS",
            "SREEL.NS", "STYLEBAAZA.NS", "SUPERHOUSE.NS", "SWIGGY.NS", "TRENT.NS",
            "V2RETAIL.NS", "VMM.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 19. Services
    # ─────────────────────────────────────────────
    "Services": {
        "description": "Professional Services, Staffing, BPO, Consulting, Engineering Services",
        "stocks": [
            "AAATECH.NS", "ABMINTLLTD.NS", "ABREL.NS", "ACCURACY.NS", "ACEINTEG.NS",
            "ADANIPORTS.NS", "AEGISVOPAK.NS", "AERONEU.NS", "AKG.NS", "ALANKIT.NS",
            "ALLCARGO.NS", "AMDIND.NS", "ANDHRAPAP.NS", "ANMOL.NS", "ANTGRAPHIC.NS",
            "ARENTERP.NS", "ARSHIYA.NS", "ASHOKAMET.NS", "ASMS.NS", "ASTRON.NS",
            "ATL.NS", "AUSOMENT.NS", "AVG.NS", "BALAJEE.NS", "BBTCL.NS",
            "BEARDSELL.NS", "BLACKBUCK.NS", "BLS.NS", "BLSE.NS", "BLUEDART.NS",
            "BLUSPRING.NS", "BOROLTD.NS", "BOROSCI.NS", "CARERATING.NS", "COMPINFO.NS",
            "COMSYN.NS", "CONCOR.NS", "COSMOFIRST.NS", "CROWN.NS", "CYBERMEDIA.NS",
            "CYIENTDLM.NS", "DELHIVERY.NS", "DHRUV.NS", "DIGIDRIVE.NS", "DJML.NS",
            "DREDGECORP.NS", "ECOSMOBLTY.NS", "EMMBI.NS", "ESSARSHPNG.NS", "FABTECH.NS",
            "FLAIR.NS", "FMNL.NS", "GATEWAY.NS", "GAUDIUMIVF.NS", "GENUSPAPER.NS",
            "GESHIP.NS", "GICL.NS", "GLOBALVECT.NS", "GLOTTIS.NS", "GOYALALUM.NS",
            "GRWRHITECH.NS", "GUJRAFFIA.NS", "HITECHCORP.NS", "HTMEDIA.NS", "IBULLSLTD.NS",
            "ICRA.NS", "IGIL.NS", "IMPAL.NS", "INFOMEDIA.NS", "JETFREIGHT.NS",
            "JKIPL.NS", "KANPRPLA.NS", "KAPSTON.NS", "KERNEX.NS", "KMEW.NS",
            "KOKUYOCMLN.NS", "KOTHARIPRO.NS", "KRN.NS", "KRYSTAL.NS", "KSHITIJPOL.NS",
            "KUANTUM.NS", "LINC.NS", "LLOYDSENT.NS", "MAGNUM.NS", "MAHESHWARI.NS",
            "MAHLOG.NS", "MALUPAPER.NS", "MARINE.NS", "MICEL.NS", "MITCON.NS",
            "MMTC.NS", "MOLDTKPAC.NS", "MPSLTD.NS", "NAVKARCORP.NS", "NECCLTD.NS",
            "NEXTMEDIA.NS", "NPST.NS", "NRAIL.NS", "NRL.NS", "OBCL.NS",
            "ODIGMA.NS", "OMFREIGHT.NS", "ORICONENT.NS", "ORIENTLTD.NS", "OSWALAGRO.NS",
            "PAKKA.NS", "PATINTLOG.NS", "PDMJEPAPER.NS", "POLYPLEX.NS", "PTL.NS",
            "PYRAMID.NS", "QUESS.NS", "RAMANEWS.NS", "REDINGTON.NS", "REPL.NS",
            "REPRO.NS", "ROLLT.NS", "RPPL.NS", "RPTECH.NS", "RUCHINFRA.NS",
            "SAGILITY.NS", "SAKUMA.NS", "SAMBHAAV.NS", "SANGHVIMOV.NS", "SCHAND.NS",
            "SCI.NS", "SEMAC.NS", "SHADOWFAX.NS", "SHREEJISPG.NS", "SHREERAMA.NS",
            "SHRENIK.NS", "SHREYANIND.NS", "SHYAMTEL.NS", "SICALLOG.NS", "SIL.NS",
            "SIS.NS", "SNOWMAN.NS", "SRD.NS", "STCINDIA.NS", "SUNDARAM.NS",
            "SVLL.NS", "SWANCORP.NS", "SWANDEF.NS", "TARACHAND.NS", "TCI.NS",
            "TCIEXP.NS", "TEAMLEASE.NS", "TIGERLOGS.NS", "TIL.NS", "TOTAL.NS",
            "TRANSWORLD.NS", "TVSELECT.NS", "UDS.NS", "UMAEXPORTS.NS", "UNIENTER.NS",
            "VAKRANGEE.NS", "VIKASLIFE.NS", "VINCOFE.NS", "VINYLINDIA.NS", "VRLLOG.NS",
            "WCIL.NS", "WORTHPERI.NS", "XPROINDIA.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 20. Telecommunication
    # ─────────────────────────────────────────────
    "Telecommunication": {
        "description": "Telecom Operators, Tower Companies, Telecom Infrastructure",
        "stocks": [
            "AKSHOPTFBR.NS", "AVANTEL.NS", "BHARTIARTL.NS", "BHARTIHEXA.NS", "BIRLACABLE.NS",
            "CENTUM.NS", "GTL.NS", "GTLINFRA.NS", "HFCL.NS", "IDEA.NS",
            "INDUSTOWER.NS", "ITI.NS", "KAVDEFENCE.NS", "MTNL.NS", "NELCAST.NS",
            "NELCO.NS", "ONMOBILE.NS", "OPTIEMUS.NS", "PACEDIGITK.NS", "PARACABLES.NS",
            "RAILTEL.NS", "RCOM.NS", "STLNETWORK.NS", "STLTECH.NS", "SUYOG.NS",
            "TATACOMM.NS", "TEJASNET.NS", "TNTELE.NS", "TTML.NS", "UMIYA-MRO.NS",
            "UNIINFO.NS", "VINDHYATEL.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 21. Textiles
    # ─────────────────────────────────────────────
    "Textiles": {
        "description": "Textiles, Garments, Home Furnishings, Innerwear, Fabrics",
        "stocks": [
            "ABCOTS.NS", "AKI.NS", "AKSHAR.NS", "ALOKINDS.NS", "AMBIKCO.NS",
            "ARVIND.NS", "ARVINDFASN.NS", "ASHIMASYN.NS", "AXITA.NS", "AYMSYNTEX.NS",
            "BANARBEADS.NS", "BANG.NS", "BANSWRAS.NS", "BASML.NS", "BELLACASA.NS",
            "BHANDARI.NS", "BIL.NS", "BLUESTONE.NS", "BOMDYEING.NS", "BORANA.NS",
            "BSL.NS", "CANTABIL.NS", "CELEBRITY.NS", "CENTENKA.NS", "DAMODARIND.NS",
            "DCMNVL.NS", "DIGJAMLMTD.NS", "DOLLAR.NS", "DONEAR.NS", "DPABHUSHAN.NS",
            "EASTSILK.NS", "ESSENTIA.NS", "EUROTEXIND.NS", "FAZE3Q.NS", "FIBERWEB.NS",
            "FILATEX.NS", "FILATFASH.NS", "FLEXITUFF.NS", "GANECOS.NS", "GARFIBRES.NS",
            "GHCLTEXTIL.NS", "GINNIFILA.NS", "GLOBALE.NS", "GLOBE.NS", "GOCOLORS.NS",
            "GOKEX.NS", "GOLDIAM.NS", "HIMATSEIDE.NS", "HIRECT.NS", "ICIL.NS",
            "INDIANCARD.NS", "INDORAMA.NS", "INDTERRAIN.NS", "IRISDOREME.NS", "JAIPURKURT.NS",
            "JINDWORLD.NS", "KALAMANDIR.NS", "KANANIIND.NS", "KDDL.NS", "KITEX.NS",
            "KKCL.NS", "KPRMILL.NS", "LAGNAM.NS", "LAL.NS", "LAMBODHARA.NS",
            "LAXMICOT.NS", "LEMERITE.NS", "LENSKART.NS", "LGHL.NS", "LIBAS.NS",
            "LOVABLE.NS", "LOYALTEX.NS", "LUXIND.NS", "LYPSAGEMS.NS", "MALLCOM.NS",
            "MANOMAY.NS", "MARALOVER.NS", "MAYURUNIQ.NS", "MFML.NS", "MIRZAINT.NS",
            "MITTAL.NS", "MODTHREAD.NS", "MOHITIND.NS", "MOKSH.NS", "MOTISONS.NS",
            "MVGJL.NS", "NAGREEKEXP.NS", "NAHARINDUS.NS", "NAHARSPING.NS", "NDL.NS",
            "NITINSPIN.NS", "ORBTEXP.NS", "PARASPETRO.NS", "PASHUPATI.NS", "PCJEWELLER.NS",
            "PDSL.NS", "PGIL.NS", "PIONEEREMB.NS", "PNGJL.NS", "PNGSREVA.NS",
            "PRECOT.NS", "RADHIKAJWE.NS", "RAJRILTD.NS", "RAJTV.NS", "RAYMONDLSL.NS",
            "RBZJEWEL.NS", "RELCHEMQ.NS", "RGL.NS", "RNBDENIMS.NS", "RSWM.NS",
            "RUBYMILLS.NS", "RUPA.NS", "SALONA.NS", "SANATHAN.NS", "SANGAMIND.NS",
            "SARLAPOLY.NS", "SBC.NS", "SELMC.NS", "SGL.NS", "SHANTIGOLD.NS",
            "SHEKHAWATI.NS", "SHIVAMILLS.NS", "SHIVATEX.NS", "SHRINGARMS.NS", "SILGO.NS",
            "SIYSIL.NS", "SKYGOLD.NS", "SOMATEX.NS", "SPAL.NS", "SPLIL.NS",
            "SPORTKING.NS", "SRTL.NS", "SSDL.NS", "SSWL.NS", "SUMEETINDS.NS",
            "SUPERSPIN.NS", "SURYALAXMI.NS", "SUTLEJTEX.NS", "SVPGLOB.NS", "TBZ.NS",
            "THANGAMAYL.NS", "THOMASCOTT.NS", "TRIDENT.NS", "TTL.NS", "UNITEDPOLY.NS",
            "VAIBHAVGBL.NS", "VARDHACRLC.NS", "VARDMNPOLY.NS", "VCL.NS", "VGL.NS",
            "VINNY.NS", "VIPCLOTHNG.NS", "VIVIDHA.NS", "VMART.NS", "VTL.NS",
            "WEIZMANIND.NS", "WELSPUNLIV.NS", "WINSOME.NS", "ZENITHEXPO.NS", "ZODIACLOTH.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 22. Utilities
    # ─────────────────────────────────────────────
    "Utilities": {
        "description": "Power Generation, Transmission, Distribution, Renewables, Water",
        "stocks": [
            "ACMESOLAR.NS", "ADANIENSOL.NS", "ADANIGREEN.NS", "ADANIPOWER.NS", "AWHCL.NS",
            "BANKA.NS", "BFUTILITIE.NS", "BGRENERGY.NS", "CESC.NS", "CEWATER.NS",
            "CLEANMAX.NS", "DENTA.NS", "DPSCLTD.NS", "EIEL.NS", "EMSLIMITED.NS",
            "ENERGYDEV.NS", "ENRIN.NS", "EXICOM.NS", "GIPCL.NS", "GMRP&UI.NS",
            "GREENPOWER.NS", "HPL.NS", "IEX.NS", "INDOWIND.NS", "INOXGREEN.NS",
            "INOXWIND.NS", "IREDA.NS", "IRMENERGY.NS", "JITFINFRA.NS", "JPPOWER.NS",
            "JSWENERGY.NS", "KARMAENG.NS", "KOTYARK.NS", "KPEL.NS", "KPIGREEN.NS",
            "NAVA.NS", "NHPC.NS", "NLCINDIA.NS", "NTPC.NS", "NTPCGREEN.NS",
            "POWERGRID.NS", "POWERMECH.NS", "PTC.NS", "RACE.NS", "RELTD.NS",
            "RPOWER.NS", "RTNINDIA.NS", "RTNPOWER.NS", "SGMART.NS", "SJVN.NS",
            "SOLARWORLD.NS", "SURANASOL.NS", "SURANAT&P.NS", "SUZLON.NS", "TATAPOWER.NS",
            "TECHNOE.NS", "TORNTPOWER.NS", "WAAREERTL.NS", "WABAG.NS", "ZODIAC.NS",
        ],
    },
    # ─────────────────────────────────────────────
    # 23. NSE All Stocks (Remaining)
    # ─────────────────────────────────────────────
    "NSE All Stocks": {
        "description": "All remaining NSE-listed stocks not covered in specific sectors above",
        "stocks": [
            "3BBLACKBIO.NS", "AARNAV.NS", "ABANSENT.NS", "ABMKNO.NS", "ACSTECH.NS",
            "AEPL.NS", "AHLWEST.NS", "AKCAPIT.NS", "AMBALALSA.NS", "AMIRCHAND.NS",
            "ASHIKA.NS", "ASTAR.NS", "AVAILFC.NS", "BAJAJST.NS", "BATLIBOI.NS",
            "BCPL.NS", "BEEKAY.NS", "BENGALASM.NS", "BI.NS", "BIMETAL.NS",
            "BIRLAPREC.NS", "BLACKROSE.NS", "BLIL.NS", "BNAGROCHEM.NS", "BNALTD.NS",
            "BONLON.NS", "BTTL.NS", "CEINSYS.NS", "CMPDI.NS", "COCKERILL.NS",
            "COMFINTE.NS", "DAICHI.NS", "DECNGOLD.NS", "DISAQ.NS", "DRAGARWQ.NS",
            "EFCIL-RE.NS", "ELANTAS.NS", "ELCIDIN.NS", "ELITECON.NS", "ELPROINTL.NS",
            "EMPOWER.NS", "FEDDERSHOL.NS", "FERMENTA.NS", "FRONTSP.NS", "GATECHDVR.NS",
            "GNRL.NS", "GOODYEAR.NS", "GRADIENTE.NS", "GRANDOAK.NS", "GRAUWEIL.NS",
            "GRAVISSHO.NS", "GSPCROP.NS", "HALDYNGL.NS", "HAWKINCOOK.NS", "HBESD.NS",
            "HEALTHX.NS", "INA.NS", "INDPRUD.NS", "INNOVISION.NS", "INVPRECQ.NS",
            "IWP.NS", "JSWDULUX.NS", "KAMAHOLD.NS", "KANCHI.NS", "KENNAMET.NS",
            "KICL.NS", "KIRANVYPAR.NS", "KIRLFER.NS", "KISSHT.NS", "KLBRENG-B.NS",
            "KOTIC.NS", "KOVAI.NS", "KPL.NS", "LAHOTIOV.NS", "LANDSMILL.NS",
            "MADHAVIPL.NS", "MAFATIND.NS", "MAHSCOOTER.NS", "MAJESAUT.NS", "MARSONS.NS",
            "MCCHRLS-B.NS", "MENNPIS.NS", "MERCANTILE.NS", "METROGLOBL.NS", "MMWL.NS",
            "NAGREEKCAP.NS", "NAHARCAP.NS", "NATIONSTD.NS", "NEAGI.NS", "NILE.NS",
            "NIMBSPROJ.NS", "NIRAJISPAT.NS", "NIRLON.NS", "NITTAGELA.NS", "NOVARTIND.NS",
            "OMPOWER.NS", "PIONRINV.NS", "PML.NS", "POWERICA.NS", "PRADPME.NS",
            "PRAVEG.NS", "PREMCO.NS", "QUINT.NS", "RAJPALAYAM.NS", "RMC.NS",
            "RRIL.NS", "RSDFIN.NS", "RSL.NS", "SAHLIBHFI.NS", "SAIPARENT.NS",
            "SAPPL.NS", "SAYAJIHOTL.NS", "SCANSTL.NS", "SEIL.NS", "SHARDUL.NS",
            "SHBAJRG.NS", "SHINDL.NS", "SHRIKRISH.NS", "SICAGEN.NS", "SIKA.NS",
            "SINGERIND.NS", "SONAL.NS", "SUMMITSEC.NS", "SURYALA.NS", "TAALTECH.NS",
            "TAMBOLIIN.NS", "TCC.NS", "TECHNVISN.NS", "THACKER.NS", "THAKDEV.NS",
            "TIMEX.NS", "TRANSPEK.NS", "TSFINV.NS", "ULTRAMAR.NS", "VELJAN.NS",
            "WELSPLSOL.NS", "WIMPLAST.NS", "WPIL.NS", "ZFSTEERING.NS", "ZSARACOM.NS",
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
