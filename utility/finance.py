import datetime as dt
import numpy as np
import pandas as pd
import pickle
import math
import decimal
import copy
import pprint
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm
import pylab
import scipy.stats as ss
import statsmodels.api as sm
from functools import reduce
from sklearn.linear_model import LinearRegression
from decorators import my_time_decorator
from scipy.interpolate import interp1d, UnivariateSpline
import logging

# Paul Modules
from ols import OLS
from ols2 import OLS as MainOLS


Best_Betas = pickle.load(open('Best_Betas.pkl', 'rb'))
SPY_Betas_Raw = pickle.load(open('SPY_Betas_Raw.pkl', 'rb'))
SPY_Betas_Scrubbed = pickle.load(open('SPY_Betas_Scrubbed.pkl', 'rb'))

def daily_returns(price_table: 'df of prices') -> 'df of daily_returns':
    return price_table / price_table.shift(-1) - 1

def get_ETF_beta_to_SPY(ETF):
    ETF_betas = pickle.load(open('ETF_betas.pkl', 'rb'))
    try:
        beta = ETF_betas.loc[ETF, ('SPY', 'Beta')]
        return beta
    except:
        print("{} is not in the ETF beta table".format(ETF))
        return 1.0

def get_total_return(stock, lookback):
    stock_prices = PriceTable.loc[:, stock].head(lookback)
    stock_prices = stock_prices[stock_prices.notnull()]
    #print(stock_prices.to_string())
    start_price = stock_prices.iloc[-1]
    end_price = stock_prices.iloc[0]
    total_return = end_price / start_price - 1
    #print(start_price, end_price)
    return total_return

def get_num_days_above_cutoff(stock, lookback, cutoff, below_cutoff=False, absolute_value=False):
    stock_prices = PriceTable.loc[:, stock].head(lookback)
    stock_prices = stock_prices[stock_prices.notnull()]
    returns = daily_returns(stock_prices)
    if below_cutoff == False:
        if absolute_value == False:
            filtered_returns = returns[returns>cutoff]
        else:
            filtered_returns = returns[abs(returns)>cutoff]
    else:
        if absolute_value == False:
            filtered_returns = returns[returns<cutoff]
        else:
            filtered_returns = returns[abs(returns)<cutoff]
    
    total_days = len(returns.tolist())
    filtered_days = len(filtered_returns.tolist())
    #print(type(returns))
    #print(filtered_days, total_days)
    return filtered_days / total_days

if _name__ == '__main__':
    num = get_num_days_above_cutoff('SPY', 450, .005, absolute_value = True)
    #print(num)

    num = get_num_days_above_cutoff('SPY', 450, -.01, below_cutoff=True)
    #print(num)
