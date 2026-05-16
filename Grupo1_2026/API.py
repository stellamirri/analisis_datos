from entsoe import EntsoePandasClient
import pandas as pd
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


prices = client.query_day_ahead_prices(
    country_code='ES',
    start=start,
    end=end
)

prices = prices.to_frame(name='price')
####The day ahead prices are getting gathered

###NEGATIVE PRICE for spain

neg_prices_sp = df[df['Spain'] < 0]

print(neg_prices_sp)
#No negative price from this period
amplitude = df['Spain'].max() - df['Spain'].min()

##SPREAD GEOGRAPHIQUE / TRADING ????

# =========================
# SOLAR GENERATION
# =========================

generation = client.query_generation(
    country_code='ES',
    start=start,
    end=end,
    psr_type=None
)


solar = generation[('Solar', 'Actual Aggregated')]

solar = solar.to_frame(name='solar_mw')

df = prices.join(solar, how='inner')

# Remove NaN
df = df.dropna()

# =========================
# CAPTURE PRICE
# =========================

capture_price = (
    (df['price'] * df['solar_mw']).sum()
    / df['solar_mw'].sum()
)

print(f"Solar Capture Price Spain: {capture_price:.2f} €/MWh")

# =========================
# BASELOAD PRICE
# =========================

baseload_price = df['price'].mean()

print(f"Baseload Price: {baseload_price:.2f} €/MWh")

# =========================
# CAPTURE RATE
# =========================

capture_rate = capture_price / baseload_price

print(f"Capture Rate: {capture_rate:.2%}")

# =========================
# NEGATIVE PRICE HOURS
# =========================

negative_hours = (df['price'] < 0).sum()

print(f"Negative price hours: {negative_hours}")

# =========================
# SOLAR PRODUCTION DURING NEGATIVE PRICES
# =========================

solar_negative = df[df['price'] < 0]['solar_mw'].sum()

solar_total = df['solar_mw'].sum()

share_negative = solar_negative / solar_total

print(f"Solar generation during negative prices: {share_negative:.2%}")



