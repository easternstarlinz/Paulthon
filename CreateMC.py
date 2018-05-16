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
from paul_resources import InformationTable, tprint, rprint, get_histogram_from_array, setup_standard_logger
from decorators import my_time_decorator, empty_decorator
from Option_Module import Option, OptionPrice, OptionPriceMC, get_implied_volatility, get_time_to_expiry
from Timing_Module import event_prob_by_expiry
from Event_Module import IdiosyncraticVol, Earnings, TakeoutEvent, Event, SysEvt_PresElection
from Distribution_Module import Distribution, float_to_event_distribution, float_to_bs_distribution
from OptimalMC import optimally_get_mc_distribution_for_event

NO_USE_TIMING_DECORATOR = True
if NO_USE_TIMING_DECORATOR:
    my_time_decorator = empty_decorator

logger = setup_standard_logger('MC_Distributions.log')

""""------------------Calculations: The goal is to optimze for speed.---------------------------"""
#@my_time_decorator
def filter_events_before_expiry(events, expiry):
    return [evt for evt in events if event_prob_by_expiry(evt.timing_descriptor, expiry) > 0]


@my_time_decorator
def sum_mc_distributions(mc_distributions: 'list of mc_distributions'):
    """Mathematically combine MC Simulation Results"""
    try:
        if len(mc_distributions) > 1:
            return reduce(lambda x, y: np.multiply(x,y), mc_distributions)
        else:
            return np.array(mc_distributions[0])
    except Exception:
        print("MC Simulations have different iteration sizes.")

@my_time_decorator
def get_total_mc_distribution_from_events(events, expiry = None, symbol = None, mc_iterations = 10**6):
    """Add the Simulation Results of Individual Events to Return the Total Simulated distribution."""
    if not events:
        return np.ones(mc_iterations)
    
    events = filter_events_before_expiry(events, expiry)
    print('Events HERE', events)
    mc_distributions = [optimally_get_mc_distribution_for_event(evt, expiry) for evt in events]
    return sum_mc_distributions(mc_distributions)









"""Functionality that I am not currently using but may prove useful later"""
#@my_time_decorator
def get_distributions_from_events(events, expiry):
    return [evt.get_distribution(expiry) for evt in events]
    
#@my_time_decorator
def get_mc_distributions(distributions, mc_iterations):
    return [dist.mc_simulation(mc_iterations) for dist in distributions]

@my_time_decorator
def get_total_mc_distribution_from_events_vanilla(events, expiry = None, symbol = None, mc_iterations = 10**6):
    """Add the Simulation Results of Individual Events Without Optimizing for Speed."""
    if not events:
        return np.ones(mc_iterations)
    
    events = filter_events_before_expiry(events, expiry)
    distributions = get_distributions_from_events(events, expiry)
    mc_distributions = get_mc_distributions(distributions, mc_iterations)
    return sum_mc_distributions(mc_distributions)
