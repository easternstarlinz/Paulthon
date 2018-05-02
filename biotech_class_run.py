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
from paul_resources import InformationTable, tprint, rprint, get_histogram_from_array
from decorators import my_time_decorator
from Option_Module import Option, OptionPrice, OptionPriceMC, get_implied_volatility, get_time_to_expiry
from Timing_Module import event_prob_by_expiry
from Event_Module import IdiosyncraticVol, Earnings, TakeoutEvent, Event, SysEvt_PresElection
from Distribution_Module import Distribution, float_to_event_distribution, float_to_bs_distribution

"""------------------------------Calculations----------------------------------------"""
"""---------------------------The goal is to optimze for speed. There are a lot of comments because I have many tradeoffs and kept the different methodologies.--------------------------------"""
EarningsDist = Earnings('CRBP', .05, 'Q2_2018').get_distribution(dt.date(2018, 7, 1)).mc_simulation(10**4)
IdiosyncraticVolDist = IdiosyncraticVol('CRBP', .10).get_distribution(dt.date.today() + timedelta(365)).mc_simulation(10**4)

@my_time_decorator
def get_total_mc_distribution(events, expiry = None, symbol = None, mc_iterations = 10**5):
    """Add the Simulation Results of Individual Events to Return the Total Simulated distribution."""
    print(mc_iterations)

    """
    events = [evt for evt in events if event_prob_by_expiry(evt.timing_descriptor, expiry) > 0]
    distributions = map(lambda evt: evt.get_distribution(expiry), events)
    mc_distributions = map(lambda dist: dist.mc_simulation(mc_iterations), distributions)
    """
    
    #@my_time_decorator
    def establish_events(events, expiry):
        return [evt for evt in events if event_prob_by_expiry(evt.timing_descriptor, expiry) > 0]
    
    #@my_time_decorator
    def get_distributions(events, expiry):
        return [evt.get_distribution(expiry) for evt in events if event_prob_by_expiry(evt.timing_descriptor, expiry) >0]
        #return list(map(lambda evt: evt.get_distribution(expiry), events))
        #return list(map(lambda evt: evt.get_distribution(expiry), events))
    
    #@my_time_decorator
    def get_mc_distributions(distributions):
        mc_distributions = list(map(lambda dist: dist.mc_simulation(mc_iterations), distributions))
        return mc_distributions
        #return map(lambda dist: dist.mc_simulation(mc_iterations), distributions)
    
    #@my_time_decorator
    def get_tot_mc_distribution(mc_distributions):
        if len(mc_distributions) > 1:
            return reduce(lambda x, y: np.multiply(x,y), mc_distributions)
        else:
            return np.array(mc_distributions)

    #@my_time_decorator
    def new_methodology(events, expiry, mc_iterations = 10**4):
        events = establish_events(events, expiry)
        
        if not events:
            return np.ones(mc_iterations)
        
        mc_distributions = []
        for evt in events:
            if isinstance(evt, IdiosyncraticVol):
                mc_distribution = (IdiosyncraticVolDist - 1)*(evt.at_the_money_vol/.10)*math.sqrt(get_time_to_expiry(expiry)) + 1
                #print('IdioVol: {}'.format(np.average(mc_distribution)))
            elif isinstance(evt, Earnings):
                mc_distribution = (EarningsDist - 1)*(evt.mean_move/1.0504) + 1
                #print('Earnings: {}'.format(np.average(mc_distribution)))
            else:
                mc_distribution = evt.get_distribution(expiry).mc_simulation(mc_iterations)
                #print('Other: {}'.format(np.average(mc_distribution)))
            mc_distributions.append(mc_distribution)
        return get_tot_mc_distribution(mc_distributions)
    


    #events = establish_events(events)
    #distributions = get_distributions(events)
    #mc_distributions = get_mc_distributions(distributions)
    #total_mc_distribution = get_tot_mc_distribution(mc_distributions)
    total_mc_distribution = new_methodology(events, expiry)
    return total_mc_distribution
    #return reduce(lambda x, y: np.multiply(x,y), mc_distributions)

