import os
from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
import pandas as pd
import requests


# Electricity Maps API key
API_KEY = os.getenv("ELECTRICITY_MAPS_API_KEY")

if not API_KEY:
    raise ValueError(
        "Missing API key. Please set ELECTRICITY_MAPS_API_KEY as an environment variable."
    )

# Countries required for the assignment:
# Spain = ES, France = FR, Germany = DE
COUNTRIES = ["ES", "FR", "DE"]

SOURCE_TYPE = "solar"
BASE_URL = "https://api.electricitymaps.com/v4/electricity-mix"
OUTPUT_FILE = "Solar_hourly_generation_3_countries_imen.csv"


def split_date_range(start_date, end_date, chunk_days=10):
    """
    Split a long period into chunks of maximum 10 days.
    Electricity Maps limits hourly past-range requests to 10 days.
    """
    current_start = start_date

    while current_start < end_date:
        current_end = min(current_start + timedelta(days=chunk_days), end_date)
        yield current_start, current_end
        current_start = current_end


def extract_solar_value(record):
    """
    Extract solar generation from one API record.

    Electricity Maps returns the electricity mix inside the 'mix' field.
    Solar generation is stored as record["mix"]["solar"].
    """

    if "mix" in record and isinstance(record["mix"], dict):
        return record["mix"].get("solar")

    if "powerProductionBreakdown" in record:
        breakdown = record["powerProductionBreakdown"]
        if isinstance(breakdown, dict):
            return breakdown.get("solar")

    if "powerConsumptionBreakdown" in record:
        breakdown = record["powerConsumptionBreakdown"]
        if isinstance(breakdown, dict):
            return breakdown.get("solar")

    for key in ["value", "powerProduction", "generation", "solar"]:
        if key in record and record[key] is not None:
            return record[key]

    return None


def extract_datetime(record):
    """
    Extract datetime from one API record.
    """
    for key in ["datetime", "time", "createdAt", "updatedAt"]:
        if key in record and record[key] is not None:
            return record[key]

    return None


def fetch_solar_data_for_country(country, start_date, end_date):
    """
    Download hourly solar generation data for one country.
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
            "flowTraced": "false",
        }

        print(
            f"Downloading {country}: "
            f"{params['start']} to {params['end']}"
        )

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(
                f"API error for {country}: "
                f"{response.status_code} - {response.text}"
            )

        data = response.json()

        # The time series is usually in "history", but this keeps it flexible.
        records = data.get("history", data.get("data", []))

        if not records:
            print(f"Warning: no records returned for {country} in this period.")
            continue

        # Debug only once per country/chunk, useful if API structure changes
        print("Example API record:")
        print(records[0])

        for record in records:
            datetime_value = extract_datetime(record)
            solar_value = extract_solar_value(record)

            all_rows.append(
                {
                    "datetime": datetime_value,
                    "country": country,
                    "solar_generation_mw": solar_value,
                    "source": "Electricity Maps",
                }
            )

    return pd.DataFrame(all_rows)


def download_solar_generation(start_date, end_date):
    """
    Download solar generation data for Spain, France and Germany.
    """
    country_dataframes = []

    for country in COUNTRIES:
        print(f"\nDownloading solar data for {country}...")
        country_df = fetch_solar_data_for_country(country, start_date, end_date)
        country_dataframes.append(country_df)

        solar_df = pd.concat(country_dataframes, ignore_index=True)
        solar_df = solar_df.drop_duplicates().reset_index(drop=True)

        solar_df["datetime"] = pd.to_datetime(solar_df["datetime"], errors="coerce")
        solar_df["solar_generation_mw"] = pd.to_numeric(
        solar_df["solar_generation_mw"], errors="coerce"
    )

    # Remove rows without datetime
    solar_df = solar_df.dropna(subset=["datetime"])

    return solar_df


def calculate_solar_statistics(solar_df):
    """
    Calculate basic solar generation statistics by country.
    """
    statistics = (
        solar_df.groupby("country")["solar_generation_mw"]
        .agg(["mean", "max", "min", "std"])
        .rename(
            columns={
                "mean": "average_solar_generation_mw",
                "max": "maximum_solar_generation_mw",
                "min": "minimum_solar_generation_mw",
                "std": "solar_generation_std_mw",
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
        daily_df.groupby(["date", "country"])["solar_generation_mw"]
        .mean()
        .reset_index()
    )

    return daily_solar


def calculate_total_solar_generation(solar_df):
    """
    Calculate total solar generation by country for the analysed period.
    """
    total_solar = (
        solar_df.groupby("country")["solar_generation_mw"]
        .sum()
        .reset_index()
        .rename(columns={"solar_generation_mw": "total_solar_generation_mw"})
    )

    return total_solar

def identify_highest_average_solar_country(statistics):
    """
    Identify the country with the highest average solar generation
    during the analysed period.
    """
    highest_country = statistics["average_solar_generation_mw"].idxmax()
    highest_value = statistics.loc[
        highest_country, "average_solar_generation_mw"
    ]

    return highest_country, highest_value


def plot_daily_solar_generation(daily_solar):
    """
    Plot daily solar generation for ES, FR and DE in the same figure.
    """
    plt.figure(figsize=(12, 6))

    for country in daily_solar["country"].unique():
        country_data = daily_solar[daily_solar["country"] == country]
        plt.plot(
            country_data["date"],
            country_data["solar_generation_mw"],
            label=country,
        )

    plt.title("Daily Average Solar Generation - ES, FR and DE")
    plt.xlabel("Date")
    plt.ylabel("Solar generation (MW)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_hourly_solar_generation(solar_df):
    """
    Plot hourly solar generation for each country.
    """
    for country in solar_df["country"].unique():
        country_data = solar_df[solar_df["country"] == country]

        plt.figure(figsize=(12, 5))
        plt.plot(
            country_data["datetime"],
            country_data["solar_generation_mw"],
            label=country,
        )
        plt.title(f"Hourly Solar Generation - {country}")
        plt.xlabel("Datetime")
        plt.ylabel("Solar generation (MW)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()


def save_processed_data(solar_df):
    """
    Save processed solar data locally.
    The CSV should not be uploaded to GitHub.
    """
    solar_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nProcessed solar data saved as {OUTPUT_FILE}")


def main():
    """
    Main execution for Imen's solar generation analysis.

    The assignment asks for hourly data over a maximum of 3 months.
    Here we analyse January, February and March 2026.
    """
    start_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2026, 4, 1, tzinfo=timezone.utc)

    solar_df = download_solar_generation(start_date, end_date)

    print("\nFirst rows of solar data:")
    print(solar_df.head())

    print("\nMissing values in solar_generation_mw:")
    print(solar_df["solar_generation_mw"].isna().sum())

    statistics = calculate_solar_statistics(solar_df)
    print("\nSolar generation statistics by country:")
    print(statistics)

    highest_country, highest_value = identify_highest_average_solar_country(statistics)
    print(
    f"\nCountry with the highest average solar generation: "
    f"{highest_country} ({highest_value:.2f} MW)")

    total_solar = calculate_total_solar_generation(solar_df)
    print("\nTotal solar generation by country:")
    print(total_solar)

    daily_solar = calculate_daily_solar_generation(solar_df)
    print("\nDaily solar generation:")
    print(daily_solar.head())

    save_processed_data(solar_df)

    plot_daily_solar_generation(daily_solar)
    plot_hourly_solar_generation(solar_df)


if __name__ == "__main__":
    main()