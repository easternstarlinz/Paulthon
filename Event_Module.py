import datetime as dt
import pandas as pd
import math
import numpy as np
import random
import copy
import matplotlib.pyplot as plt
from collections import namedtuple
from statistics import mean
from py_vollib.black_scholes.implied_volatility import black_scholes, implied_volatility

from decorators import my_time_decorator
from paul_resources import InformationTable, tprint, rprint
from Distribution_Module import Distribution, Distribution_MultiIndex, float_to_event_distribution, float_to_bs_distribution, float_to_volbeta_distribution, get_no_event_distribution
from Option_Module import get_time_to_expiry
from Timing_Module import Timing, event_prob_by_expiry
import logging

# Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s', "%m/%d/%Y %H:%M")

file_handler = logging.FileHandler('event_instances.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

#stream_handler = logging.StreamHandler()

logger.addHandler(file_handler)
#logger.addHandler(stream_handler)

class GeneralEvent(object):
    name = 'General Event'
    abbrev_name = 'GenEvent'
    timing = None
    instances = ['Event']
    #main_lever = 2.0

    def __init__(self, timing_descriptor = timing):
        self.timing_descriptor = timing_descriptor
        
        for cls in type(self).__mro__[0:-1]:
            cls.instances.append(self)
        
        if type(self).__name__ == 'GeneralEvent':
            logger.info("General Event Instantiated Successfully")


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
                 event_input: 'float or distribution object' = None,
                 timing_descriptor = timing,
                 event_name = None,
                 idio_mult = 1.0):
        super().__init__(timing_descriptor = timing_descriptor)
        self.stock = stock
        self.event_input_value = event_input
        
        
        if type(event_input) is int or type(event_input) is float:
            self.event_input = float_to_event_distribution(event_input)
        else:
            self.event_input = event_input
       
        #if timing_descriptor is None:
        #    self.timing_descriptor = self.timing
        #self.timing_descriptor = timing_descriptor
        if event_name is None:
            self.event_name = self.abbrev_name
        else:
            self.event_name = event_name
        self.idio_mult = idio_mult

        logger.info("{} {} Instantiated Successfully".format(self.stock, self.name))
        
        if type(self).__name__ == 'Event':
            logger.info("{} Systematic Event Instantiated Successfully".format(self.stock))
        
    def __str__(self):
        return "{} ({:.2f}% move)".format(self.name, self.modeled_move*100)

    def __repr__(self):
        return "{}".format(self.event_name)
        #return "{} ({})".format(self.abbrev_name, self.stock)

    @property
    def event_input_distribution_df(self):
        return self.event_input.distribution_df

    @property
    def modeled_move(self):
        return self.get_distribution().mean_move

    def set_idio_mult(self, new_value):
        self.idio_mult = new_value

    def set_move_input(self, new_value):
        self.event_input = new_value
    
    #@my_time_decorator
    def get_distribution(self, expiry = None, *args, **kwargs):
        event_by_expiry = event_prob_by_expiry(self.timing_descriptor, expiry)
        event_not_by_expiry = 1 - event_by_expiry
        
        if event_by_expiry == 0:
            return get_no_event_distribution()
       
        elif event_by_expiry == 1:
            distribution_df = copy.deepcopy(self.event_input_distribution_df)
            distribution_df.loc[:, 'Pct_Move'] *= self.mult*self.idio_mult
            distribution_df.loc[:, 'Relative_Price'] = distribution_df.loc[:, 'Pct_Move'] + 1
            return Distribution(distribution_df)
            
        else:
            no_event_scenario_info = {'State': ['No_Event'],
                                      'Prob': [event_not_by_expiry],
                                      'Pct_Move': [0],
                                      'Relative_Price': [1.0]}
            
            no_event_scenario_df = pd.DataFrame(no_event_scenario_info).set_index('State').loc[:, ['Prob', 'Pct_Move', 'Relative_Price']]
            

            distribution_df = copy.deepcopy(self.event_input_distribution_df)
            distribution_df.loc[:, 'Pct_Move'] *= self.mult*self.idio_mult
            distribution_df.loc[:, 'Relative_Price'] = distribution_df.loc[:, 'Pct_Move'] + 1
            distribution_df.loc[:, 'Prob'] *= event_by_expiry
            distribution_df = distribution_df.append(no_event_scenario_df)
            
            return Distribution(distribution_df)

    @property
    def event_bid(self):
        return Event(self.stock,
                     self.event_input*.9,
                     self.timing_descriptor,
                     self.event_name,
                     self.idio_mult)
   
    @property
    def event_ask(self):
        return Event(self.stock,
                     self.event_input*1.1,
                     self.timing_descriptor,
                     self.event_name,
                     self.idio_mult)
    @property
    def event_width(self):
        return self.event_ask.get_distribution().mean_move - self.event_bid.get_distribution().mean_move

