# settings

START = "2023-01-01"
END = None   # None = today

MARKET = "ACWI"   # MSCI ACWI etf as market proxy

# portfolio split, equal weight inside each region
NORDIC_SHARE = 0.4
GLOBAL_SHARE = 0.6

# ticker: (name, region, group)
STOCKS = {
    # core AI names, these make up the AI basket
    "NVDA": ("Nvidia", "global", "direct_ai"),
    "MSFT": ("Microsoft", "global", "direct_ai"),
    "GOOGL": ("Alphabet", "global", "direct_ai"),
    "META": ("Meta", "global", "direct_ai"),
    "AMZN": ("Amazon", "global", "direct_ai"),
    "AVGO": ("Broadcom", "global", "direct_ai"),
    "AMD": ("AMD", "global", "direct_ai"),
    "TSM": ("TSMC", "global", "direct_ai"),
    "ASML.AS": ("ASML", "global", "direct_ai"),

    # power / grid / electrification
    "ETN": ("Eaton", "global", "power_grid"),
    "VRT": ("Vertiv", "global", "power_grid"),
    "SU.PA": ("Schneider Electric", "global", "power_grid"),
    "ENR.DE": ("Siemens Energy", "global", "power_grid"),
    "NEE": ("NextEra Energy", "global", "power_grid"),
    "CEG": ("Constellation", "global", "power_grid"),
    "ABB.ST": ("ABB", "nordic", "power_grid"),
    "NIBE-B.ST": ("Nibe", "nordic", "power_grid"),

    # suppliers to chip industry / metals
    "ATCO-A.ST": ("Atlas Copco", "nordic", "semi_supply"),
    "BOL.ST": ("Boliden", "nordic", "semi_supply"),
    "ALFA.ST": ("Alfa Laval", "nordic", "semi_supply"),

    "ERIC-B.ST": ("Ericsson", "nordic", "other_tech"),
    "HEXA-B.ST": ("Hexagon", "nordic", "other_tech"),

    "SAND.ST": ("Sandvik", "nordic", "industrial"),
    "VOLV-B.ST": ("Volvo", "nordic", "industrial"),
    "ASSA-B.ST": ("Assa Abloy", "nordic", "industrial"),
    "EPI-A.ST": ("Epiroc", "nordic", "industrial"),
    "SAAB-B.ST": ("Saab", "nordic", "industrial"),
    "SIE.DE": ("Siemens", "global", "industrial"),

    "SEB-A.ST": ("SEB", "nordic", "financial"),
    "NDA-SE.ST": ("Nordea", "nordic", "financial"),
    "INVE-B.ST": ("Investor", "nordic", "financial"),
    "JPM": ("JPMorgan", "global", "financial"),

    "NOVO-B.CO": ("Novo Nordisk", "nordic", "health"),
    "JNJ": ("Johnson & Johnson", "global", "health"),
    "RHHBY": ("Roche", "global", "health"),
    "HM-B.ST": ("H&M", "nordic", "consumer"),
    "ESSITY-B.ST": ("Essity", "nordic", "consumer"),
    "NESN.SW": ("Nestle", "global", "consumer"),
    "PG": ("Procter & Gamble", "global", "consumer"),
    "KO": ("Coca-Cola", "global", "consumer"),
    "TELIA.ST": ("Telia", "nordic", "telecom"),
    "EQNR.OL": ("Equinor", "nordic", "energy"),
    "XOM": ("Exxon Mobil", "global", "energy"),
}

AI_STOCKS = [t for t in STOCKS if STOCKS[t][2] == "direct_ai"]

# deepseek sell-off, monday 27 jan 2025
DEEPSEEK_DATE = "2025-01-27"

# scenario: AI basket falls 25%, market falls 10%
SCEN_AI = -0.25
SCEN_MARKET = -0.10
