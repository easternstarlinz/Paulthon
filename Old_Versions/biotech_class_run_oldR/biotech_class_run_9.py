import pandas as pd
import numpy as np
from option_model.Option_Module import Option, OptionPriceMC, get_implied_volatility
from functools import reduce

"""------------------------------Calculations----------------------------------------"""
#@my_time_decorator
def get_total_mc_distribution(events, expiry = None, symbol = None, mc_iterations = 10**4):
    """Add the simulation results of individual events to return the total simulated distribution."""
    distributions = map(lambda evt: evt.get_distribution(expiry), events)
    mc_distributions = map(lambda dist: dist.mc_simulation(mc_iterations), distributions)
    return reduce(lambda x, y: np.multiply(x,y), mc_distributions)

#@my_time_decorator
def get_option_sheet_from_mc_distribution(mc_distribution, expiry = None, strikes = None):
    if strikes is None:
        strikes = np.arange(.75, 1.25, .05)

    call_options = [Option('Call', strike, expiry) for strike in strikes]
    call_prices = list(map(lambda option: OptionPriceMC(option, mc_distribution), call_options))
    call_IVs = list(map(lambda option, option_price: get_implied_volatility(option, option_price), call_options, call_prices))
   
    put_options = [Option('Put', strike, expiry) for strike in strikes]
    put_prices = list(map(lambda option: OptionPriceMC(option, mc_distribution), put_options))
    put_IVs = list(map(lambda option, option_price: get_implied_volatility(option, option_price), put_options, put_prices))

    option_premiums = [min(call_price, put_price) for call_price, put_price in zip(call_prices, put_prices)]
    
    """
    option_sheet_info = {'Strike': strikes, 'Price': option_premiums, 'IV': call_IVs}
    option_sheet = pd.DataFrame(option_sheet_info).set_index('Strike').loc[:, ['Price', 'IV']].round(2)
    """
    
    option_sheet_info = list(zip(option_premiums, call_IVs))
    index_r = pd.Index(strikes, name = 'Strike')
    iterables_c = [[expiry], ['Premium', 'IV']]
    index_c = pd.MultiIndex.from_product(iterables_c, names = ['Expiry', 'Option_Info'])
    option_sheet = pd.DataFrame(option_sheet_info, index = index_r, columns = index_c)
    return option_sheet

#@my_time_decorator
def get_option_sheet_by_event_groupings(event_groupings, expiry):
#        i = 0
#        for grouping in event_groupings:
#            mc_distribution = get_total_mc_distribution(grouping, expiry = expiry)
#            prices = get_option_sheet_from_mc_distribution(mc_distribution, strikes = np.arange(.5, 1.55, .05)).loc[:, ['Price','IV']]
#
#            if event_groupings.index(grouping) == 0:
#                prices_df = prices
#            else:
#                prices_df = pd.merge(prices_df, prices, left_index=True, right_index=True)
#            
#            get_mc_histogram(mc_distribution)
#            
#            i += 1
#        return prices_df
    mc_distributions = list(map(lambda event_grouping: get_total_mc_distribution(event_grouping, expiry), event_groupings))
    #[get_histogram_from_array(mc_distribution) for mc_distribution in mc_distributions]
    #show_term_structure(mc_distributions)

    option_sheets = list(map(lambda dist: get_option_sheet_from_mc_distribution(dist, expiry).loc[:, ['IV']], mc_distributions))
    return reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), option_sheets)

#@my_time_decorator
def option_sheet(event_groupings,
                  expiry = None,
                  mc_iterations = 10**5):
    option_sheet_by_groupings = get_option_sheet_by_event_groupings(event_groupings, expiry)
    #print(option_sheet_by_groupings)
    return option_sheet_by_groupings
