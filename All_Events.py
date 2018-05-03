import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter("ignore", category=RuntimeWarning)
import pandas as pd
import datetime as dt
from pprint import pprint
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import warnings

from Option_Module import Option, get_option_price, get_implied_volatility, get_option_price
from Timing_Module import Timing, event_prob_by_expiry
from Event_Module import IdiosyncraticVol, TakeoutEvent, Earnings, Event, ComplexEvent, SysEvt_PresElection
from Distribution_Module import Distribution, Distribution_MultiIndex
from Events_sqlite import get_earnings_events
from timeline_chart import get_event_timeline
from term_structure import term_structure
from GetVolMC import get_vol_surface_from_events, get_vol_surface_spline, get_call_prices_from_events, get_option_sheet_from_events
from CreateMC import get_total_mc_distribution_from_events

from paul_resources import TakeoutParams, Symbols
from decorators import my_time_decorator

EarningsEvents = get_earnings_events()

#@my_time_decorator
def establish_events_by_expiry(events, expiry):
    return [evt for evt in events if event_prob_by_expiry(evt.timing_descriptor, expiry) > 0]

class Stock(object):
    elagolix_info = pd.read_excel('CLVS_RiskScenarios.xlsx',
                             header = [0],
                             index_col = [0,1],
                             sheet_name = 'Sub_States')

    fda_meeting = Event('CLVS', .1, 'Q2_2018', 'FDA Meeting')
    data = Event('CLVS', Distribution(pd.read_csv('CLVS.csv')), 'Q2_2018', 'Ph3_Data')
    elagolix = ComplexEvent('CLVS', Distribution_MultiIndex(elagolix_info), dt.date(2018,6,1), 'Elagolix Approval')
    all_other_events = [data, fda_meeting, elagolix]
    
    vol_surface_spline_cache = {}

    def __init__(self, stock):
        self.stock = stock
        self.vol_surface_spline_cache = {}

    @property
    def idio_vol(self):
        return IdiosyncraticVol(self.stock, .10)

    @property
    def earnings_events(self):
        #return get_earnings_events(self.stock)
        return [evt for evt in EarningsEvents if evt.stock == self.stock]

    @property
    def takeout_event(self):
        return TakeoutEvent(self.stock, TakeoutParams.loc[self.stock, 'Bucket'])
    
    @property
    def other_events(self):
        if self.stock == 'CLVS':
            return self.all_other_events
        else:
            return []
    
    # Think about how to use a cache for events
    @property
    def events_cache(self):
        return self.earnings_events
    
    @property
    def events(self):
        #return tuple(self.earnings_events + [self.idio_vol] + self.other_events)
        return tuple(self.earnings_events + [self.takeout_event] + [self.idio_vol] + self.other_events)
    
    @property
    def sorted_events(self):
        return sorted(self.events, key=lambda evt: Timing(evt.timing_descriptor).center_date)

    
    def get_event_timeline(self):
        get_event_timeline(self.events, self.stock, self.expiries)

    def get_term_structure(self):
        term_struc = term_structure(self.events, self.expiries, metric = 'IV', mc_iterations = 10**6)
        return term_struc.iloc[[term_struc.index.get_loc(1.00, method='nearest')], :]

    @property
    def expiries(self):
        return [dt.date(2018, 5, 21), dt.date(2018, 6, 21), dt.date(2018, 7, 21), dt.date(2018, 8, 21), dt.date(2018, 9, 21), dt.date(2018, 10, 21), dt.date(2018, 11, 21), dt.date(2018, 12, 21)]
    
    @property
    def best_index(self):
        return 'SPY'

    @property
    def beta(self):
        return 1.0

    @property
    def beta_to_SPY(self):
        return 1.0

    def get_beta(self, index: 'str'):
        return 1.0

    #events_cache = {}
    def get_call_prices(self, expiry, strikes = None, pretty = True):
        return get_call_prices_from_events(self.events, expiry, strikes = strikes, pretty = pretty, symbol = self.stock)

    def get_vol_surface(self, expiry, strikes = None, pretty = True):
        return get_vol_surface_from_events(self.events, expiry, strikes = strikes, pretty = pretty)
    
    def get_option_sheet(self, expiry, strikes = None, pretty = True):
        return get_option_sheet_from_events(self.events, expiry, strikes = strikes, pretty = pretty)

    def get_vol_surface_spline(self, expiry):
        if expiry in self.vol_surface_spline_cache:
            vol_surface_spline = self.vol_surface_spline_cache[expiry]
        else:
            vol_surface = self.get_vol_surface(expiry, pretty = False)
            vol_surface_spline = get_vol_surface_spline(vol_surface)
            self.vol_surface_spline_cache[expiry] = vol_surface_spline
        return vol_surface_spline

    def get_implied_vol(self, Option):
        vol_surface_spline = self.get_vol_surface_spline(Option.Expiry)
        return vol_surface_spline(Option.Strike)
    
    #@my_time_decorator    
    def get_option_price(self, Option):
        implied_vol = self.get_implied_vol(Option)
        return get_option_price(Option, implied_vol)


