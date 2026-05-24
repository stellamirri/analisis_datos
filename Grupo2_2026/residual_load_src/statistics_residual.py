import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]

countries = ["Spain", "France", "Germany"]

processed_dir = base_dir / "residual_load_data" / "processed"

results = []

for country in countries:
    file = processed_dir / f"{country}_residual_load.csv"

    df = pd.read_csv(file)

    stats = {
        "country": country,
        "mean_residual_load": df["residual_load"].mean(),
        "std_residual_load": df["residual_load"].std(),
        "min_residual_load": df["residual_load"].min(),
        "max_residual_load": df["residual_load"].max(),
        "median_residual_load": df["residual_load"].median()
    }

    results.append(stats)

summary = pd.DataFrame(results)

output = processed_dir / "residual_load_statistics.csv"

summary.to_csv(output, index=False)

print(summary)
print("Saved:", output)