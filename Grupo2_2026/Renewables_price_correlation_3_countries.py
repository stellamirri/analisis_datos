# Renewables_price_correlation_3_countries
# Here we will analyze the correlation between renewable energy generation and electricity prices in Spain, France, and Germany. 
# We will use the data obtained by our group and perform statistical analysis to find patterns and insights.

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from Data_crudo_cor_ren import dfES as Price_ES
from Data_crudo_cor_ren import dfFR as Price_FR
from Data_crudo_cor_ren import dfDE as Price_DE

from Hydro_hourly_generation_3_countries import france_values as FR_hydro
from Hydro_hourly_generation_3_countries import germany_values as DE_hydro
from Hydro_hourly_generation_3_countries import spain_values as ES_hydro

from Solar_hourly_generation_3_countries_imen import solar_df as solar_generation

from Wind_hourly_generation_3_countries import france_values as FR_wind
from Wind_hourly_generation_3_countries import germany_values as DE_wind
from Wind_hourly_generation_3_countries import spain_values as ES_wind

from Mix_hourly_generation_3_countries import mix_df as mix_generation

data_consolidada = []

paises_data = [
    {"name": "Spain", "price": Price_ES, "solar": solar_generation['ES'], "wind": ES_wind, "hydro": ES_hydro, "mix": mix_generation['ES']},
    {"name": "France", "price": Price_FR, "solar": solar_generation['FR'], "wind": FR_wind, "hydro": FR_hydro, "mix": mix_generation['FR']},
    {"name": "Germany", "price": Price_DE, "solar": solar_generation['DE'], "wind": DE_wind, "hydro": DE_hydro, "mix": mix_generation['DE']}
]

for p in paises_data:
    
    df = pd.merge(p['price'], p['solar'], on='datetime')
    df = pd.merge(df, p['wind'], on='datetime')
    df = pd.merge(df, p['hydro'], on='datetime')
    df = pd.merge(df, p['mix'], on='datetime')
    
    
    df['pct_solar'] = (df['solar'] / df['mix']) * 100
    df['pct_wind'] = (df['wind'] / df['mix']) * 100
    df['pct_hydro'] = (df['hydro'] / df['mix']) * 100
    df['pct_renovables'] = df['pct_solar'] + df['pct_wind'] + df['pct_hydro']
    df['pais'] = p['nombre']
    
    data_consolidada.append(df)


df_final = pd.concat(data_consolidada)

fuentes = ['solar', 'wind', 'hydro']

for f in fuentes:
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df_final, x=f'pct_{f}', y='value', hue='pais', alpha=0.6)
    plt.title(f'Correlation: Price vs % of renewable {f.capitalize()}')
    plt.show()


plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_final, x='pct_renovables', y='value', hue='pais')
plt.title('Price vs % Total Renewables')
plt.show()


plt.figure(figsize=(10, 6))
sns.regplot(data=df_final, x='pct_renovables', y='value', color='purple')
plt.title('General Trend: Price vs % Renewables')
plt.show()
