import requests
import pandas as pd
from pandas import json_normalize
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import warnings


warnings.filterwarnings("ignore")



# =========================================================
# API KEY
# =========================================================

API_KEY = "patCytbSzwwY9ZZhgner"


# =========================================================
# API URL & HEADERS
# =========================================================

url = "https://api.electricitymaps.com/v3/electricity-source/wind/past-range"


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
        "temporalGranularity": "hourly"
    },
    {
        "zone": "ES",
        "start": "2026-01-01T00:00:00.000Z",
        "end": "2026-04-01T00:00:00.000Z",
        "temporalGranularity": "hourly"
    },
    {
        "zone": "DE",
        "start": "2026-01-01T00:00:00.000Z",
        "end": "2026-04-01T00:00:00.000Z",
        "temporalGranularity": "hourly"
    }
]

COUNTRY_NAMES = {
    "FR": "France",
    "ES": "Spain",
    "DE": "Germany"
}

# LOAD API DATA — 7-day chunks per country (API range limit)
 
all_dfs = []
 
for base_params in params_list:
    zone = base_params["zone"]
    print(f"\nLoading data for {zone} ({COUNTRY_NAMES[zone]})...")
 
    start = pd.Timestamp(base_params["start"])
    end   = pd.Timestamp(base_params["end"])
    zone_records = []
    current = start
 
    while current < end:
        chunk_end = min(current + pd.Timedelta(days=7), end)
        params = {
            "zone":                zone,
            "start":               current.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "end":                 chunk_end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "temporalGranularity": "hourly"
        }
        print(f"  Fetching {params['start'][:10]} → {params['end'][:10]}...", end=" ", flush=True)
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        records = response.json().get("data", [])
        print(f"✓ {len(records)} records")
        zone_records.extend(records)
 
        current = chunk_end
 
    df = json_normalize(zone_records)
    print(f"  Total: {len(df)} hourly records for {COUNTRY_NAMES[zone]}.")
 
    # Add country identifier
    df["country"] = zone
    df["country_name"] = COUNTRY_NAMES[zone]
 
    # Parse datetime
    df["datetime"] = pd.to_datetime(df["datetime"])


    # FIX: Select only columns that actually exist in the df
    wind_df = df[["datetime", "country", "country_name"] + 
                 [c for c in df.columns if c not in ["datetime", "country", "country_name"]]].copy()

    # Rename the main value column to wind_mw and convert MW → keep as MW
    wind_df.rename(columns={"value": "wind_mw"}, inplace=True)
    wind_df["wind_mw"] = pd.to_numeric(wind_df["wind_mw"], errors="coerce")

    wind_df = wind_df.dropna(subset=["wind_mw"])

    print(f"  {len(wind_df)} data points loaded.")
    all_dfs.append(wind_df)

# MERGE ALL COUNTRIES

final_df = pd.concat(all_dfs, ignore_index=True)
final_df.sort_values(["country", "datetime"], inplace=True)

final_df["hour"] = final_df["datetime"].dt.hour
final_df["weekday"] = final_df["datetime"].dt.day_name()
final_df["is_weekend"] = final_df["datetime"].dt.weekday >= 5
final_df["month"] = final_df["datetime"].dt.to_period("M")

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
print("WIND GENERATION ANALYSIS (MW) — HOURLY DATA")
print("=" * 50)
 
wind_stats = final_df.groupby(["country", "country_name"])["wind_mw"].agg(
    Mean="mean",
    Median="median",
    Std="std",
    Min="min",
    Max="max",
    Total="sum",
    Count="count"
).round(1)
 
print("\nStatistics by Country (per hourly observation):\n")
print(wind_stats.to_string())
 
# Month-by-month breakdown (hourly averaged per month)
if "datetime" in final_df.columns:
    monthly = final_df.groupby(["country_name", "month"])["wind_mw"].agg(
        Mean="mean",
        Std="std",
        Min="min",
        Max="max"
    ).round(1)
    print("\n\nMonthly Hourly Wind Generation Statistics (MW):\n")
    print(monthly.to_string())
 
