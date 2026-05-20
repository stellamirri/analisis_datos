from entsoe import EntsoePandasClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#DL the module entsoe 

client = EntsoePandasClient(
    api_key='5bcf63bf-87d7-4aa5-8bfb-040cbc4c4af0'
)


##This is my token 
start = pd.Timestamp(
    '2025-01-01',
    tz='Europe/Brussels'
)

end = pd.Timestamp(
    '2025-03-01',
    tz='Europe/Brussels'
)

es = client.query_day_ahead_prices(
    'ES',
    start=start,
    end=end
)

fr = client.query_day_ahead_prices(
    'FR',
    start=start,
    end=end
)

df = pd.DataFrame({
    'Spain': es,
    'France': fr
})

print(df.head())

####The day ahead prices are getting gathered

###NEGATIVE PRICE for spain

neg_prices_sp = df[df['Spain'] < 0]

print(neg_prices_sp)
#No negative price from this period
amplitude = df['Spain'].max() - df['Spain'].min()

##SPREAD GEOGRAPHIQUE / TRADING ????