#@my_time_decorator
def get_vol_surface_from_mc_distribution(mc_distribution, expiry = None, strikes = None):
    
    @my_time_decorator
    def establish_strike_range(mc_distribution: 'numpy array'):
        """array.min() seems to be >70x faster than min(mc_distribution)"""
        strikeMin = mc_distribution.min()
        strikeMax = mc_distribution.max()
    #establish_strike_range(mc_distribution)
    
    if strikes is None:
        strikeMin = mc_distribution.min()
        strikeMax = mc_distribution.max()
        strikeInterval = (strikeMax - strikeMin) / 50
        strikes = pd.Series(np.arange(strikeMin, strikeMax, .01))
        #strikes = np.arange(strikeMin, strikeMax, strikeInterval)

    #@my_time_decorator
    def establish_call_options(expiry, strikes):
        return [Option('Call', strike, expiry) for strike in strikes]
        Option_Map = lambda strike: Option('Call', strike, expiry)
        return strikes.apply(Option_Map)
    
    #@my_time_decorator
    def get_call_prices(call_options, mc_distribution):
        return list(map(lambda option: OptionPriceMC(option, mc_distribution), call_options))
        OptionPriceMC_Map = lambda option: OptionPriceMC(option, mc_distribution)
        #return call_options.apply(OptionPriceMC_Map)
    
    #@my_time_decorator
    def get_call_IVs(call_options, call_prices):
        return list(map(lambda option, option_price: get_implied_volatility(option, option_price), call_options, call_prices))
        tuples = pd.concat([call_options, call_prices], axis=1).loc[:, [0,1]].apply(tuple, axis=1)
        IV_Map = lambda tup: get_implied_volatility(tup[0], tup[1])
        call_IVs = tuples.apply(IV_Map)
        #df = pd.concat([call_options, call_prices, call_IVs], axis=1).round(3)
        return call_IVs
    
    #@my_time_decorator
    def get_vol_surface_df(expiry, strikes, call_IVs):
        vol_surface_info = list(call_IVs)
        index_r = pd.Index(strikes, name = 'Strike')
        iterables_c = [[expiry], ['IV']]
        index_c = pd.MultiIndex.from_product(iterables_c, names = ['Expiry', 'Option_Info'])
        vol_surface = pd.DataFrame(vol_surface_info, index = index_r, columns = index_c)
        return vol_surface
    
    call_options = establish_call_options(expiry, strikes)
    call_prices = get_call_prices(call_options, mc_distribution)
    call_IVs = get_call_IVs(call_options, call_prices)
    #print(strikes)
    #print(call_IVs.to_string())
    #return get_vol_surface_df(expiry, strikes, call_IVs)
    return [strikes, call_IVs]
    """
    call_options = [Option('Call', strike, expiry) for strike in strikes]
    call_prices = list(map(lambda option: OptionPriceMC(option, mc_distribution), call_options))
    call_IVs = list(map(lambda option, option_price: get_implied_volatility(option, option_price), call_options, call_prices))
    
    vol_surface_info = list(call_IVs)
    index_r = pd.Index(strikes, name = 'Strike')
    iterables_c = [[expiry], ['IV']]
    index_c = pd.MultiIndex.from_product(iterables_c, names = ['Expiry', 'Option_Info'])
    vol_surface = pd.DataFrame(vol_surface_info, index = index_r, columns = index_c)
    return vol_surface
    """
    #return [strikes, call_IVs]

#@my_time_decorator
def get_vol_surface_from_event_grouping(event_grouping, expiry):
    mc_distribution = get_total_mc_distribution(event_grouping, expiry)
    #print(np.average(mc_distribution))
    #print('Expiry:', expiry, 'Event Grouping:', event_grouping)
    return get_vol_surface_from_mc_distribution(mc_distribution, expiry)

#@my_time_decorator
def get_vol_surface(events, expiry):
    if not events:
        return None
    return get_vol_surface_from_event_grouping(events, expiry)

#@my_time_decorator
def get_vol_surface_spline(vol_surface):
    #strikes = vol_surface.index.values.tolist()
    #vols = vol_surface.iloc[:, 0].values.tolist()
    if vol_surface is None:
        return None
    strikes = vol_surface[0]
    vols = vol_surface[1]
    return interp1d(strikes, vols, kind='cubic')
