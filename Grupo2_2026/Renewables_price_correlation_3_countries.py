# Renewables_price_correlation_3_countries
# Here we will analyze the correlation between renewable energy generation and electricity prices in Spain, France, and Germany. 
# We will use the data obtained by our group and perform statistical analysis to find patterns and insights.

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data_crudo_cor_ren import dfES as Price_ES
from data_crudo_cor_ren import dfFR as Price_FR
from data_crudo_cor_ren import dfDE as Price_DE
