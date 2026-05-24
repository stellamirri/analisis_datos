import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]

processed_dir = base_dir / "residual_load_data" / "processed"

countries = ["Spain", "France", "Germany"]

plt.figure(figsize=(15,5))

for country in countries:
    file = processed_dir / f"{country}_renewable_share.csv"

    df = pd.read_csv(file)
    df["datetime"] = pd.to_datetime(df["datetime"])

    plt.plot(
        df["datetime"],
        df["renewable_share"],
        label=country
    )

plt.title("Renewable Share Comparison")

plt.xlabel("Datetime")
plt.ylabel("Renewable Share")

plt.legend()
plt.grid(True)

output = processed_dir / "compare_renewable_share.png"

plt.savefig(output)

print("Saved:", output)

plt.show()