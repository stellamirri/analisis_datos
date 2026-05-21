import requests
import pandas as pd
import matplotlib.pyplot as plt

API_KEY = "patCytbSzwwY9ZZhgner"

url = "https://api.electricitymaps.com/v3/electricity-source/hydro/past-range"

headers = {
"auth-token": API_KEY
}

params1 = {
    "zone": "FR",
    "start": "2026-01-02T00:00:00.000Z",
    "end": "2026-03-01T00:00:00.000Z",
    "temporalGranularity": "daily"
}



response1 = requests.get(url, headers=headers, params=params1)

data1 = response1.json()


rows1 = data1["data"]

df1 = pd.json_normalize(rows1)


df1 = df1[["datetime", "value"]]



df1["datetime"] = pd.to_datetime(df1["datetime"])
df1["day"] = df1["datetime"].dt.day
df1["value"] = df1["value"]/1000


france_values = df1["value"]


bar_width = 0.35
x = range(len(df1["datetime"]))



plt.figure(figsize=(7, 3))
plt.bar([i for i in x], france_values, width=bar_width, label = "France", color = "blue")
plt.title("Hydroelectricity generation per day France (January-March 2026)")
plt.xlabel("Day")
plt.ylabel("Hydroelectricity Generation (GWh)/day ")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(x, df1["day"])
plt.legend()
plt.tight_layout()

plt.figtext(
    0.5,  
    0.01,
    "Source : API Electricity Maps.",
    ha="center",  
    fontsize=9, 
    bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5}  
)


plt.show()
