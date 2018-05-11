import numpy as np
import datetime as dt
import pandas as pd
import pickle
import copy
import pprint
from pprint import pprint
import decimal
import statsmodels.formula.api as sm
from sklearn.linear_model import LinearRegression
from collections import namedtuple
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import scipy.stats as ss
import statsmodels.api as sm
from ols import OLS
from ols2 import OLS as MainOLS
from paul_resources import PriceTable, daily_returns, tprint
from decorators import my_time_decorator
import copy
from beta_class import Beta, ScrubParams
from StockLine_Module import StockLineSimple, StockLineBetaAdjusted, StockChart

if __name__ == '__Main__':
    stock = 'ABBV'
    index = 'XLV'
    beta_lookback = 400
    lookback = beta_lookback
    scrub_params = ScrubParams(.075, .01, .8)
    beta = Beta(stock, index, beta_lookback, scrub_params).beta

    stock_line = StockLineBetaAdjusted(stock, lookback, beta, index)
    adjusted_returns = stock_line.adjusted_returns
    #print(adjusted_returns)

class Beta_StepTwo(Beta):
    def __init__(self,
                 stock: 'str',
                 index: 'str',
                 lookback: 'int',
                 ScrubParams: 'obj'):
        super().__init__(stock, index, lookback, ScrubParams)
    
        beta_value = Beta(self.stock, self.index, self.lookback, self.ScrubParams).beta
        #print("{}, {}, Beta: {}".format(self.stock, self.index, beta_value))
        self.stock_line = copy.deepcopy(StockLineBetaAdjusted(self.stock, self.lookback, beta_value, self.index))
        self.adjusted_returns = self.stock_line.adjusted_returns
        self.adjusted_returns_df_column_name = self.stock_line.adjusted_returns_df_column_name
    
    """
    @property
    def stock_line(self):
        beta_value = Beta(self.stock, self.index, self.lookback, self.ScrubParams).beta
        print("{}, {}, Beta: {}".format(self.stock, self.index, beta_value))
        return copy.deepcopy(StockLineBetaAdjusted(self.stock, self.lookback, beta_value, self.index))

    @property
    def adjusted_returns(self):
        return self.stock_line.adjusted_returns
    
    @property
    def adjusted_returns_df_column_name(self):
        return self.stock_line.adjusted_returns_df_column_name
    """

    @property
    def initial_scrub(self):
        if self.ScrubParams.stock_cutoff:
            #print(self.stock, self.index)
            return self.daily_returns[abs(self.adjusted_returns[self.adjusted_returns_df_column_name]) <= self.ScrubParams.stock_cutoff]
            return self.daily_returns[abs(self.daily_returns[self.stock]) <= self.ScrubParams.stock_cutoff]
        else:
            return None


#def __init__(self, stock: 'str', lookback: 'int', beta: 'float', index: 'str', base = None):

if __name__ == '__main__':
    stock = 'ABBV'
    stock2 = 'PFE'
    index = 'XLV'
    beta_lookback = 252
    chart_lookback = beta_lookback

    base = 100
    beta = Beta_StepTwo(stock, index, beta_lookback, ScrubParams(.075, .01, .8)).beta
    beta2 = Beta_StepTwo(stock2, index, beta_lookback, ScrubParams(.075, .01, .8)).beta
    #beta = Beta(stock, index, beta_lookback, ScrubParams(.075, .01, .8)).beta
    #beta2 = Beta(stock2, index, beta_lookback, ScrubParams(.075, .01, .8)).beta
#beta, beta2 = 0.0, 0.0

# Stock Lines to plot
    stock_line = StockLineSimple(stock, chart_lookback, base)
    index_line = StockLineSimple(index, chart_lookback, base)
    stock_line_adj = StockLineBetaAdjusted(stock, chart_lookback, beta, index, base)
    tprint(stock_line_adj.prices_df.round(2))
    
    stock_line_adj2 = StockLineBetaAdjusted(stock2, chart_lookback, beta2, index, base)

    stock_lines = [stock_line.stock_line(color = 'red'),
                   index_line.stock_line(color = 'black'),
                   stock_line_adj.stock_line(color = 'blue'),
                   #stock_line_adj2.stock_line(color = 'c')
                   ]
    StockChart(stock_lines).run()

    Beta(stock, index, beta_lookback, ScrubParams(.075, .01, .8)).show_scrub_trajectory()
