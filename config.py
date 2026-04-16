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
    "IT":                             {"avg": 28, "cheap": 20, "expensive": 38},
    "Pharma & Healthcare":            {"avg": 30, "cheap": 22, "expensive": 42},
    "Banking & Finance":              {"avg": 15, "cheap": 10, "expensive": 22},
    "FMCG":                           {"avg": 45, "cheap": 30, "expensive": 60},
    "Auto & Ancillaries":             {"avg": 22, "cheap": 14, "expensive": 30},
    "Infrastructure & Capital Goods": {"avg": 25, "cheap": 16, "expensive": 35},
    "Energy & Power":                 {"avg": 12, "cheap": 8,  "expensive": 18},
    "Chemicals & Materials":          {"avg": 30, "cheap": 20, "expensive": 42},
    "Telecom & Media":                {"avg": 20, "cheap": 12, "expensive": 30},
    "Metals & Mining":                {"avg": 10, "cheap": 6,  "expensive": 16},
    "Consumer Discretionary":         {"avg": 45, "cheap": 28, "expensive": 65},
    "Real Estate":                    {"avg": 25, "cheap": 15, "expensive": 40},
    "Textiles & Apparel":             {"avg": 18, "cheap": 10, "expensive": 28},
}

SECTOR_PB_NORMS = {
    "IT":                             {"avg": 8,   "cheap": 4,   "expensive": 15},
    "Pharma & Healthcare":            {"avg": 5,   "cheap": 2,   "expensive": 10},
    "Banking & Finance":              {"avg": 2.5, "cheap": 1,   "expensive": 4},
    "FMCG":                           {"avg": 12,  "cheap": 6,   "expensive": 25},
    "Auto & Ancillaries":             {"avg": 5,   "cheap": 2,   "expensive": 10},
    "Infrastructure & Capital Goods": {"avg": 5,   "cheap": 2,   "expensive": 10},
    "Energy & Power":                 {"avg": 2,   "cheap": 1,   "expensive": 4},
    "Chemicals & Materials":          {"avg": 5,   "cheap": 2,   "expensive": 10},
    "Telecom & Media":                {"avg": 3,   "cheap": 1,   "expensive": 6},
    "Metals & Mining":                {"avg": 1.5, "cheap": 0.7, "expensive": 3},
    "Consumer Discretionary":         {"avg": 10,  "cheap": 4,   "expensive": 20},
    "Real Estate":                    {"avg": 2.5, "cheap": 1.2, "expensive": 5},
    "Textiles & Apparel":             {"avg": 3,   "cheap": 1.5, "expensive": 6},
}

# Cyclical sectors need normalised PE (avg over cycle, not TTM)
# Source: Howard Marks -- "The Most Important Thing"
CYCLICAL_SECTORS = {"Metals & Mining", "Energy & Power", "Auto & Ancillaries", "Real Estate"}


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
    "IT":                             ["switching_cost", "intangible_assets", "data_advantage"],
    "Pharma & Healthcare":            ["intangible_assets", "regulatory", "distribution"],
    "Banking & Finance":              ["switching_cost", "network_effect", "regulatory"],
    "FMCG":                           ["intangible_assets", "distribution", "cost_advantage"],
    "Auto & Ancillaries":             ["intangible_assets", "cost_advantage", "distribution"],
    "Infrastructure & Capital Goods": ["regulatory", "cost_advantage", "switching_cost"],
    "Energy & Power":                 ["regulatory", "cost_advantage", "distribution"],
    "Chemicals & Materials":          ["cost_advantage", "intangible_assets", "switching_cost"],
    "Telecom & Media":                ["network_effect", "regulatory", "distribution"],
    "Metals & Mining":                ["cost_advantage", "regulatory"],
    "Consumer Discretionary":         ["intangible_assets", "distribution", "switching_cost"],
    "Real Estate":                    ["regulatory", "distribution", "cost_advantage"],
    "Textiles & Apparel":             ["cost_advantage", "distribution", "intangible_assets"],
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
    "IT": 7, "Pharma & Healthcare": 8, "Banking & Finance": 7,
    "FMCG": 7, "Auto & Ancillaries": 7,
    "Infrastructure & Capital Goods": 9, "Energy & Power": 6,
    "Chemicals & Materials": 7, "Telecom & Media": 5, "Metals & Mining": 5,
    "Consumer Discretionary": 8,
    "Real Estate": 8, "Textiles & Apparel": 7,
}

