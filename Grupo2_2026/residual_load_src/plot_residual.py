import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]

file = base_dir / "residual_load_data" / "processed" / "Spain_residual_load.csv"

df = pd.read_csv(file)

df["datetime"] = pd.to_datetime(df["datetime"])

plt.figure(figsize=(15,5))

plt.plot(df["datetime"], df["residual_load"])

plt.title("Spain Residual Load")

plt.xlabel("Datetime")

plt.ylabel("Residual Load")

plt.grid(True)

# 保存图片
output = base_dir / "residual_load_data" / "processed" / "Spain_residual_load.png"

plt.savefig(output)

print("Plot saved:", output)

plt.show()