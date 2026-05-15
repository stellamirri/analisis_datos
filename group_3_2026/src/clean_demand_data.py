import pandas as pd

#Loading Spain data

spain_tables = pd.read_html(
    "data/raw/data_spain_april_to_june.xls"
)

spain_df = spain_tables[0]

print("Spain data loaded")
print(spain_df.head())


#Loading France data

france_df = pd.read_csv(
    "data/raw/France_demand_year_2024.csv",
    sep="\t",
    encoding="latin1"
)

print("France data loaded")
print(france_df.head())


#Loading Germany data

germany_df = pd.read_csv(
    "data/raw/hourly_consumption_germany_april_june.csv",
    sep=";",
    encoding="latin1"
)

print("Germany data loaded")
print(germany_df.head())