SECTOR_DIVERSIFICATION = {
    "IT": 7, "Pharma & Healthcare": 6, "Banking & Finance": 5,
    "FMCG": 7, "Auto & Ancillaries": 5,
    "Infrastructure & Capital Goods": 5, "Energy & Power": 4,
    "Chemicals & Materials": 6, "Telecom & Media": 4, "Metals & Mining": 3,
    "Consumer Discretionary": 7,
    "Real Estate": 3, "Textiles & Apparel": 5,
}

SECTOR_THREATS = {
    "IT": 6, "Pharma & Healthcare": 7, "Banking & Finance": 6,
    "FMCG": 8, "Auto & Ancillaries": 5,
    "Infrastructure & Capital Goods": 7, "Energy & Power": 5,
    "Chemicals & Materials": 6, "Telecom & Media": 5, "Metals & Mining": 4,
    "Consumer Discretionary": 6,
    "Real Estate": 5, "Textiles & Apparel": 5,
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
    "IT": {
        "description": "Information Technology & Software Services",
        "stocks": [
            # Large-cap
            "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS",
            "LTIM.NS", "PERSISTENT.NS", "COFORGE.NS", "MPHASIS.NS", "LTTS.NS",
            # Mid-cap
            "TATAELXSI.NS", "KPITTECH.NS", "CYIENT.NS", "ZENSAR.NS", "BIRLASOFT.NS",
            "HAPPSTMNDS.NS", "INTELLECT.NS", "NEWGEN.NS", "ROUTE.NS", "MASTEK.NS",
            # Extended universe
            "OFSS.NS", "ECLERX.NS", "TANLA.NS", "RATEGAIN.NS", "AFFLE.NS",
            "LATENTVIEW.NS", "DATAPATTNS.NS", "SONATSOFTW.NS", "NIITLTD.NS", "FIRSTSOURCE.NS",
            "CMSINFO.NS", "NUCLEUS.NS", "JUSTDIAL.NS", "TATATECH.NS", "3IINFOLTD.NS",
            "QUICKHEAL.NS", "ZENSARTECH.NS", "BSOFT.NS", "MAPMYINDIA.NS", "NAUKRI.NS",
            "NETWEB.NS", "SASKEN.NS", "EMUDHRA.NS", "SUBEXLTD.NS", "RAMCOSYS.NS",
            "INFIBEAM.NS", "SAKSOFT.NS", "AURIONPRO.NS",
        ],
    },
    "Pharma & Healthcare": {
        "description": "Pharmaceuticals, API, Hospitals, Diagnostics",
        "stocks": [
            # Large-cap
            "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "ZYDUSLIFE.NS",
            "AUROPHARMA.NS", "APOLLOHOSP.NS", "MAXHEALTH.NS", "FORTIS.NS", "LALPATHLAB.NS",
            # Mid-cap
            "BIOCON.NS", "LUPIN.NS", "TORNTPHARM.NS", "ALKEM.NS", "GLENMARK.NS",
            "IPCALAB.NS", "NATCOPHARMA.NS", "LAURUSLABS.NS", "METROPOLIS.NS", "SYNGENE.NS",
            # Extended universe
            "ABBOTINDIA.NS", "PFIZER.NS", "GLAXO.NS", "MANKIND.NS", "JBCHEPHARM.NS",
            "GRANULES.NS", "AJANTPHARM.NS", "ERIS.NS", "POLYMED.NS", "RAINBOW.NS",
            "THYROCARE.NS", "GLAND.NS", "MEDPLUS.NS", "CONCORD.NS", "SUVENPHAR.NS",
            "PPLPHARMA.NS", "ASTRAZEN.NS", "SANOFI.NS", "CAPLIPOINT.NS", "NEULANDLAB.NS",
            "MARKSANS.NS", "SOLARA.NS", "SHILPAMED.NS", "IOLCP.NS", "YATHARTH.NS",
            "VIJAYA.NS", "KRSNAA.NS", "STARHEALTH.NS", "GLORIALAB.NS",
            # Nifty 500 expansion
            "MEDANTA.NS",
        ],
    },
    "Banking & Finance": {
        "description": "Private Banks, PSU Banks, NBFCs, Insurance, AMCs",
        "stocks": [
            # Large-cap
            "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SBIN.NS",
            "BAJFINANCE.NS", "BAJAJFINSV.NS", "HDFCLIFE.NS", "SBILIFE.NS", "CHOLAFIN.NS",
            # Mid-cap (PSU banks, NBFCs, insurance)
            "BANKBARODA.NS", "PNB.NS", "INDUSINDBK.NS", "FEDERALBNK.NS", "SBICARD.NS",
            "MUTHOOTFIN.NS", "ICICIGI.NS", "ICICIPRULI.NS", "MANAPPURAM.NS", "CANBK.NS",
            # Extended universe
            "SHRIRAMFIN.NS", "M&MFIN.NS", "LICHSGFIN.NS", "RECLTD.NS", "IRFC.NS",
            "LICI.NS", "PAYTM.NS", "POLICYBZR.NS", "ABCAPITAL.NS", "IDFCFIRSTB.NS",
            "BANDHANBNK.NS", "RBLBANK.NS", "IOB.NS", "CENTRALBK.NS", "UNIONBANK.NS",
            "KFINTECH.NS", "ANGELONE.NS", "BSE.NS", "CDSL.NS", "MCX.NS",
            "NIACL.NS", "GICRE.NS", "HDFCAMC.NS", "NIPPONIND.NS", "UTIAMC.NS",
            "SUNDARMFIN.NS", "PNBHOUSING.NS", "CANFINHOME.NS", "AAVAS.NS", "CREDITACC.NS",
            # Nifty 500 expansion
            "AUBANK.NS", "EQUITASBNK.NS", "UJJIVANSFB.NS", "KARURVYSYA.NS", "CUB.NS",
            "INDIANB.NS", "IDBI.NS", "MAHABANK.NS", "MOTILALOFS.NS", "POONAWALLA.NS",
            "FIVESTAR.NS", "CRISIL.NS", "SOUTHBANK.NS"
        ],
    },
    "FMCG": {
        "description": "Fast Moving Consumer Goods, Food & Beverages",
        "stocks": [
            # Large-cap
            "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS",
            "MARICO.NS", "GODREJCP.NS", "COLPAL.NS", "TATACONSUM.NS", "VBL.NS",
            # Mid-cap
            "EMAMILTD.NS", "JYOTHYLAB.NS", "PGHH.NS", "RADICO.NS", "BIKAJI.NS",
            "HONAUT.NS", "GILLETTE.NS", "ZYDUSWELL.NS", "HATSUN.NS", "GODFRYPHLP.NS",
            # Extended universe
            "KRBL.NS", "MCDOWELL-N.NS", "UBL.NS", "CCL.NS", "BAJAJCON.NS",
            "VSTIND.NS", "VENKEYS.NS", "BALRAMCHIN.NS", "EIDPARRY.NS", "BECTORFOOD.NS",
            "PATANJALI.NS", "GLOBUSSPR.NS", "DODLA.NS", "AVANTIFEED.NS", "HERITGFOOD.NS",
            "VADILALIND.NS", "CASTROLIND.NS", "APLLTD.NS",
            # Nifty 500 expansion
            "AWL.NS", "RAJESHEXPO.NS",
        ],
    },
    "Auto & Ancillaries": {
        "description": "Automobile OEMs, Auto Parts, EV, Tyres, Batteries",
        "stocks": [
            # Large-cap OEMs
            "MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS",
            "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "FORCEMOT.NS", "OLECTRA.NS",
            # Mid-cap ancillaries
            "BALKRISIND.NS", "MOTHERSON.NS", "BHARATFORG.NS", "BOSCHLTD.NS", "SONACOMS.NS",
            "TIINDIA.NS", "SUNDRMFAST.NS", "ENDURANCE.NS", "UNOMINDA.NS", "CRAFTSMAN.NS",
            # Tyres & batteries
            "EXIDEIND.NS", "AMARARAJA.NS", "APOLLOTYRE.NS", "MRF.NS", "CEATLTD.NS",
            "JKTYRE.NS",
            # Bearings & precision
            "SCHAEFFLER.NS", "SKFINDIA.NS", "TIMKEN.NS",
            # Extended universe
            "SUPRAJIT.NS", "GABRIEL.NS", "LUMAXTECH.NS", "SANDHAR.NS", "JTEKTINDIA.NS",
            "VARROC.NS", "SWARAJENG.NS", "MAHINDCIE.NS", "TATAMTRDVR.NS", "JAMNAAUTO.NS",
            # Nifty 500 expansion
            "JBMA.NS",
        ],
    },
    "Infrastructure & Capital Goods": {
        "description": "Construction, Engineering, Defence, Railways, Electricals, Shipbuilding",
        "stocks": [
            # Large-cap
            "LT.NS", "ABB.NS", "SIEMENS.NS", "HAL.NS", "BEL.NS",
            "IRCTC.NS", "CUMMINSIND.NS", "THERMAX.NS", "GRINFRA.NS", "ESCORTS.NS",
            # Mid-cap
            "BHEL.NS", "KAYNES.NS", "AIAENG.NS", "CGPOWER.NS", "TITAGARH.NS",
            "RVNL.NS", "IRCON.NS", "NBCC.NS", "KEC.NS", "ENGINERSIN.NS",
            # Defence & shipbuilding
            "COCHINSHIP.NS", "MAZDOCK.NS", "GRSE.NS", "BDL.NS", "ASTRAMICRO.NS",
            "BEML.NS",
            # Ports & infra
            "ADANIPORTS.NS", "NCC.NS", "PNC.NS", "GPPL.NS", "HCC.NS",
            # Electricals & automation
            "HONEYWELL.NS", "TRIVENITUR.NS", "ELECON.NS", "KENNAMETAL.NS",
            # Railways & housing
            "RAILTEL.NS", "HUDCO.NS", "HGINFRA.NS", "MANINFRA.NS", "JKINFRA.NS",
            # Nifty 500 expansion
            "KPIL.NS", "PRAJ.NS", "ELGIEQUIP.NS", "JSWINFRA.NS", "VOLTAMP.NS", "ACE.NS",
        ],
    },
    "Energy & Power": {
        "description": "Oil & Gas, Renewables, Power Utilities, Gas Distribution",
        "stocks": [
            # Large-cap
            "RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ADANIGREEN.NS", "TATAPOWER.NS",
            "BPCL.NS", "IOC.NS", "GAIL.NS", "COALINDIA.NS", "NHPC.NS",
            # Mid-cap
            "ONGC.NS", "HINDPETRO.NS", "PETRONET.NS", "IGL.NS", "MGL.NS",
            "JSWENERGY.NS", "SJVN.NS", "TORNTPOWER.NS", "CESC.NS", "PFC.NS",
            # Extended
            "ADANIENT.NS", "ADANIPOWER.NS", "GUJGASLTD.NS", "GSPL.NS", "ATGL.NS",
            "MRPL.NS", "CHENNPETRO.NS", "OIL.NS", "AEGISCHEM.NS", "IREDA.NS",
            "KPIGREEN.NS", "WAAREE.NS", "SUZLON.NS", "INOXWIND.NS", "GIPCL.NS",
            "POWERMECH.NS", "RPOWER.NS", "JPPOWER.NS",
            # Nifty 500 expansion
            "IEX.NS",
        ],
    },
    "Chemicals & Materials": {
        "description": "Specialty Chemicals, Paints, Agrochemicals, Cement, Polymers",
        "stocks": [
            # Large-cap
            "PIDILITIND.NS", "ASIANPAINT.NS", "SRF.NS", "ATUL.NS", "PIIND.NS",
            "DEEPAKFERT.NS", "CLEAN.NS", "NAVINFLUOR.NS", "FLUOROCHEM.NS", "TATACHEM.NS",
            # Mid-cap chemicals
            "DEEPAKNTR.NS", "AARTIIND.NS", "GALAXYSURF.NS", "SUMICHEM.NS", "UPL.NS",
            "BASF.NS", "LXCHEM.NS", "ALKYLAMINE.NS", "FINEORG.NS", "SUDARSCHEM.NS",
            # Extended chemicals
            "VINATIORGA.NS", "NOCIL.NS", "ROSSARI.NS", "APCOTEXIND.NS", "TIRUMALCHM.NS",
            "CHEMPLAST.NS", "GUJALKALI.NS", "IONEXCHANG.NS", "RALLIS.NS", "BALAMINES.NS",
            "NEOGEN.NS", "ANUPAM.NS",
            # Cement & building materials
            "ULTRACEMCO.NS", "SHREECEM.NS", "AMBUJACEM.NS", "ACC.NS", "DALBHARAT.NS",
            "JKCEMENT.NS", "RAMCOCEM.NS", "INDIACEM.NS",
            # Paints
            "BERGEPAINT.NS", "KANSAINER.NS",
            # Abrasives & glass
            "GRINDWELL.NS", "CARBORUNIV.NS", "TARSONS.NS",
            # Nifty 500 expansion — fertilizers & agrochemicals
            "COROMANDEL.NS", "CHAMBLFERT.NS", "GNFC.NS", "GSFC.NS",
            "GODREJIND.NS", "GRASIM.NS", "SUPREMEIND.NS", "NUVOCO.NS", "DHANUKA.NS",
        ],
    },
    "Telecom & Media": {
        "description": "Telecom Operators, Media, Broadcasting, Digital Platforms",
        "stocks": [
            # Telecom operators
            "BHARTIARTL.NS", "IDEA.NS", "INDUSTOWER.NS", "TTML.NS",
            # Media & entertainment
            "ZEEL.NS", "PVRINOX.NS", "SUNTV.NS", "NAZARA.NS", "SAREGAMA.NS",
            "HATHWAY.NS", "DEN.NS", "TV18BRDCST.NS", "NETWORK18.NS", "NDTV.NS",
            # Extended
            "DISH.NS", "BALAJITELE.NS", "SHEMAROO.NS", "TIPSINDLTD.NS",
            "DBCORP.NS", "JAGRAN.NS", "GTPL.NS", "TVTODAY.NS", "NAVNETEDUL.NS",
            # Nifty 500 expansion
            "TATACOMM.NS",
        ],
    },
    "Metals & Mining": {
        "description": "Steel, Aluminium, Copper, Mining, Metal Products",
        "stocks": [
            # Large-cap
            "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "NMDC.NS",
            "JINDALSTEL.NS", "NATIONALUM.NS", "HINDZINC.NS", "SAIL.NS",
            # Mid-cap
            "MOIL.NS", "APLAPOLLO.NS", "RATNAMANI.NS", "WELCORP.NS", "KIOCL.NS",
            "GRAVITA.NS", "HINDCOPPER.NS",
            # Extended
            "MIDHANI.NS", "GODAWARI.NS", "SHYAMMETL.NS", "SARDAEN.NS", "GALLANTT.NS",
            "JSWHL.NS", "TINPLATE.NS", "RAJRATAN.NS", "MANAKSIA.NS",
            # Nifty 500 expansion
            "JSL.NS", "LLOYDSME.NS",
        ],
    },
    "Consumer Discretionary": {
        "description": "Retail, Lifestyle, Jewellery, QSR, Home & Building Products, Electronics",
        "stocks": [
            # Large-cap
            "TITAN.NS", "TRENT.NS", "DMART.NS", "JUBLFOOD.NS", "PAGEIND.NS",
            "VOLTAS.NS", "HAVELLS.NS", "POLYCAB.NS", "DIXON.NS", "ASTRAL.NS",
            # Mid-cap home & lifestyle
            "CROMPTON.NS", "WHIRLPOOL.NS", "BLUESTAR.NS", "BATAINDIA.NS", "RELAXO.NS",
            "RAYMOND.NS", "KAJARIACER.NS", "CERA.NS", "VGUARD.NS", "AMBER.NS",
            # QSR & food services
            "DEVYANI.NS", "SAPPHIRE.NS", "WESTLIFE.NS", "ZOMATO.NS",
            # Fashion & retail
            "SHOPERSTOP.NS", "NYKAA.NS", "MANYAVAR.NS", "CAMPUS.NS", "METROBRAND.NS",
            # Electronics & electricals
            "ORIENTELEC.NS", "SYMPHONY.NS", "IFBIND.NS", "TTKPRESTIG.NS",
            # Building products
            "CENTURYPLY.NS", "GREENPLY.NS", "PRINCEPIPE.NS",
            # Jewellery
            "KALYANKJIL.NS", "SENCO.NS", "ETHOS.NS",
            # Travel & leisure
            "INDIGO.NS", "WONDERLA.NS", "MHRIL.NS",
            # Luggage & accessories
            "SAFARI.NS", "VIPIND.NS",
            # Other consumer
            "BOROSIL.NS", "CARTRADE.NS", "BLUEDART.NS",
            # Nifty 500 expansion
            "INDHOTEL.NS", "DOMS.NS", "BARBEQUE.NS",
        ],
    },
    "Real Estate": {
        "description": "Real Estate Developers, REITs, Property Management",
        "stocks": [
            # Large-cap developers
            "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "LODHA.NS",
            "PHOENIXLTD.NS", "BRIGADE.NS",
            # Mid-cap developers
            "SOBHA.NS", "SUNTECK.NS", "MAHLIFE.NS", "KOLTEPATIL.NS",
            "ANANTRAJ.NS", "PURVA.NS",
            # Extended
            "RUSTOMJEE.NS", "SIGNATURE.NS",
            # REITs
            "EMBASSY.NS", "MINDSPACE.NS", "BIRET.NS",
        ],
    },
    "Textiles & Apparel": {
        "description": "Textiles, Garments, Home Furnishings, Innerwear",
        "stocks": [
            # Home textiles
            "TRIDENT.NS", "WELSPUNLIV.NS", "HIMATSEIDE.NS",
            # Fabrics & yarn
            "ARVIND.NS", "VTL.NS", "KPRMILL.NS",
            # Garment exports
            "GOKALDAS.NS", "KITEX.NS",
            # Innerwear & hosiery
            "LUXIND.NS", "DOLLAR.NS", "RUPA.NS",
            # Branded apparel
            "TCNSBRANDS.NS",
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