if __name__ == '__main__':
    @my_time_decorator
    def run():
        #@my_time_decorator
        def get_option_price_first_time(stock, option):
            option_price = stock.get_option_price(option)
            return option_price

        @my_time_decorator
        def get_option_price_second_time(stock, option):
            option_price = stock.get_option_price(option)
            return option_price
        
        @my_time_decorator
        def instantiate_expiries(stock, expiries):
            for expiry in expiries:
                stock.get_vol_surface_spline(expiry)
       
        @my_time_decorator
        def get_option_price_fast(stock, option):
            print(stock.stock, option.Expiry, option.Strike, option.Option_Type)
            return stock.get_option_price(option)
        
        @my_time_decorator
        def instantiate_expiries_multiple_stocks(stocks):
            instantiation_list = []
            for stock in stocks:
                my_list = (stock, stock.expiries)
                my_list = [(my_list[0], my_list[1][i])  for i in range(len(my_list[1]))]
                instantiation_list.extend(my_list)
            for stock, expiry in instantiation_list:
                stock.get_vol_surface_spline(expiry)

            stocks = [i[0] for i in instantiation_list]
            expiries = [i[1] for i in instantiation_list]
            
            pool = ThreadPool(8)
            #map(lambda stock, expiry: stock.get_vol_surface_spline(expiry), stocks, expiries)
            
            stock = Stock('VRTX')
            expiries = stock.expiries
            
            @my_time_decorator
            def pool_isolated():
                pool.map(lambda expiry: stock.get_vol_surface_spline(expiry), expiries)
            #pool_isolated()
            #list(map(lambda expiry: stock.get_vol_surface_spline(expiry), expiries))
            
            expiry = dt.date(2018, 12, 3)
            #pool.map(lambda stock: stock.get_vol_surface_spline(expiry), stocks)
            #list(map(lambda stock: stock.get_vol_surface_spline(expiry), stocks))
            
            
            """
            for stock in stocks:
                for expiry in stock.expiries:
                    stock.get_vol_surface_spline(expiry)
                #get_option_price_first_time(stock, option)
                #stock.earnings_events[0].timing_descriptor
            """

        @my_time_decorator
        def get_stock_objects(symbols: 'list of symbols'):
            return [Stock(symbol) for symbol in symbols]
        
        symbols = Symbols[0:20]
        stocks = get_stock_objects(symbols)
        instantiate_expiries_multiple_stocks(stocks)
        
        total_num_expiries = 0
        for stock in stocks:
            #print(stock.vol_surface_spline_cache)
            #print(stock.events)
            total_num_expiries += len(stock.vol_surface_spline_cache)
        #get_option_price_fast(stocks[3], option2)
        print('Num Stocks:', len(stocks), 'Num Expiries:', total_num_expiries)
    run()
