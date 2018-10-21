# Standard Packages
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

# Paul Packages
from option_model.Option_Module import Option, OptionPriceMC, get_implied_volatility
from CreateMC import get_total_mc_distribution_from_events, filter_events_before_expiry

# Paul Utility Functions
from utility.decorators import my_time_decorator, empty_decorator
from utility.general import setup_standard_logger, merge_dfs_horizontally

NO_USE_TIMING_DECORATOR = True
if NO_USE_TIMING_DECORATOR:
    my_time_decorator = empty_decorator

logger = setup_standard_logger('MC_Vol_Calcs')

""""---------------Calculations: The goal is to optimze for speed (and organization)------------------"""
@my_time_decorator
def establish_strikes_from_mc_distribution(mc_distribution: 'numpy array', num_strikes = 100):
    """This will be obsolete when I use the real strikes listed on the exchanges.
        array.min() seems to be >70x faster than min(mc_distribution)"""
    strikeMin = mc_distribution.min()
    strikeMax = mc_distribution.max()
    strikeInterval = (strikeMax - strikeMin) / num_strikes
    logger.debug('Min Value: {:.3f}, Max Value: {:.3f}, Interval: {:.3f}'.format(strikeMin, strikeMax, strikeInterval))
    return np.arange(strikeMin, strikeMax, strikeInterval)
    return pd.Series(np.arange(strikeMin, strikeMax, strikeInterval))

@my_time_decorator
def establish_call_options(expiry, strikes):
    """For a given expiry and list of strikes, establish a list of Call Options"""
    return [Option('Call', strike, expiry) for strike in strikes]
    create_call_option = lambda strike: Option('Call', strike, expiry)
    return strikes.apply(create_call_option)

@my_time_decorator
def get_call_prices(call_options, mc_distribution):
    return list(map(lambda option: OptionPriceMC(option, mc_distribution), call_options))
    OptionPriceMC_Map = lambda option: OptionPriceMC(option, mc_distribution)
    #return call_options.apply(OptionPriceMC_Map)

@my_time_decorator
def get_call_IVs(call_options, call_prices):
    return list(map(lambda call_option, call_price: get_implied_volatility(call_option, call_price), call_options, call_prices))
    tuples = pd.concat([call_options, call_prices], axis=1).loc[:, [0,1]].apply(tuple, axis=1)
    IV_Map = lambda tup: get_implied_volatility(tup[0], tup[1])
    call_IVs = tuples.apply(IV_Map)
    #df = pd.concat([call_options, call_prices, call_IVs], axis=1).round(3)
    return call_IVs


@my_time_decorator
def get_option_sheet_df(options, content, content_label = 'IV'):
    """This function takes a list of option contracts and content (prices or implied vols), and creates a DataFrame with the information"""

    # Extract the expiry from the first option contract (all contracts should have the same expiry date and only vary by strike)
    expiry = options[0].Expiry
    
    # Extract the strikes
    strikes = [option.Strike for option in options]
    
    # Extract the content; should already be a list
    content = list(content)
    
    # Define row and column labels for the DataFrame
    index_r = pd.Index(strikes, name = 'Strike')
    iterables_c = [[expiry], [content_label]]
    index_c = pd.MultiIndex.from_product(iterables_c, names = ['Expiry', 'Option_Info'])
    
    # Create the DataFrame
    df = pd.DataFrame(content, index = index_r, columns = index_c)
    
    # This line makes sense for a single expiry, but it returns an Empty DataFrame when I merge multiple expiries together that don't have the same rows.
    #df = df[df[(expiry, content_label)] > .0025].round(4)
    return df
    return pd.DataFrame(content, index = index_r, columns = index_c).round(3)

@my_time_decorator
def get_vol_surface_df(call_options, call_IVs):
    return get_option_sheet_df(options = call_options,
                               content = call_IVs,
                               content_label = 'IV')

@my_time_decorator
def get_call_prices_df(call_options, call_prices):
    return get_option_sheet_df(options = call_options,
                               content = call_prices,
                               content_label = 'Call_Price')

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
    """Events -> Event Groupings by Expiry -> Vol_Surfaces by Expiry -> a DataFrame showing all expiries"""
    if strikes is None:
        strikes = np.arange(.5, 1.5, .025)
    
    event_groupings = [filter_events_before_expiry(events, expiry) for expiry in expiries]
    implied_vols = [get_vol_surface_from_events(event_grouping, expiry, strikes = strikes, pretty = True) for event_grouping, expiry in zip(event_groupings, expiries)]
    
    logger.debug('Term Structure ran successfully.')
    return merge_dfs_horizontally(implied_vols)

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
