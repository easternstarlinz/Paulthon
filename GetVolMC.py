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
from decorators import my_time_decorator, empty_decorator
from Option_Module import Option, OptionPrice, OptionPriceMC, get_implied_volatility, get_time_to_expiry
from Timing_Module import event_prob_by_expiry
from Event_Module import IdiosyncraticVol, Earnings, TakeoutEvent, Event, SysEvt_PresElection
from Distribution_Module import Distribution, float_to_event_distribution, float_to_bs_distribution
from CreateMC import get_total_mc_distribution_from_events, filter_events_before_expiry

NO_USE_TIMING_DECORATOR = True
if NO_USE_TIMING_DECORATOR:
    my_time_decorator = empty_decorator


# Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s', "%m/%d/%Y %H:%M")

file_handler = logging.FileHandler('MC_Distributions.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

""""---------------Calculations: The goal is to optimze for speed (and organization)------------------"""
@my_time_decorator
def establish_strikes_from_mc_distribution(mc_distribution: 'numpy array', num_strikes = 100):
    """array.min() seems to be >70x faster than min(mc_distribution)"""
    strikeMin = mc_distribution.min()
    strikeMax = mc_distribution.max()
    strikeInterval = (strikeMax - strikeMin) / num_strikes
    return np.arange(strikeMin, strikeMax, strikeInterval)
    return pd.Series(np.arange(strikeMin, strikeMax, strikeInterval))

@my_time_decorator
def establish_call_options(expiry, strikes):
    return [Option('Call', strike, expiry) for strike in strikes]
    Option_Map = lambda strike: Option('Call', strike, expiry)
    return strikes.apply(Option_Map)

@my_time_decorator
def get_call_prices(call_options, mc_distribution):
    return list(map(lambda option: OptionPriceMC(option, mc_distribution), call_options))
    OptionPriceMC_Map = lambda option: OptionPriceMC(option, mc_distribution)
    #return call_options.apply(OptionPriceMC_Map)

@my_time_decorator
def get_call_IVs(call_options, call_prices):
    return list(map(lambda option, option_price: get_implied_volatility(option, option_price), call_options, call_prices))
    tuples = pd.concat([call_options, call_prices], axis=1).loc[:, [0,1]].apply(tuple, axis=1)
    IV_Map = lambda tup: get_implied_volatility(tup[0], tup[1])
    call_IVs = tuples.apply(IV_Map)
    #df = pd.concat([call_options, call_prices, call_IVs], axis=1).round(3)
    return call_IVs


@my_time_decorator
def get_option_sheet_df(options, content, content_label = 'IV'):
    expiry = options[0].Expiry
    strikes = [option.Strike for option in options]
    content = list(content)
    index_r = pd.Index(strikes, name = 'Strike')
    iterables_c = [[expiry], [content_label]]
    index_c = pd.MultiIndex.from_product(iterables_c, names = ['Expiry', 'Option_Info'])
    df = pd.DataFrame(content, index = index_r, columns = index_c)
    return df[df[(expiry, content_label)] > .0025].round(4)
    return pd.DataFrame(content, index = index_r, columns = index_c).round(3)

@my_time_decorator
def get_vol_surface_df(call_options, call_IVs):
    return get_option_sheet_df(call_options, call_IVs, 'IV')

@my_time_decorator
def get_call_prices_df(call_options, call_prices):
    return get_option_sheet_df(call_options, call_prices, 'Call_Price')

call_prices_cache = {}
@my_time_decorator
def get_call_prices_from_mc_distribution(mc_distribution,
                                         expiry = None,
                                         strikes = None,
                                         num_strikes = 100,
                                         pretty = False,
                                         symbol = None):
    if strikes is None:
        strikes = establish_strikes_from_mc_distribution(mc_distribution, num_strikes)

    call_options = tuple(establish_call_options(expiry, strikes))
    
    if (symbol, call_options) in call_prices_cache:
        call_prices = call_prices_cache[(symbol, call_options)]
    else:
        call_prices = get_call_prices(call_options, mc_distribution)
        call_prices_cache[(symbol, call_options)] = call_prices

        
    if pretty:
        return get_call_prices_df(call_options, call_prices)
    else:
        return [call_options, call_prices]

@my_time_decorator
def get_vol_surface_from_mc_distribution(mc_distribution,
                                         expiry = None,
                                         strikes = None,
                                         num_strikes = 100,
                                         pretty = False):
    call_options, call_prices = get_call_prices_from_mc_distribution(mc_distribution, expiry, strikes = strikes, pretty = pretty)
    call_IVs = get_call_IVs(call_options, call_prices)
    
    if pretty:
        return get_vol_surface_df(call_options, call_IVs)
    else:
        return [call_options, call_IVs]

mc_distribution_cache = {}

@my_time_decorator
def get_call_prices_from_events(events, expiry, strikes = None, pretty = False, symbol = None):
    if not events:
        return None
    
    #if (events, expiry) in mc_distribution_cache:
    if (symbol, expiry) in mc_distribution_cache:
        #mc_distribution = mc_distribution_cache[(events, expiry)]
        mc_distribution = mc_distribution_cache[(symbol, expiry)]
    else:
        mc_distribution = get_total_mc_distribution_from_events(events, expiry)
        #mc_distribution_cache[(events, expiry)] = mc_distribution
        mc_distribution_cache[(symbol, expiry)] = mc_distribution
    return get_call_prices_from_mc_distribution(mc_distribution, expiry, strikes = strikes, pretty = pretty, symbol = symbol)

@my_time_decorator
def get_vol_surface_from_events(events, expiry, strikes = None, pretty = False):
    if not events:
        return None

    call_options, call_prices = get_call_prices_from_events(events, expiry, strikes = strikes, pretty = False)
    call_IVs = get_call_IVs(call_options, call_prices)
    
    if pretty == True:
        return get_vol_surface_df(call_options, call_IVs) 
    else:
        return [call_options, call_IVs]

@my_time_decorator
def get_option_sheet_from_events(events, expiry, strikes = None, pretty = True):
    if not events:
        return None
    call_prices_df = get_call_prices_from_events(events, expiry, strikes = strikes, pretty = pretty)
    vol_surface_df = get_vol_surface_from_events(events, expiry, strikes = strikes, pretty = pretty)
    return call_prices_df.join(vol_surface_df).round(3)

@my_time_decorator
def get_vol_surface_spline(vol_surface):
    #strikes = vol_surface.index.values.tolist()
    #vols = vol_surface.iloc[:, 0].values.tolist()
    if vol_surface is None:
        return None
    strikes = [option.Strike for option in vol_surface[0]]
    vols = vol_surface[1]
    return interp1d(strikes, vols, kind='cubic')

@my_time_decorator
def get_term_structure(events, expiries, strikes, mc_iterations = 10**5):
    """Events -> Event Groupings by Expiry -> Vol_Surfaces by Expiry"""
    if strikes is None:
        strikes = np.arange(.5, 1.5, .025)
    
    event_groupings = [filter_events_before_expiry(events, expiry) for expiry in expiries]
    implied_vols = [get_vol_surface_from_events(event_grouping, expiry, strikes = strikes, pretty = True) for event_grouping, expiry in zip(event_groupings, expiries)]
    
    return reduce(lambda x,y: pd.merge(x, y, left_index=True, right_index=True), implied_vols)

"""
@my_time_decorator
def get_vol_surface_from_mc_distribution(mc_distribution,
                                         expiry = None,
                                         strikes = None,
                                         num_strikes = 100,
                                         pretty = False):
    if strikes is None:
        strikes = establish_strikes_from_mc_distribution(mc_distribution, num_strikes)

    call_options = establish_call_options(expiry, strikes)
    call_prices = get_call_prices(call_options, mc_distribution)
    call_IVs = get_call_IVs(call_options, call_prices)
    
    if pretty:
        return get_vol_surface_df(call_options, call_IVs)
    else:
        return [call_options, call_IVs]

#@my_time_decorator
def get_vol_surface_from_events(events, expiry, strikes = None, pretty = False):
    if not events:
        return None
    mc_distribution = get_total_mc_distribution_from_events(events, expiry)
    return get_vol_surface_from_mc_distribution(mc_distribution, expiry, strikes = strikes, pretty = pretty)
"""
