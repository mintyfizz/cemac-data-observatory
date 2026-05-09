"""Configuration constants for the extraction pipeline."""

# List of CEMAC countries and their corresponding ISO3 codes.
CEMAC_COUNTRIES = {
    "COG": "Congo, Rep.",
    "CMR": "Cameroon",
    "CAF": "Central African Republic",
    "TCD": "Chad",
    "GNQ": "Equatorial Guinea",
    "GAB": "Gabon",
}

# Benchmark countries to compare with CEMAC countries.
BENCHMARK_COUNTRIES = {
    "RWA": "Rwanda",
    "KEN": "Kenya",
}

# Combine CEMAC and benchmark countries.
ALL_COUNTRIES = {**CEMAC_COUNTRIES, **BENCHMARK_COUNTRIES}

# List of indicators to be extracted from the World Bank API.
INDICATORS = {
    "IT.NET.USER.ZS":    "Internet users (% of population)",
    "IT.CEL.SETS.P2":    "Mobile cellular subscriptions per 100",
    "IT.NET.BBND.P2":    "Fixed broadband subscriptions per 100",
    "EG.ELC.ACCS.ZS":    "Access to electricity (% of population)",
    "NY.GDP.PCAP.PP.CD": "GDP per capita, PPP (current intl $)",
    "SE.XPD.TOTL.GD.ZS": "Government education spending (% of GDP)",
    "SH.XPD.CHEX.GD.ZS": "Current health expenditure (% of GDP)",
    "NE.TRD.GNFS.ZS":    "Trade (% of GDP)",
    "SP.URB.TOTL.IN.ZS": "Urban population (%)",
    "SP.POP.TOTL":       "Population, total",
}

WB_BASE_URL = "https://api.worldbank.org/v2"
