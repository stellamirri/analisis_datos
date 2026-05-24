import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

API_KEY = "gHCKjHZ6f2AvhZKfCqg7"

countries = {
    "Spain": "ES",
    "France": "FR",
    "Germany": "DE"
}

url = "https://api.electricitymaps.com/v4/total-load/past-range"

headers = {
    "auth-token": API_KEY
}

start_date = datetime(2026, 2, 23)
end_date = datetime(2026, 5, 23)

step = timedelta(days=10)

base_dir = Path(__file__).resolve().parents[1]
output_dir = base_dir / "residual_load_data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)

for country, zone in countries.items():
    all_data = []
    current_start = start_date

    while current_start < end_date:
        current_end = min(current_start + step, end_date)

        params = {
            "zone": zone,
            "start": current_start.strftime("%Y-%m-%dT00:00:00Z"),
            "end": current_end.strftime("%Y-%m-%dT00:00:00Z")
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        data = response.json()

        if isinstance(data, list):
            all_data.extend(data)
        elif isinstance(data, dict) and "data" in data:
            all_data.extend(data["data"])
        elif isinstance(data, dict) and "history" in data:
            all_data.extend(data["history"])
        else:
            print("Unexpected data:", data)

        print(f"{country}: {current_start} -> {current_end}")

        current_start = current_end

    df = pd.DataFrame(all_data)

    filename = output_dir / f"{country}_3months_load.csv"

    print("Rows:", len(df))
    print("Saving to:", filename)

    df.to_csv(filename, index=False)

    print(f"{country} saved!")