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

""""
Changes since v2 (biotech_class_2.py):
    -Save instances of Evt_PresElection into a dictionary
    -Before I had assigned each instance a variable name
"""

Option = namedtuple('Option', ['Option_Type', 'Strike', 'Expiry'])

def OptionPrice(Option, Distribution):
    if Option.Option_Type == 'Call':
        return sum([state.Prob*max(state.Relative_Price - Option.Strike, 0) for state in Distribution.distribution_df.itertuples()])

    if Option.Option_Type == 'Put':
        return sum([state.Prob*max(Option.Strike - state.Relative_Price, 0) for state in Distribution.distribution_df.itertuples()])

def OptionPriceMC(Option, MC_Results):
    if Option.Option_Type == 'Call':
        return np.average(np.maximum(MC_Results + 1 - Option.Strike, np.zeros(len(MC_Results))))
    if Option.Option_Type == 'Put':
        return np.average(np.maximum(Option.Strike - (MC_Results + 1), np.zeros(len(MC_Results))))

def get_implied_volatility(Option, underlying_price, option_price, interest_rate = 0, reference_date = dt.date.today()):
    price = option_price
    S = underlying_price
    K = Option.Strike
    r = interest_rate
    flag = Option.Option_Type.lower()[0]
    t = get_time_to_expiry(Option.Expiry)
    return implied_volatility(price, S, K, t, r, flag)

def graph_MC_distribution(results: 'numpy array of numbers'):
    bins = np.arange(-2.5, 2.5, .05)
    plt.hist(results, bins, histtype='bar', rwidth=.8, color = 'blue', label = 'Rel. Frequency')
    
    plt.title('Monte Carlo Simulation\n Check it out')
    plt.xlabel('Percent Move')
    plt.ylabel('Relative Frequency')
    plt.legend()
    plt.show()

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

def float_to_Distribution_object(move_input: 'float'):
    distribution_df = pd.read_csv('Event.csv')
    distribution_df.set_index('State', inplace=True)
    distribution_df.loc[:, 'Pct_Move'] *= move_input*100
    distribution_df.loc[:, 'Relative_Price'] = distribution_df.loc[:, 'Pct_Move'] + 1
    distribution_df = Distribution(distribution_df)
    return distribution_df

def get_time_to_expiry(expiry: 'dt.date', ref_date = dt.date.today()):
    return  max((expiry - ref_date).days/365, 0)

class Event(GeneralEvent):
    name = 'Event'
    abbrev_name = 'SysEvent'
    timing = None
    mult = 1.0
    
    def __init__(self, stock: 'str', event_input: 'float or Distribution object', event_name = name, idio_mult = 1.0):
        super().__init__()
        self.stock = stock
        #self.event_input = event_input
        self.idio_mult = idio_mult

        if type(event_input) is int or type(event_input) is float:
            self.event_input = float_to_Distribution_object(event_input)
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

class Distribution(object):
    """DataFrame({Index: 'States',
                    Columns: ['Prob', 'Pct_Move', 'Price']
                    }) 
                    
                    ->
                    'Distribution() object'
    """
    def __init__(self, distribution_df: "DataFrame({Index: 'States', Columns: ['Prob', 'Pct_Move', 'Relative_Price']}") -> 'Distribution object':
        self.distribution_df = distribution_df

    @property
    def mean_move(self):
        return math.sqrt(sum([state.Prob*state.Pct_Move**2 for state in self.distribution_df.itertuples()]))

    
    def mc_simulation(self, iterations):
        pct_moves = self.distribution_df.loc[:, 'Pct_Move'].values.tolist()
        weights = self.distribution_df.loc[:, 'Prob'].values.tolist()
        results = random.choices(pct_moves, weights=weights, k=iterations)
        results = np.array(results)
        return results


    def __add__(self, other):
        i  = 1
        new_states = []
        new_probs = []
        new_pct_moves = []
        new_relative_prices = []
        
        for self_state in self.distribution_df.itertuples():
            for other_state in other.distribution_df.itertuples():
                index = i
                #new_state = "{}; {}".format(self_state.Index, other_state.Index)
                new_prob = self_state.Prob*other_state.Prob
                new_relative_price = self_state.Relative_Price*other_state.Relative_Price
                new_pct_move = new_relative_price - 1

                new_states.append(i)
                new_probs.append(new_prob)
                new_relative_prices.append(new_relative_price)
                new_pct_moves.append(new_pct_move)

                i += 1

        new_distribution_info = {'State': new_states,
                                 'Prob': new_probs,
                                 'Pct_Move': new_pct_moves,
                                 'Relative_Price': new_relative_prices}

        new_distribution_df = pd.DataFrame(new_distribution_info)
        new_distribution_df.set_index('State', inplace=True)
        new_distribution_df = new_distribution_df.loc[:, ['Prob', 'Pct_Move', 'Relative_Price']]
        return Distribution(new_distribution_df)


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

