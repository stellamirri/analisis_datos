# Renewables_price_correlation_3_countries
# Here we will analyze the correlation between renewable energy generation and electricity prices in Spain, France, and Germany. 
# We will use the data obtained by our group and perform statistical analysis to find patterns and insights.

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data_crudo_cor_ren import dfES as Price_ES
from data_crudo_cor_ren import dfFR as Price_FR
from data_crudo_cor_ren import dfDE as Price_DE

from Hydro_hourly_generation_3_countries import france_values as FR_hydro
from Hydro_hourly_generation_3_countries import germany_values as DE_hydro
from Hydro_hourly_generation_3_countries import spain_values as ES_hydro

from Solar_hourly_generation_3_countries_imen import solar_df as solar_generation

from Wind_hourly_generation_3_countries import france_values as FR_wind
from Wind_hourly_generation_3_countries import germany_values as DE_wind
from Wind_hourly_generation_3_countries import spain_values as ES_wind

from Mix_hourly_generation_3_countries import france_values as FR_mix
from Mix_hourly_generation_3_countries import germany_values as DE_mix
from Mix_hourly_generation_3_countries import spain_values as ES_mix