class IdiosyncraticVol(Event):
    name = 'Idiosyncratic Vol'
    abbrev_name = 'Idio_Vol'
    timing = None
    mult = 1.0
    instances = []

    def __init__(self,
                 stock: 'str',
                 event_input: 'float',
                 idio_mult = 1.0):
        super().__init__(stock, idio_mult = idio_mult)
        
        if type(event_input) is int or type(event_input) is float:
            self.event_input = float_to_volbeta_distribution(event_input)
        else:
            self.event_input = event_input
        logger.info("{} {} Instantiated Successfully".format(self.stock, self.name))
        
        self.event_input_float = event_input

    def get_distribution(self, expiry):
        time_to_expiry = get_time_to_expiry(expiry)
        distribution_df = copy.deepcopy(self.event_input_distribution_df)
        distribution_df.loc[:, 'Pct_Move'] *= self.mult*self.idio_mult*math.sqrt(time_to_expiry)
        distribution_df.loc[:, 'Relative_Price'] = distribution_df.loc[:, 'Pct_Move'] + 1
        return Distribution(distribution_df)

    def __str__(self):
        return "{} ({:.2f}% IV)".format(self.name, self.at_the_money_vol*100)
    
    @property
    def at_the_money_vol(self):
        return self.event_input_float*IdiosyncraticVol.mult*self.idio_mult

    @property
    def event_bid(self):
        return IdiosyncraticVol(self.stock,
                                self.event_input*.95,
                                self.idio_mult)
   
    @property
    def event_ask(self):
        return IdiosyncraticVol(self.stock,
                                self.event_input*1.05,
                                self.idio_mult)

class SysEvt_PresElection(Event):
    name = 'U.S. Presidential Election'
    abbrev_name = 'Elec.'
    timing = dt.date(2018, 11, 3)
    mult = 1.0
    instances = []
    
    def __init__(self,
                 stock: 'str',
                 event_input: 'float',
                 idio_mult = 1.0):
        super().__init__(stock = stock,
                         event_input = event_input,
                         timing_descriptor = self.timing,
                         idio_mult = idio_mult)
        
        logger.info("{} Presidential Election Event Instantiated Successfully".format(self.stock))

class Earnings(Event):
    name = 'Earnings'
    abbrev_name = 'Earns.'
    timing = None
    mult = 1.0
    instances = []
    
    def __init__(self,
                 stock: 'str',
                 event_input: 'float',
                 timing_descriptor,
                 event_name = name,
                 idio_mult = 1.0):
        super().__init__(stock = stock,
                         event_input = event_input,
                         timing_descriptor = timing_descriptor,
                         event_name = event_name,
                         idio_mult = idio_mult,
                         )
        
        logger.info("{} {} Earnings Event Instantiated Successfully".format(self.stock, self.quarter))
        
        self.event_input_float = event_input 
    
    def __repr__(self):
        return "{} ({})".format(self.abbrev_name, self.quarter)
        #return "{} ({})".format(self.abbrev_name, Timing(self.timing_descriptor).timing_descriptor_abbrev)
        #return "{}-{} ({})".format(self.abbrev_name, self.timing_descriptor, self.stock)
    
    @property
    def quarter(self):
        return self.event_name[0:2]
    
    @property
    def mean_move(self):
        return self.event_input_float*Earnings.mult*self.idio_mult

    @property
    def event_bid(self):
        return Earnings(self.stock,
                        self.event_input*.925,
                        self.timing_descriptor,
                        self.event_name,
                        self.idio_mult)
   
    @property
    def event_ask(self):
        return Earnings(self.stock,
                        self.event_input*1.075,
                        self.timing_descriptor,
                        self.event_name,
                        self.idio_mult)
    

