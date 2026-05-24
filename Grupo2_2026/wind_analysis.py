import requests
import pandas as pd
from pandas import json_normalize


# =========================================================
# API KEY
# =========================================================

API_KEY = "patCytbSzwwY9ZZhgner"


# =========================================================
# API URL & HEADERS
# =========================================================

url = "https://api.electricitymaps.com/v4/electricity-mix/past-range"

headers = {
    "auth-token": API_KEY
}

# =========================================================
# DEFINE COUNTRIES
# =========================================================

params_list = [
    {
        "zone": "FR",
        "start": "2026-01-01T00:00:00.000Z",
        "end": "2026-04-01T00:00:00.000Z",
        "temporalGranularity": "daily"
    },
    {
        "zone": "ES",
        "start": "2026-01-01T00:00:00.000Z",
        "end": "2026-04-01T00:00:00.000Z",
        "temporalGranularity": "daily"
    },
    {
        "zone": "DE",
        "start": "2026-01-01T00:00:00.000Z",
        "end": "2026-04-01T00:00:00.000Z",
        "temporalGranularity": "daily"
    }
]

COUNTRY_NAMES = {
    "FR": "France",
    "ES": "Spain",
    "DE": "Germany"
}

# =========================================================
# LOAD API DATA
# =========================================================

all_dfs = []

for params in params_list:
    zone = params["zone"]
    print(f"\nLoading data for {zone} ({COUNTRY_NAMES[zone]})...")

    response = requests.get(url, headers=headers, params=params, timeout=15)
    response.raise_for_status()

    raw = response.json()

    records = raw.get("data", [])

    # FIX: json_normalize on the list of records; nested dicts become dotted columns
    df = json_normalize(records)

    # Add country identifier
    df["country"] = zone
    df["country_name"] = COUNTRY_NAMES[zone]

    # Parse datetime
    df["datetime"] = pd.to_datetime(df["datetime"])

    # -------------------------------------------------------
    # FIX: Select only columns that actually exist in the df
    # -------------------------------------------------------
    desired_cols = [
        "datetime", "country", "country_name",
        "mix.wind",
        "mix.solar",
        "mix.hydro",
        "mix.nuclear",
        "mix.coal",
        "mix.gas",
        "mix.biomass",
        "mix.geothermal",
        "mix.oil",
        "mix.unknown",
        "mix.battery storage.charge",
        "mix.battery storage.discharge",
        "mix.hydro storage.charge",
        "mix.hydro storage.discharge",
        "mix.flows.imports",
        "mix.flows.exports",
    ]

    # Keep only the columns that exist (API schema may vary)
    available_cols = [c for c in desired_cols if c in df.columns]
    wind_df = df[available_cols].copy()

    # Rename
    rename_map = {
        "mix.wind":                      "wind_mw",
        "mix.solar":                     "solar_mw",
        "mix.hydro":                     "hydro_mw",
        "mix.nuclear":                   "nuclear_mw",
        "mix.coal":                      "coal_mw",
        "mix.gas":                       "gas_mw",
        "mix.biomass":                   "biomass_mw",
        "mix.geothermal":                "geothermal_mw",
        "mix.oil":                       "oil_mw",
        "mix.unknown":                   "unknown_mw",
        "mix.battery storage.charge":    "battery_charge_mw",
        "mix.battery storage.discharge": "battery_discharge_mw",
        "mix.hydro storage.charge":      "hydro_charge_mw",
        "mix.hydro storage.discharge":   "hydro_discharge_mw",
        "mix.flows.imports":             "import_mw",
        "mix.flows.exports":             "export_mw",
    }

    wind_df.rename(columns={k: v for k, v in rename_map.items() if k in wind_df.columns}, inplace=True)

    # Drop rows with no wind data
    wind_df = wind_df.dropna(subset=["wind_mw"])

    print(f"  {len(wind_df)} data points loaded.")
    all_dfs.append(wind_df)


