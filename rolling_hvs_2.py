import numpy as np
import pandas as pd
import seaborn
import pickle
import copy
import pprint
import decimal
import statsmodels.formula.api as sm
from time_decorator import my_time_decorator
from paul_resources import tprint, rprint
from ols import OLS
import math
import datetime as dt
import matplotlib.pyplot as plt
import scipy.stats as ss
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from beta_class_6 import StockLineBetaAdjusted, Beta, ScrubParams
from functools import reduce

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
#price_table = pickle.load(open('sp500_price_table.pkl', 'rb')).head(2000)[['AAPL', 'SPY']]
#daily_returns = price_table / price_table.shift(-1) - 1

# Can Probably Delete This
#model = sm.OLS(daily_returns['AAPL'], daily_returns['SPY'], missing='drop')
#results = model.fit()
# Print Statements
# Head(500) returns 498 for results.df_resid. I want that number to be 499.
#print("Beta: {:.2f}, Corr.: {:.2f}, n = {:.0f}".format(results.params['SPY'], results.rsquared, results.df_resid))


# Calculate Adjusted Returns
# Configuration Parameters
stock = 'QQQ'
index = 'CL'
lookback = 2000
beta_lookback = 2000
scrub_params = ScrubParams(.1, .0125, .8)
beta_object = Beta(stock, index, beta_lookback, scrub_params)
beta = beta_object.beta
beta = 0

# Rolling Parameters
rolling_returns_window = 3
rolling_HVs_window = 5
fwd_rolling_HVs_window = 10

adj_stock_line = StockLineBetaAdjusted(stock, lookback, beta, index)
adjusted_returns = adj_stock_line.adjusted_returns
adjusted_returns_scrubbed = adj_stock_line.adjusted_returns_scrubbed(.1)

adjusted_returns_scrubbed_rolling = adjusted_returns_scrubbed[::-1].rolling(rolling_returns_window).sum()
rolling_HVs = adjusted_returns_scrubbed.iloc[::-1].rolling(window=rolling_HVs_window).std()*math.sqrt(252)
fwd_rolling_HVs = (adjusted_returns_scrubbed.iloc[::-1].rolling(window=fwd_rolling_HVs_window).std()*math.sqrt(252)).shift(-fwd_rolling_HVs_window)

vol = np.nanstd(adjusted_returns_scrubbed)*math.sqrt(252)
vol_of_vol = np.nanstd(rolling_HVs)
print("Vol: {:.3f}, Vol of Vol: {:.3f}, Beta: {:.3f}, n = {}".format(vol, vol_of_vol, beta, 500))

# Create DataFrame with Scatter Plot Information
dfs = [fwd_rolling_HVs, rolling_HVs, adjusted_returns_scrubbed_rolling]
scatter_plot_df = reduce(lambda left,right: left.merge(right, how='outer', left_index=True, right_index=True), dfs) 
scatter_plot_df.columns = ["Fwd_Rolling_HVs({})".format(fwd_rolling_HVs_window),
                           "Rolling_HVs({})".format(rolling_HVs_window),
                           "Rolling_Returns({})".format(rolling_returns_window)]

# Print head of the DataFrame
print(scatter_plot_df.loc[dt.date(2016, 1, 5):dt.date(2018, 3, 8), :].head(5).round(4))

# --------------------------------Scatter Plot Segment-----------------------------------------------------------
# x and y values to plot
y = scatter_plot_df.iloc[:, 0].values.tolist()
x = scatter_plot_df.iloc[:, 2].values.tolist()

# Searborn Parameters
y_values = pd.Series(data = y)
x_values = pd.Series(data = x)
mean_vol = pd.Series([vol for i in range(len(x_values))])

seaborn.set(rc={'figure.figsize':(6,5)})
seaborn.regplot(x = x_values, y = y_values)
seaborn.regplot(x = x_values, y = mean_vol)

# MatplotLib Parameters
#plt.scatter(x, y, label='skitscat', color='k')
plt.xlabel('Rolling HVs / Rolling Return')

plt.ylabel('Lagged Rolling HVs')
plt.title('Scatter Plot')
plt.legend()

plt.show()

# Can Probably Delete This
y = scatter_plot_df.iloc[:, [0]]
X = scatter_plot_df.iloc[:, [1, 2]]
X = sm.add_constant(X)

model = sm.OLS(y, X, missing='drop')
results = model.fit()

# Print Statements
print("Constant: {:.2f}, HVs: {:.2f}, Returns: {:.2f} Corr.: {:.2f}, n = {:.0f}".format(results.params['const'],
                                                                                        results.params["Rolling_HVs({})".format(rolling_HVs_window)],
                                                                                        results.params["Rolling_Returns({})".format(rolling_returns_window)],
                                                                                        results.rsquared,
                                                                                        results.df_resid))

print(results.params)
