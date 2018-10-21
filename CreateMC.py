import numpy as np
from functools import reduce

# Paul Resources
from option_model.Timing_Module import event_prob_by_expiry
from option_model.OptimalMC import optimally_get_mc_distribution_for_event

# Paul Utility Functions
from utility.general import setup_standard_logger
from utility.decorators import my_time_decorator, empty_decorator

NO_USE_TIMING_DECORATOR = True
if NO_USE_TIMING_DECORATOR:
    my_time_decorator = empty_decorator

logger = setup_standard_logger('MC_Distributions.log')

""""------------------Calculations: The goal is to optimze for speed.---------------------------"""
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

# I currently have symbol as an optional parameter, but I don't think I need this when there are multiple symbols that share an event, the events will be chosen by symbol.
@my_time_decorator
def get_total_mc_distribution_from_events(events, expiry, symbol=None, mc_iterations=10**6):
#def get_total_mc_distribution_from_events(events, expiry=None, symbol=None, mc_iterations=10**6):
    """For one expiry, add the simulation results of individual events to return the total simulated distribution."""
    
    events = filter_events_before_expiry(events, expiry)
    
    if not events:
        return np.ones(mc_iterations)
    
    print('Events HERE', events)
    individual_mc_distributions = [optimally_get_mc_distribution_for_event(evt, expiry) for evt in events]
    return sum_mc_distributions(individual_mc_distributions)









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