class ComplexEvent(Event):
    name = 'Complex_Event'
    abbrev_name = 'Complex_Evt'
    timing = None
    mult = 1.0
    instances = []
    
    def __init__(self,
                 stock: 'str',
                 event_input: 'float',
                 timing_descriptor,
                 event_name = None,
                 idio_mult = 1.0):
        super().__init__(stock = stock,
                         event_input = event_input,
                         timing_descriptor = timing_descriptor,
                         event_name = event_name,
                         idio_mult = idio_mult,
                         )
        
        logger.info("{} {} Complex Event Instantiated Successfully".format(self.stock, self.timing_descriptor))
    @property
    def event_bid(self):
        return ComplexEvent(self.stock,
                            self.event_input*.925,
                            self.timing_descriptor,
                            self.event_name,
                            self.idio_mult)
   
    @property
    def event_ask(self):
        return ComplexEvent(self.stock,
                            self.event_input*1.075,
                            self.timing_descriptor,
                            self.event_name,
                            self.idio_mult)

    
    def event_prob_success(self, new_prob_success):
        new_distribution = Distribution_MultiIndex(self.event_input_distribution_df)
        new_distribution.set_prob_success(new_prob_success)
        new_event = ComplexEvent(self.stock,
                                new_distribution,
                                self.timing_descriptor,
                                self.event_name,
                                self.idio_mult)
        #print(new_event.event_input_distribution_df.to_string())
        return new_event
    
    @property
    def event_high_prob_success(self):
        return self.event_prob_success(.95)

    @property
    def event_low_prob_success(self):
        return self.event_prob_success(.05)
    
    @property
    def event_max_optionality(self):
        new_distribution = Distribution_MultiIndex(self.event_input_distribution_df)
        
        most_positive_state = new_distribution.positive_scenario_states[0][1]
        new_distribution.set_positive_scenario_substate_prob(most_positive_state, 1.0)
        
        most_negative_state = new_distribution.negative_scenario_states[-1][1]
        new_distribution.set_negative_scenario_substate_prob(most_negative_state, 1.0)

        new_distribution.set_prob_success(.5)

        new_event = ComplexEvent(self.stock,
                                new_distribution,
                                self.timing_descriptor,
                                self.event_name,
                                self.idio_mult)
        #print(new_event.event_input_distribution_df.to_string())
        return new_event
        return self.event_prob_success(.05)

class TakeoutEvent(GeneralEvent):
    name = 'Takeout'
    abbrev_name = 'T.O.'
    timing = None
    mult = 1.0
    instances = []
    
    takeout_buckets = pd.read_csv('TakeoutBuckets.csv')
    takeout_buckets.set_index('Rank', inplace=True)

    base_takeout_premium = .35
    base_mcap = 8750
    mcap_sensitivity = .3
    """
    def __init__(self,
                 stock: 'str',
                 takeout_bucket: 'int',
                 event_input: 'float or distribution object' = None,
                 timing_descriptor = None,
                 event_name = name,
                 idio_mult = 1.0):
        super().__init__()
    """    
    def __init__(self, stock: 'str', takeout_bucket: 'int'):
        super().__init__()
        self.stock = stock
        self.takeout_bucket = takeout_bucket
        logger.info("{} Takeout Event Instantiated Successfully.".format(self.stock))

    def __str__(self):
        return "{}-{} ({})".format(self.abbrev_name, self.takeout_bucket, self.stock)
    
    def __repr__(self):
        return "{} Tier {} ({})".format(self.abbrev_name, self.takeout_bucket, self.stock)

    @property
    def takeout_prob(self):
        return self.takeout_buckets.loc[self.takeout_bucket, 'Prob']
    
    @property
    def mcap(self):
        try:
            return InformationTable.loc[self.stock, 'Market Cap']    
        except Exception:
            logger.error("{} did not register a Market Cap. Check error source.".format(self.stock))
            return self.base_mcap

    @property
    def takeout_premium_adjustment(self):
        return min(((1 / (self.mcap/self.base_mcap)) - 1)*self.mcap_sensitivity, 1.5)

    @property
    def takeout_premium(self):
        return self.base_takeout_premium * (1 + self.takeout_premium_adjustment)

    
    def get_distribution(self, expiry: 'dt.date', *args, **kwargs):
        time_to_expiry = get_time_to_expiry(expiry)
        prob_takeout_by_expiry = time_to_expiry * self.takeout_prob
        prob_no_takeout_by_expiry = 1 - prob_takeout_by_expiry

        relative_price_takeout = (1 + self.takeout_premium)
        relative_price_no_takeout = 1-(prob_takeout_by_expiry*self.takeout_premium) / (prob_no_takeout_by_expiry)
        
        distribution_info = {'States': ['Takeout', 'No Takeout'],
                             'Prob': [prob_takeout_by_expiry, prob_no_takeout_by_expiry],
                             'Relative_Price': [relative_price_takeout, relative_price_no_takeout],
                             'Pct_Move': [self.takeout_premium, relative_price_no_takeout-1]}
        
        distribution_df = pd.DataFrame(distribution_info).set_index('States').loc[:, ['Prob', 'Pct_Move', 'Relative_Price']]
        return Distribution(distribution_df)
    
    @property
    def event_bid(self):
        return TakeoutEvent(self.stock, min(self.takeout_bucket + 2, 7))
        #return TakeoutEvent(self.stock, 7)
   
    @property
    def event_ask(self):
        return TakeoutEvent(self.stock, max(self.takeout_bucket - 1, 1))