# Hour-of-day breakdown
print("\n\nAverage Wind Generation by Hour of Day (MW):\n")
hourly_profile = final_df.groupby(["country_name", "hour"])["wind_mw"].mean().round(1)
print(hourly_profile.to_string())
 
# Peak hour per country
print("\n\nPeak Wind Hour per Country:\n")
for country in final_df["country_name"].unique():
    profile = final_df[final_df["country_name"] == country].groupby("hour")["wind_mw"].mean()
    peak_hour = profile.idxmax()
    print(f"  {country}: {peak_hour:02d}:00 ({profile[peak_hour]:,.1f} MW avg)")
 
# Weekend vs Weekday
print("\n\nWeekday vs Weekend Average Wind Generation (MW):\n")
wk = final_df.groupby(["country_name", "is_weekend"])["wind_mw"].mean().round(1)
wk = wk.rename(index={False: "Weekday", True: "Weekend"}, level="is_weekend")
print(wk.to_string())
 
 
# =========================================================
# TOP & BOTTOM WIND HOURS
# =========================================================
 
print("\n" + "=" * 50)
print("TOP 10 WIND GENERATION HOURS")
print("=" * 50)
 
top_hours = final_df.sort_values("wind_mw", ascending=False)[
    ["datetime", "country_name", "wind_mw"]
].head(10).copy()
top_hours["datetime"] = top_hours["datetime"].dt.strftime("%Y-%m-%d %H:%M")
print(top_hours.to_string(index=False))
 
print("\n" + "=" * 50)
print("BOTTOM 10 WIND GENERATION HOURS (lowest production)")
print("=" * 50)
 
bottom_hours = final_df.sort_values("wind_mw", ascending=True)[
    ["datetime", "country_name", "wind_mw"]
].head(10).copy()
bottom_hours["datetime"] = bottom_hours["datetime"].dt.strftime("%Y-%m-%d %H:%M")
print(bottom_hours.to_string(index=False))

# VISUALIZATION settings

colors = {"FR": "#2563EB", "ES": "#DC2626", "DE": "#16A34A"}
country_labels = {"FR": "France", "ES": "Spain", "DE": "Germany"}
countries = final_df["country"].unique()

# Figure 1: Daily Wind Generation per Country

fig1, axes1 = plt.subplots(len(countries), 1, figsize=(12, 4 * len(countries)), sharex=True)
fig1.suptitle("Figure 1 — Hourly Wind Generation per Country (MW)", fontsize=14, fontweight="bold", y=1.01)
 
