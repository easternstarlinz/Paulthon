import datetime as dt
import pandas as pd
import math
import numpy as np
import random
import copy
import matplotlib.pyplot as plt
from collections import namedtuple
from statistics import mean
from paul_resources import InformationTable, tprint, rprint
from decorators import my_time_decorator
from py_vollib.black_scholes.implied_volatility import black_scholes, implied_volatility

"""
-Option: NamedTuple
    -Params:
        -Option_Type: 'str'
        -Strike: 'float'
        -Expiry: 'Datetime'

-OptionPrice: Function
    -Params:
        -Option: 'NamedTuple'
        -Distribution: 'Object'
    -Returns->
        -'Float'
        -Content: Option Price 
"""

Option = namedtuple('Option', ['Option_Type', 'Strike', 'Expiry'])

def OptionPrice(Option, Distribution):
    if Option.Option_Type == 'Call':
        return sum([state.Prob*max(state.Relative_Price - Option.Strike, 0) for state in Distribution.distribution_df.itertuples()])

    if Option.Option_Type == 'Put':
        return sum([state.Prob*max(Option.Strike - state.Relative_Price, 0) for state in Distribution.distribution_df.itertuples()])

def OptionPriceMC(Option, MC_Results):
    if Option.Option_Type == 'Call':
        return np.average(np.maximum(MC_Results - Option.Strike, np.zeros(len(MC_Results))))
    
    if Option.Option_Type == 'Put':
        return np.average(np.maximum(Option.Strike - MC_Results, np.zeros(len(MC_Results))))

def get_time_to_expiry(expiry: 'dt.date', ref_date = dt.date.today()):
    if isinstance(expiry, dt.datetime):
        expiry = expiry.date()
    return  max((expiry - ref_date).days/365, 0)

def get_implied_volatility(Option,
                           option_price,
                           underlying_price = None,
                           interest_rate = None,
                           reference_date = None):

    if underlying_price is None:
        underlying_price = 1

    if interest_rate is None:
        interest_rate = 0

    if reference_date is None:
        reference_date = dt.date.today()
    
    price = option_price
    S = underlying_price
    K = Option.Strike
    r = interest_rate
    flag = Option.Option_Type.lower()[0]
    t = get_time_to_expiry(Option.Expiry)
    
    if S <= .05:
        return 0

    if flag == 'c':
        if S - K > price or price/S > .9:
            return 0
    else:
        if K - S > price or price/S > .9:
            return 0

    if price < .01:
        return 0

    #print("Strike: {}{}, Underlying: {:.2f}, Option: {:.2f}".format(K, flag, S, price))
    #print(price, S, K, t, r, flag) 
    return implied_volatility(price, S, K, t, r, flag)
