import datetime as dt
import pandas as pd
from pprint import pprint

from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter("ignore", category=RuntimeWarning)

# Paul Modules
from Stock_Module import Stock
from Option_Module import Option, get_option_price, get_implied_volatility, get_option_price
from Timing_Module import Timing, event_prob_by_expiry
from Event_Module import IdiosyncraticVol, TakeoutEvent, Earnings, Event, ComplexEvent, SysEvt_PresElection
from Distribution_Module import Distribution, Distribution_MultiIndex
from Events_sqlite import get_earnings_events
from timeline_chart import get_event_timeline
from term_structure import term_structure
from GetVolMC import get_vol_surface_from_events, get_vol_surface_spline, get_call_prices_from_events, get_option_sheet_from_events, get_term_structure
from CreateMC import get_total_mc_distribution_from_events

# Paul Utility Functions
from data.finance import TakeoutParams, Symbols
from utility.decorators import my_time_decorator, empty_decorator

NO_USE_TIMING_DECORATOR = False
if NO_USE_TIMING_DECORATOR:
    my_time_decorator = empty_decorator

EarningsEvents = get_earnings_events()

@my_time_decorator
def get_stock_objects(symbols: 'list of symbols'):
    return [Stock(symbol) for symbol in symbols]

@my_time_decorator
def get_option_price_first_time(stock, option):
    return stock.get_option_price(option)

@my_time_decorator
def instantiate_expiries(stock, expiries):
    for expiry in expiries:
        stock.get_vol_surface_spline(expiry)

def setup_instantiation_list(stocks):
    instantiation_list = []
    for stock in stocks:
        pair = (stock, stock.expiries)
        all_pairs = [(pair[0], pair[1][i])  for i in range(len(pair[1]))]
        instantiation_list.extend(all_pairs)
    
    return instantiation_list

@my_time_decorator
def instantiate_expiries_multiple_stocks(stocks, USE_POOL = False):
    if USE_POOL is False:
        # Set up Instantiation List
        instantiation_list = setup_instantiation_list(stocks)
        for stock, expiry in instantiation_list:
            stock.get_vol_surface_spline(expiry)

    else:
        for stock in stocks:
            stock_expiries = stock.expiries
            
            pool = ThreadPool(2)
            pool.map(lambda expiry: stock.get_vol_surface_spline(expiry), stock_expiries)

@my_time_decorator
def run():
    if __name__ == '__main__':
        symbols = Symbols[0:20]
        stocks = get_stock_objects(symbols)
        instantiate_expiries_multiple_stocks(stocks, USE_POOL = True)
        
        total_num_expiries = 0
        for stock in stocks:
            total_num_expiries += len(stock.expiries)
        print('Num Stocks: {}, Num Expiries: {}'.format(len(stocks), total_num_expiries))
run()
