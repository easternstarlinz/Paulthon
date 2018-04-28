import numpy as np
import pandas as pd
import seaborn
import pickle
import copy
import pprint
import decimal
import statsmodels.formula.api as sm
from time_decorator import my_time_decorator
from ols import OLS
import math
import datetime as dt
import matplotlib.pyplot as plt
import scipy.stats as ss
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from beta_class_6 import StockLineBetaAdjusted, Beta, ScrubParams

"""OLS model from statsmodels.api as sm
    .df_model # Degrees of Freedom of the Model
    .df_resid; # Degrees of Freedom of the Residuals
    model.endog_names
    model.exog_names

Deprecation Warning:
pandas_new.py:45: FutureWarning: pd.rolling_mean is deprecated for DataFrame and will be removed in a future version, replace with 
    DataFrame.rolling(center=False,window=5).mean()
      rolling_mean = pd.rolling_mean(price_table.iloc[::-1], window = 5).round(2)


Deleted lines of code that may be interesting:
filtered_data = daily_returns[np.isfinite(daily_returns['SPY'])]   .exog_names
price_table_reversed = price_table.iloc[::-1]
rolling_HVs = np.nanstd(daily_returns['SPY'])
rolling_mean = price_table.iloc[::-1].rolling(window=5).mean()
"""


# Import Price Table as Pandas DataFrame from Pickle File for S&P500 + Discretionary Symbols
price_table = pickle.load(open('sp500_price_table.pkl', 'rb')).head(2000)[['AAPL', 'SPY']]
daily_returns = price_table / price_table.shift(-1) - 1
model = sm.OLS(daily_returns['AAPL'], daily_returns['SPY'], missing='drop')
results = model.fit()

# Calculate Adjusted Returns
stock = 'SPY'
index = 'CL'
lookback = 2000
rolling_window = 10
scrub_params = ScrubParams(.1, .0125, .8)
beta_lookback = 2000

beta_object = Beta(stock, index, beta_lookback, scrub_params)
beta = beta_object.beta
beta = 0
adj_stock_line = StockLineBetaAdjusted(stock, lookback, beta, index)
adjusted_returns = adj_stock_line.adjusted_returns
adjusted_returns_scrubbed = adj_stock_line.adjusted_returns_scrubbed(.1)
adjusted_returns_scrubbed_rolling = adjusted_returns_scrubbed[::-1].rolling(rolling_window).sum()
adjusted_returns_scrubbed_rolling = adjusted_returns_scrubbed[::-1].rolling(1).sum()
print(adjusted_returns_scrubbed[::-1].head())
print(adjusted_returns_scrubbed_rolling.head())
# Calculate n-Day Rolling HVs.
rolling_HVs = adjusted_returns_scrubbed.iloc[::-1].rolling(window=rolling_window).std()*math.sqrt(252)
#print(rolling_HVs[::-1].head(500))
#rolling_HVs = daily_returns.rolling(window=rolling_window).std()*math.sqrt(252)

# Print Statements
# Head(500) returns 498 for results.df_resid. I want that number to be 499.
#print("Beta: {:.2f}, Corr.: {:.2f}, n = {:.0f}".format(results.params['SPY'], results.rsquared, results.df_resid))

vol = np.nanstd(adjusted_returns_scrubbed)*math.sqrt(252)
vol_of_vol = np.nanstd(rolling_HVs)
print("Vol: {:.3f}, Vol of Vol: {:.3f}, Beta: {:.3f}, n = {}".format(vol, vol_of_vol, beta, 500))

rolling_HVs_shifted = rolling_HVs.shift(-rolling_window)
rolling_HVs_shifted = rolling_HVs.shift(-rolling_window)
scatter_plot_df = pd.merge(rolling_HVs, rolling_HVs_shifted, left_index=True, right_index=True)
#scatter_plot_df = pd.merge(adjusted_returns_scrubbed_rolling, rolling_HVs_shifted, left_index=True, right_index=True)
scatter_plot_df = pd.merge(scatter_plot_df, adjusted_returns_scrubbed_rolling, left_index=True, right_index=True)


print(scatter_plot_df.loc[dt.date(2016, 1, 19):dt.date(2018, 3, 8), :].head(5))

x = scatter_plot_df.iloc[:, 0].values.tolist()
y = scatter_plot_df.iloc[:, 1].values.tolist()

#plt.scatter(x, y, label='skitscat', color='k')

#plt.xlabel('Rolling HVs')
#plt.ylabel('Lagged Rolling HVs')
#plt.title('Scatter Plot')
#plt.legend()
#plt.show()

seaborn.set(rc={'figure.figsize':(6,5)})
x_values = pd.Series(data = x)
y_values = pd.Series(data = y)

mean_vol = pd.Series([vol for i in range(len(x_values))])

seaborn.regplot(x = x_values, y = y_values)
seaborn.regplot(x = x_values, y = mean_vol)

plt.xlabel('Rolling HVs')
plt.ylabel('Lagged Rolling HVs')
plt.title('Scatter Plot')
plt.legend()

plt.show()
