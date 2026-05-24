import requests
import pandas as pd
from pandas import json_normalize
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


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
#        "mix.unknown",
#        "mix.battery storage.charge",
#        "mix.battery storage.discharge",
#        "mix.hydro storage.charge",
#        "mix.hydro storage.discharge",
#        "mix.flows.imports",
#        "mix.flows.exports",
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
#        "mix.unknown":                   "unknown_mw",
#        "mix.battery storage.charge":    "battery_charge_mw",
#        "mix.battery storage.discharge": "battery_discharge_mw",
#        "mix.hydro storage.charge":      "hydro_charge_mw",
#        "mix.hydro storage.discharge":   "hydro_discharge_mw",
#        "mix.flows.imports":             "import_mw",
#        "mix.flows.exports":             "export_mw",
    }

    wind_df.rename(columns={k: v for k, v in rename_map.items() if k in wind_df.columns}, inplace=True)

    # Drop rows with no wind data
    wind_df = wind_df.dropna(subset=["wind_mw"])

    print(f"  {len(wind_df)} data points loaded.")
    all_dfs.append(wind_df)



# MERGE ALL COUNTRIES

final_df = pd.concat(all_dfs, ignore_index=True)
final_df.sort_values(["country", "datetime"], inplace=True)

# DISPLAY OPTIONS

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.float_format", "{:,.1f}".format)

# DATAFRAME OVERVIEW

print("\n" + "=" * 50)
print("DATAFRAME INFO")
print("=" * 50)
print(final_df.info())

print("\n" + "=" * 50)
print("FIRST 10 ROWS")
print("=" * 50)
print(final_df.head(10).to_string())

print("\n" + "=" * 50)
print("MISSING VALUES")
print("=" * 50)
print(final_df.isnull().sum())

# WIND GENERATION ANALYSIS

print("\n" + "=" * 50)
print("WIND GENERATION ANALYSIS (MW)")
print("=" * 50)

wind_stats = final_df.groupby(["country", "country_name"])["wind_mw"].agg(
    Mean="mean",
    Median="median",
    Std="std",
    Min="min",
    Max="max",
    Total="sum"
).round(1)

print("\nStatistics by Country:\n")
print(wind_stats.to_string())

# Month-by-month breakdown
if "datetime" in final_df.columns:
    final_df["month"] = final_df["datetime"].dt.to_period("M")
    monthly = final_df.groupby(["country_name", "month"])["wind_mw"].mean().round(1)
    print("\n\nMonthly Average Wind Generation (MW):\n")
    print(monthly.to_string())

# Wind share of total production (if other sources available)
production_cols = [c for c in ["wind_mw", "solar_mw", "hydro_mw", "nuclear_mw", "coal_mw", "gas_mw", "biomass_mw", "geothermal_mw", "oil_mw"] if c in final_df.columns]
if len(production_cols) > 1:
    for col in production_cols:
        final_df[col] = pd.to_numeric(final_df[col], errors="coerce")
        final_df["total_production_mw"] = final_df[production_cols].sum(axis=1, min_count=1)
        final_df["wind_share_pct"] = (
            pd.to_numeric(final_df["wind_mw"], errors="coerce") /
            pd.to_numeric(final_df["total_production_mw"], errors="coerce") * 100
    ).round(2)
    wind_share = final_df.groupby("country_name")["wind_share_pct"].mean().round(2)
    print("\n\nAverage Wind Share of Total Production (%):\n")
    print(wind_share.to_string())

    # VISUALIZATION settings

colors = {"FR": "#2563EB", "ES": "#DC2626", "DE": "#16A34A"}
country_labels = {"FR": "France", "ES": "Spain", "DE": "Germany"}
countries = final_df["country"].unique()

# Figure 1: Daily Wind Generation per Country

fig1, axes1 = plt.subplots(len(countries), 1, figsize=(12, 4 * len(countries)), sharex=True)
fig1.suptitle("Figure 1 — Daily Wind Generation per Country (MW)", fontsize=14, fontweight="bold", y=1.01)
 
for ax, country in zip(axes1, countries):
    subset = final_df[final_df["country"] == country].copy().sort_values("datetime")
    ax.plot(
        subset["datetime"], subset["wind_mw"],
        color=colors.get(country, "grey"), linewidth=2.0, alpha=0.9,
        label="Daily"
    )
    # 7-day rolling mean
    rolling = subset.set_index("datetime")["wind_mw"].rolling("7D").mean()
    ax.plot(
        rolling.index, rolling.values,
        color=colors.get(country, "grey"), linewidth=1.5,
        linestyle="--", alpha=0.6, label="7-Day Avg"
    )
    ax.set_title(country_labels.get(country, country), fontsize=12, fontweight="bold")
    ax.set_ylabel("Wind (MW)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax.legend(fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
 
fig1.tight_layout()
#fig1.savefig("Grupo2_2026/plots/wind_daily.png", dpi=150, bbox_inches="tight")
#print("\nFigure 1 saved as: wind_daily.png")


# Figure 2: Monthly Average Wind Generation 

if "month" in final_df.columns:
    monthly_pivot = (
        final_df.groupby(["month", "country"])["wind_mw"]
        .mean()
        .unstack("country")
    )
    month_list = list(monthly_pivot.index)
    n_months = len(month_list)
    country_list = list(monthly_pivot.columns)
    x = list(range(len(country_list)))
    width = 0.55
 
    fig2, axes2 = plt.subplots(1, n_months, figsize=(5 * n_months, 6), sharey=True)
    if n_months == 1:
        axes2 = [axes2]
    fig2.suptitle("Figure 2 — Monthly Wind Generation Comparison by Country (MW)", fontsize=14, fontweight="bold", y=1.02)
 
    for ax, month in zip(axes2, month_list):
        values = [monthly_pivot.loc[month, c] if c in monthly_pivot.columns else 0 for c in country_list]
        bar_colors = [colors.get(c, "grey") for c in country_list]
        bars = ax.bar(x, values, width=width, color=bar_colors, alpha=0.85, edgecolor="white")
 
        # Value labels on top of each bar
        for bar, val in zip(bars, values):
            if pd.notna(val):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(v for v in values if pd.notna(v)) * 0.01,
                    f"{val:,.0f}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold"
                )
 
        ax.set_title(str(month), fontsize=12, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([country_labels.get(c, c) for c in country_list], fontsize=10)
        ax.grid(True, axis="y", linestyle="--", alpha=0.4)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        if ax == axes2[0]:
            ax.set_ylabel("Avg Wind Generation (MW)")
 
    # Shared legend
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors.get(c, "grey"), alpha=0.85)
               for c in country_list]
    fig2.legend(handles, [country_labels.get(c, c) for c in country_list],
                loc="lower center", ncol=len(country_list), fontsize=10,
                bbox_to_anchor=(0.5, -0.06), frameon=False)
 
    fig2.tight_layout()
    #fig2.savefig("Grupo2_2026/plots/wind_monthly_comparison.png", dpi=150, bbox_inches="tight")
    #print("Figure 2 saved as: wind_monthly_comparison.png")
     
     
plt.show()