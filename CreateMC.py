import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
import math
import random
import copy
import pylab
from functools import reduce
from scipy.interpolate import interp1d, UnivariateSpline
from collections import namedtuple
import logging
from paul_resources import InformationTable, tprint, rprint, get_histogram_from_array
from decorators import my_time_decorator
from Option_Module import Option, OptionPrice, OptionPriceMC, get_implied_volatility, get_time_to_expiry
from Timing_Module import event_prob_by_expiry
from Event_Module import IdiosyncraticVol, Earnings, TakeoutEvent, Event, SysEvt_PresElection
from Distribution_Module import Distribution, float_to_event_distribution, float_to_bs_distribution

# Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s', "%m/%d/%Y %H:%M")

file_handler = logging.FileHandler('MC_Distributions.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

""""------------------Calculations: The goal is to optimze for speed.---------------------------"""

mc_iterations = 10**6
EarningsDist = Earnings('CRBP', .05, 'Q2_2018').get_distribution(dt.date(2018, 7, 1)).mc_simulation(mc_iterations)
IdiosyncraticVolDist = IdiosyncraticVol('CRBP', .10).get_distribution(dt.date.today() + timedelta(365)).mc_simulation(mc_iterations)

#@my_time_decorator
def filter_events_before_expiry(events, expiry):
    return [evt for evt in events if event_prob_by_expiry(evt.timing_descriptor, expiry) > 0]

#@my_time_decorator
def get_distributions_from_events(events, expiry):
    return [evt.get_distribution(expiry) for evt in events]
    
#@my_time_decorator
def get_mc_distributions(distributions, mc_iterations):
    return [dist.mc_simulation(mc_iterations) for dist in distributions]

@my_time_decorator
def sum_mc_distributions(mc_distributions: 'list of mc_distributions'):
    try:
        if len(mc_distributions) > 1:
            return reduce(lambda x, y: np.multiply(x,y), mc_distributions)
        else:
            return np.array(mc_distributions)
    except Exception:
        print("MC Simulations have different iteration sizes.")

@my_time_decorator
def optimally_get_mc_distribution_for_event(event, expiry):
    if isinstance(event, IdiosyncraticVol):
        mc_distribution = (IdiosyncraticVolDist - 1)*(event.at_the_money_vol/.10)*math.sqrt(get_time_to_expiry(expiry)) + 1
        logger.info('IdioVol: {}'.format(np.average(mc_distribution)))
    elif isinstance(event, Earnings):
        mc_distribution = (EarningsDist - 1)*(event.mean_move/.0504) + 1
        logger.info('Earnings: {}'.format(np.average(mc_distribution)))
    else:
        mc_distribution = event.get_distribution(expiry).mc_simulation(mc_iterations)
        logger.info('Other: {}'.format(np.average(mc_distribution)))
    return mc_distribution

@my_time_decorator
def get_total_mc_distribution_from_events(events, expiry = None, symbol = None, mc_iterations = 10**6):
    """Add the Simulation Results of Individual Events to Return the Total Simulated distribution."""
    if not events:
        return np.ones(mc_iterations)
    
    events = filter_events_before_expiry(events, expiry)
    mc_distributions = [optimally_get_mc_distribution_for_event(evt, expiry) for evt in events]
    return sum_mc_distributions(mc_distributions)

@my_time_decorator
def get_total_mc_distribution_from_events_vanilla(events, expiry = None, symbol = None, mc_iterations = 10**6):
    """Add the Simulation Results of Individual Events Without Optimizing for Speed."""
    if not events:
        return np.ones(mc_iterations)
    
    events = filter_events_before_expiry(events)
    distributions = get_distributions_from_events(events, expiry)
    mc_distributions = get_mc_distributions(distributions, mc_iterations)
    return sum_mc_distributions(mc_distributions)
