import pandas as pd
from pathlib import Path
import ast

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

    # Extract solar, wind, hydro from the mix dictionary column
    mix_df["mix"] = mix_df["mix"].apply(ast.literal_eval)

    mix_df["solar"] = mix_df["mix"].apply(lambda x: x.get("solar", 0))
    mix_df["wind"] = mix_df["mix"].apply(lambda x: x.get("wind", 0))
    mix_df["hydro"] = mix_df["mix"].apply(lambda x: x.get("hydro", 0))

    merged = pd.merge(
        load_df[["datetime", "value"]],
        mix_df[["datetime", "solar", "wind", "hydro"]],
        on="datetime",
        how="inner"
    )

    merged["renewable_generation"] = (
        merged["solar"] + merged["wind"] + merged["hydro"]
    )

    merged["renewable_share"] = (
        merged["renewable_generation"] / merged["value"]
    )

    output = processed_dir / f"{country}_renewable_share.csv"

    merged.to_csv(output, index=False)

    print(country, "renewable share saved!")