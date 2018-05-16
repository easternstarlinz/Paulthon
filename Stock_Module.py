import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter("ignore", category=RuntimeWarning)
import pandas as pd
import datetime as dt
from pprint import pprint
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

from Option_Module import Option, get_option_price, get_implied_volatility, get_option_price
from Timing_Module import Timing, event_prob_by_expiry
from Event_Module import IdiosyncraticVol, TakeoutEvent, Earnings, Event, ComplexEvent, SysEvt_PresElection
from Distribution_Module import Distribution, Distribution_MultiIndex
from Events_sqlite import get_earnings_events
from timeline_chart import get_event_timeline
from term_structure import term_structure
from GetVolMC import get_vol_surface_from_events, get_vol_surface_spline, get_call_prices_from_events, get_option_sheet_from_events, get_term_structure
from CreateMC import get_total_mc_distribution_from_events

from paul_resources import TakeoutParams, Symbols
from decorators import my_time_decorator

EarningsEvents = get_earnings_events()

class Stock(object):
    elagolix_info = pd.read_excel('CLVS_RiskScenarios2.xlsx',
                             header = [0],
                             index_col = [0,1],
                             sheet_name = 'Sub_States')

    fda_meeting = Event('CLVS', .1, 'Q2_2018', 'FDA Meeting')
    data = Event('CLVS', Distribution(pd.read_csv('CLVS.csv')), 'Q2_2018', 'Ph3_Data')
    elagolix = ComplexEvent('CLVS', Distribution_MultiIndex(elagolix_info), dt.date(2018,5,15), 'Elagolix Approval')
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

    def get_term_structure(self, strikes = None, mc_iterations = 10**6):
        term_struc = get_term_structure(self.events, self.expiries, strikes = strikes, mc_iterations = mc_iterations)
        return term_struc.round(2)
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
