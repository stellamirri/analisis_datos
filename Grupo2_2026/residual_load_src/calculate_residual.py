import pandas as pd
from pathlib import Path

countries = ["Spain", "France", "Germany"]

base_dir = Path(__file__).resolve().parents[1]

raw_dir = base_dir / "residual_load_data" / "raw"
processed_dir = base_dir / "residual_load_data" / "processed"

for country in countries:
    load_file = raw_dir / f"{country}_3months_load.csv"
    mix_file = processed_dir / f"{country}_3months_mix.csv"

    load = pd.read_csv(load_file)
    mix = pd.read_csv(mix_file)

    load["datetime"] = pd.to_datetime(load["datetime"])
    mix["datetime"] = pd.to_datetime(mix["datetime"])

    mix["solar"] = mix["mix"].apply(lambda x: eval(x).get("solar", 0))
    mix["wind"] = mix["mix"].apply(lambda x: eval(x).get("wind", 0))
    mix["hydro"] = mix["mix"].apply(lambda x: eval(x).get("hydro", 0))

    df = pd.merge(
        load[["datetime", "value"]],
        mix[["datetime", "solar", "wind", "hydro"]],
        on="datetime",
        how="inner"
    )

    df["renewable_generation"] = df["solar"] + df["wind"] + df["hydro"]
    df["residual_load"] = df["value"] - df["renewable_generation"]

    output_file = processed_dir / f"{country}_residual_load.csv"

    df.to_csv(output_file, index=False)

    print(f"{country} residual load saved!")