for ax, country in zip(axes1, countries):
    subset = final_df[final_df["country"] == country].copy().sort_values("datetime")
    ax.plot(
        subset["datetime"], subset["wind_mw"],
        color=colors.get(country, "grey"), linewidth=2.0, alpha=0.9,
        label="Hourly"
    )
    # 7-day rolling mean
    rolling = subset.set_index("datetime")["wind_mw"].rolling("7D").mean()
    ax.plot(
        rolling.index, rolling.values,
        color=colors.get(country, "grey"), linewidth=1.5,
        linestyle="--", alpha=0.6, label="7-Day Rolling Avg"
    )
    ax.set_title(country_labels.get(country, country), fontsize=12, fontweight="bold")
    ax.set_ylabel("Wind (MW)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax.legend(fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
 
fig1.text(0.5, -0.01, "Source: Electricity Maps API", ha="center", fontsize=8, color="grey")
fig1.tight_layout()
#fig1.savefig("Grupo2_2026/plots/wind_hourly.png", dpi=150, bbox_inches="tight")
#print("\nFigure 1 saved as: wind_hourly.png")


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
    fig2.text(0.5, -0.01, "Source: Electricity Maps API", ha="center", fontsize=8, color="grey")
    fig2.tight_layout()
    #fig2.savefig("Grupo2_2026/plots/wind_monthly_comparison.png", dpi=150, bbox_inches="tight")
    #print("Figure 2 saved as: wind_monthly_comparison.png")
     
# Figure 3: Wind Distribution Boxplot (all countries side by side)

fig3, ax3 = plt.subplots(figsize=(10, 6))
fig3.suptitle("Figure 3 — Wind Generation Distribution by Country (MW)", fontsize=14, fontweight="bold")
 
data_for_box = [
    pd.to_numeric(final_df[final_df["country"] == c]["wind_mw"], errors="coerce").dropna().values
    for c in countries
]
bp = ax3.boxplot(
    data_for_box,
    labels=[country_labels.get(c, c) for c in countries],
    patch_artist=True,
    medianprops=dict(color="black", linewidth=1.5, linestyle= "--" ),
    whiskerprops=dict(linewidth=1.5),
    capprops=dict(linewidth=1.5),
    flierprops=dict(marker="o", markersize=4, alpha=0.5)
)
for patch, country in zip(bp["boxes"], countries):
    patch.set_facecolor(colors.get(country, "grey"))
    patch.set_alpha(0.75)

# Add median value labels on the right end of each median line
for i, (median_line, data) in enumerate(zip(bp["medians"], data_for_box)):
    median_val = median_line.get_ydata()[1]
    x_right = median_line.get_xdata()[1]  # rightmost x point of the median line
    ax3.text(
        x_right + 0.05, median_val,
        f"{median_val:,.0f} MW",
        ha="left", va="center",
        fontsize=10, fontweight="bold", color="black",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.7)
    )
 
ax3.set_ylabel("Wind Generation (MW)")
ax3.grid(True, axis="y", linestyle="--", alpha=0.4)
ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

fig3.text(0.5, -0.01, "Source: Electricity Maps API", ha="center", fontsize=8, color="grey") 
fig3.tight_layout()
# fig3.savefig("Grupo2_2026/plots/boxplot.png", dpi=150, bbox_inches="tight")
# print("Figure 3 saved as: boxplot.png")


# =========================================================
# COEFFICIENT OF VARIATION (CV)
# =========================================================
 
print("\n" + "=" * 50)
print("COEFFICIENT OF VARIATION (CV) — WIND GENERATION")
print("=" * 50)
 
cv_stats = final_df.groupby(["country", "country_name"])["wind_mw"].agg(
    Mean="mean",
    Std="std"
)
cv_stats["CV (%)"] = (cv_stats["Std"] / cv_stats["Mean"] * 100).round(2)
cv_stats = cv_stats.round(2)
print("\nA higher CV means more volatile/unreliable wind output.\n")
print(cv_stats.to_string())
 
# Figure 4: CV Bar Chart
fig4, ax4 = plt.subplots(figsize=(8, 5))
fig4.suptitle("Figure 4 — Coefficient of Variation of Wind Generation (%)",
              fontsize=14, fontweight="bold")
 
cv_values = cv_stats["CV (%)"]
bar_colors = [colors.get(c, "grey") for c in cv_stats.index.get_level_values("country")]
bars = ax4.bar(
    [country_labels.get(c, c) for c in cv_stats.index.get_level_values("country")],
    cv_values,
    color=bar_colors,
    alpha=0.85,
    edgecolor="white",
    width=0.5
)
 
# Value labels on bars
for bar, val in zip(bars, cv_values):
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        f"{val:.1f}%",
        ha="center", va="bottom",
        fontsize=11, fontweight="bold"
    )
 
ax4.set_ylabel("Coefficient of Variation (%)")
ax4.grid(True, axis="y", linestyle="--", alpha=0.4)
ax4.set_ylim(0, cv_values.max() * 1.2)

fig4.text(0.5, -0.01, "Source: Electricity Maps API", ha="center", fontsize=8, color="grey") 
fig4.tight_layout()
# fig4.savefig("Grupo2_2026/plots/wind_variation.png", dpi=150, bbox_inches="tight")
# print("\nFigure 4 saved as: wind_variation.png")

plt.show()