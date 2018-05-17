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
from Distribution_Module_2 import Distribution, float_to_distribution
from Option_Module import get_time_to_expiry

""""
Changes since v2 (biotech_class_2.py):
    -Save instances of Evt_PresElection into a dictionary
    -Before I had assigned each instance a variable name
"""

class GeneralEvent(object):
    name = 'General Event'
    abbrev_name = 'GenEvent'
    timing = None
    instances = ['Event']
    #main_lever = 2.0

    def __init__(self):
        for cls in type(self).__mro__[0:-1]:
            cls.instances.append(self)
        
        #if type(self).__name__ == 'GeneralEvent':
        #    print("General Event Instantiated Successfully")

    def __str__(self):
        return "{}".format(self.abbrev_name)

    def __repr__(self):
        return "{}".format(self.abbrev_name)


class Event(GeneralEvent):
    name = 'Event'
    abbrev_name = 'SysEvent'
    timing = None
    mult = 1.0
    
    def __init__(self,
                 stock: 'str',
                 event_input: 'float or distribution object',
                 timing_descriptor = None,
                 event_name = name,
                 idio_mult = 1.0):
        super().__init__()
        self.stock = stock
        self.idio_mult = idio_mult

        if type(event_input) is int or type(event_input) is float:
            self.event_input = float_to_distribution(event_input)
        else:
            self.event_input = event_input
        #print("{} {} Instantiated Successfully".format(self.stock, self.name))
        
        #if type(self).__name__ == 'Event':
        #    print("{} Systematic Event Instantiated Successfully".format(self.stock))
        
    def __str__(self):
        return "{} ({:.2f}% move)".format(self.name, self.modeled_move*100)

    def __repr__(self):
        return "{} ({})".format(self.abbrev_name, self.stock)

    @property
    def event_input_distribution_df(self):
        return self.event_input.distribution_df

    @property
    def modeled_move(self):
        return self.get_distribution().distribution_df.mean_move

    def set_idio_mult(self, new_value):
        self.idio_mult = new_value

    def set_move_input(self, new_value):
        self.event_input = new_value

    def get_distribution(self, *args, **kwargs):
        distribution_df = copy.deepcopy(self.event_input_distribution_df)
        distribution_df.loc[:, 'Pct_Move'] *= self.mult*self.idio_mult
        distribution_df.loc[:, 'Relative_Price'] = distribution_df.loc[:, 'Pct_Move'] + 1
        return Distribution(distribution_df)


class SysEvt_PresElection(Event):
    name = 'U.S. Presidential Election'
    abbrev_name = 'Elec.'
    timing = dt.datetime(2020, 11, 3)
    mult = 1.0
    instances = ['Presidential Election']
    
    def __init__(self, stock: 'str', event_input: 'float', idio_mult = 1.0):
        super().__init__(stock, event_input, idio_mult)
        
        #print("{} Presidential Election Event Instantiated Successfully".format(self.stock))


class TakeoutEvent(GeneralEvent):
    name = 'Takeout'
    abbrev_name = 'T.O.'
    timing = None
    mult = 1.0
    instances = []
    
    takeout_buckets = pd.read_csv('TakeoutBuckets.csv')
    takeout_buckets.set_index('Rank', inplace=True)

    base_takeout_premium = .40
    base_mcap = 7500
    mcap_sensitivity = .35

    def __init__(self, stock: 'str', takeout_bucket: 'int'):
        super().__init__()
        self.stock = stock
        self.takeout_bucket = takeout_bucket
        #print("{} Takeout Event Instantiated Successfully.".format(self.stock))

    def __str__(self):
        return "{}-{} ({})".format(self.abbrev_name, self.takeout_bucket, self.stock)
    
    def __repr__(self):
        return "{} ({})".format(self.abbrev_name, self.stock)

    @property
    def takeout_prob(self):
        return self.takeout_buckets.loc[self.takeout_bucket, 'Prob']
    
    @property
    def mcap(self):
        try:
            return InformationTable.loc[self.stock, 'Market Cap']    
        except Exception:
            print("{} did not register a Market Cap. Check error source.".format(self.stock))
            return self.base_mcap

    @property
    def takeout_premium_adjustment(self):
        return min(((1 / (self.mcap/self.base_mcap)) - 1)*self.mcap_sensitivity, 1.5)

    @property
    def takeout_premium(self):
        return self.base_takeout_premium * (1 + self.takeout_premium_adjustment)

    
    def get_distribution(self, expiry: 'dt.date', *args, **kwargs):
        ref_date = dt.date.today()
        time_to_expiry = get_time_to_expiry(expiry)
        prob_takeout_by_expiry = time_to_expiry * self.takeout_prob
        prob_no_takeout_by_expiry = 1 - prob_takeout_by_expiry


        relative_price_takeout = (1 + self.takeout_premium)
        relative_price_no_takeout = 1-(prob_takeout_by_expiry*self.takeout_premium) / (prob_no_takeout_by_expiry)
        distribution_df = pd.DataFrame({'States': ['Takeout', 'No Takeout'],
                                        'Prob': [prob_takeout_by_expiry, prob_no_takeout_by_expiry],
                                        'Relative_Price': [relative_price_takeout, relative_price_no_takeout],
                                        'Pct_Move': [self.takeout_premium, relative_price_no_takeout-1]
                                        })
        distribution_df.set_index('States', inplace=True)
        distribution_df = distribution_df.loc[:, ['Prob', 'Pct_Move', 'Relative_Price']]
        distribution_df = Distribution(distribution_df)
        return distribution_df


# Option(option_type: 'str: C/P', strike: 'float', expiry: 'datetime')
# Price(Distribution, Option)
"""
-OptionPrice
    -Type: Function
    -Params:
        -Option: 'NamedTuple'
        -Distribution: 'Object'
    -Returns->
        -Content: Option Price 
        -Type: Float
"""


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


#Distribution(distrubtions: 'list of independent distributions')
#Price(Option, Distribution)
"""


"""
Types of Distributions:
    --DataFrame of ('Prob', 'Price)
    --MonteCarlo Distribution
    --DataFrame with Residual Volatilities
"""

