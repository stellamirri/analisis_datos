import os
from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
import pandas as pd
import requests


API_KEY = "patCytbSzwwY9ZZhgner"
COUNTRIES = ["ES", "FR", "DE"]
SOURCE_TYPE = "solar"
BASE_URL = "https://api.electricitymaps.com/v4/electricity-mix"
OUTPUT_FILE = "Solar_hourly_generation_3_countries_imen.csv"


def split_date_range(start_date, end_date, chunk_days=10):
    """
    Split the selected period into chunks of maximum 10 days.
    Electricity Maps past-range endpoints may limit the number of days per request.
    """
    current_start = start_date

    while current_start < end_date:
        current_end = min(current_start + timedelta(days=chunk_days), end_date)
        yield current_start, current_end
        current_start = current_end


def fetch_solar_data_for_country(country, start_date, end_date):
    """
    Download hourly solar electricity generation data for one country.
    """
    headers = {"auth-token": API_KEY}
    all_rows = []

    for chunk_start, chunk_end in split_date_range(start_date, end_date):
        url = f"{BASE_URL}/{SOURCE_TYPE}/past-range"

        params = {
            "zone": country,
            "start": chunk_start.isoformat().replace("+00:00", "Z"),
            "end": chunk_end.isoformat().replace("+00:00", "Z"),
            "temporalGranularity": "hourly",
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(
                f"API error for {country}: {response.status_code} - {response.text}"
            )

        data = response.json()
        records = data.get("history", data.get("data", []))

        for item in records:
            datetime_value = item.get("datetime") or item.get("time")
            solar_value = (
                item.get("value")
                or item.get("powerProduction")
                or item.get("generation")
                or item.get("solar")
            )

            all_rows.append(
                {
                    "datetime": datetime_value,
                    "country": country,
                    "solar_generation": solar_value,
                    "source": "Electricity Maps",
                }
            )

    return pd.DataFrame(all_rows)


def download_solar_generation(start_date, end_date):
    """
    Download solar electricity generation data for Spain, France and Germany.
    """
    country_dataframes = []

    for country in COUNTRIES:
        print(f"Downloading solar data for {country}...")
        country_df = fetch_solar_data_for_country(country, start_date, end_date)
        country_dataframes.append(country_df)

    solar_df = pd.concat(country_dataframes, ignore_index=True)
    solar_df["datetime"] = pd.to_datetime(solar_df["datetime"])
    solar_df["solar_generation"] = pd.to_numeric(
        solar_df["solar_generation"], errors="coerce"
    )

    return solar_df


def calculate_solar_statistics(solar_df):
    """
    Calculate mean, maximum, minimum and standard deviation by country.
    """
    statistics = (
        solar_df.groupby("country")["solar_generation"]
        .agg(["mean", "max", "min", "std"])
        .rename(
            columns={
                "mean": "average_solar_generation",
                "max": "maximum_solar_generation",
                "min": "minimum_solar_generation",
                "std": "solar_generation_std",
            }
        )
    )

    return statistics


def calculate_daily_solar_generation(solar_df):
    """
    Calculate daily average solar generation by country.
    """
    daily_df = solar_df.copy()
    daily_df["date"] = daily_df["datetime"].dt.date

    daily_solar = (
        daily_df.groupby(["date", "country"])["solar_generation"]
        .mean()
        .reset_index()
    )

    return daily_solar


def plot_daily_solar_generation(daily_solar):
    """
    Plot daily solar generation for the three countries.
    """
    for country in daily_solar["country"].unique():
        country_data = daily_solar[daily_solar["country"] == country]

        plt.figure(figsize=(10, 5))
        plt.plot(country_data["date"], country_data["solar_generation"])
        plt.title(f"Daily Solar Generation - {country}")
        plt.xlabel("Date")
        plt.ylabel("Solar generation")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


def save_processed_data(solar_df):
    """
    Save processed solar data locally.
    """
    solar_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Processed solar data saved as {OUTPUT_FILE}")


def main():
    """
    Main execution for Imen's solar generation analysis.
    The assignment asks for a maximum of 3 months of hourly data.
    """
    start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 4, 1, tzinfo=timezone.utc)

    solar_df = download_solar_generation(start_date, end_date)

    print("\nFirst rows of solar data:")
    print(solar_df.head())

    statistics = calculate_solar_statistics(solar_df)
    print("\nSolar generation statistics by country:")
    print(statistics)

    daily_solar = calculate_daily_solar_generation(solar_df)
    print("\nDaily solar generation:")
    print(daily_solar.head())

    save_processed_data(solar_df)
    plot_daily_solar_generation(daily_solar)


if __name__ == "__main__":
    main()