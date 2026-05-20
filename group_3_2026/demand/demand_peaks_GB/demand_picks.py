import pandas as pd

# loading the cleaned data for France, Germany, and Spain
df_fr = pd.read_csv("data\\processed\\france_cleaned.csv")
df_de = pd.read_csv("data\\processed\\germany_cleaned.csv")
df_es = pd.read_csv("data\\processed\\spain_cleaned.csv")


# converting the datetime column to datetime format
for df in [df_fr, df_de, df_es]:
    df["datetime"] = pd.to_datetime(df["datetime"])


# function to analyze peaks in the demand data for a given country
def analyze_peaks(df, country_name):
    
    # global peak value and time
    peak_value = df["demand_mwh"].max()
    peak_time = df.loc[df["demand_mwh"].idxmax(), "datetime"]
    
    # Top 5 peaks
    top_peaks = df.nlargest(5, "demand_mwh")[["datetime", "demand_mwh"]]
    
    # day with the highest demand
    daily_max = df.groupby(df["datetime"].dt.date)["demand_mwh"].max()
    max_day = daily_max.idxmax()
    max_day_value = daily_max.max()


    print(f"\n===== {country_name} =====")
    print(f"Peak max : {peak_value:.0f} MWh")
    print(f"Date du peak : {peak_time}")
    print(f"Peak journalier max : {max_day_value:.0f} MWh (le {max_day})")
    
    print("\nTop 5 peaks :")
    print(top_peaks)
    
    return peak_value, peak_time

#Analyzing peaks for each country
analyze_peaks(df_fr, "France")
analyze_peaks(df_de, "Germany")
analyze_peaks(df_es, "Spain")


import matplotlib.pyplot as plt

def plot_demand(df, country):
    plt.figure(figsize=(12,4))
    plt.plot(df["datetime"], df["demand_mwh"])
    
    # Peak
    peak_idx = df["demand_mwh"].idxmax()
    plt.scatter(df.loc[peak_idx, "datetime"],
                df.loc[peak_idx, "demand_mwh"],
                color="red", label="Peak")
    
    plt.title(f"Electricity demand - {country}")
    plt.xlabel("Time")
    plt.ylabel("Demand (MWh)")
    plt.legend()
    plt.tight_layout()
    plt.show()

plot_demand(df_fr, "France")
plot_demand(df_de, "Germany")
plot_demand(df_es, "Spain")