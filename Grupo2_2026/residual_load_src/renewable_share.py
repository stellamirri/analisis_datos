import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]

countries = ["Spain", "France", "Germany"]

processed_dir = base_dir / "residual_load_data" / "processed"
raw_dir = base_dir / "residual_load_data" / "raw"

for country in countries:

    load_file = raw_dir / f"{country}_3months_load.csv"
    mix_file = processed_dir / f"{country}_3months_mix.csv"

    load_df = pd.read_csv(load_file)
    mix_df = pd.read_csv(mix_file)

    load_df["datetime"] = pd.to_datetime(load_df["datetime"])
    mix_df["datetime"] = pd.to_datetime(mix_df["datetime"])

    merged = pd.merge(
        load_df,
        mix_df,
        on="datetime",
        how="inner"
    )

    merged["renewable_share"] = (
        merged["solar"]
        + merged["wind"]
        + merged["hydro"]
    ) / merged["value"]

    output = processed_dir / f"{country}_renewable_share.csv"

    merged.to_csv(output, index=False)

    print(country, "renewable share saved!")