import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter("ignore", category=RuntimeWarning)

import datetime as dt

# Paul Modules
from Option_Module import Option, get_option_price 
from Timing_Module import Timing 
from Event_Module import IdiosyncraticVol, TakeoutEvent 
from timeline_chart import get_event_timeline
from term_structure import term_structure
from GetVolMC import get_vol_surface_from_events, get_vol_surface_spline, get_call_prices_from_events, get_option_sheet_from_events, get_term_structure

from get_best_betas_2 import get_betas_multiple_indices
from scrubbing_processes import default_stock_ceiling_params, default_index_floor_params, BEST_FIT_PERCENTILE

# Paul Utility Functions
from data.finance import TakeoutParams 

# Events
from data.earnings_events import EarningsEvents
from stock_events import all_other_events

class Stock(object):
    all_other_events = all_other_events
    
    vol_surface_spline_cache = {}

    def __init__(self, stock):
        self.stock = stock
        self.vol_surface_spline_cache = {}
    
    # Risk Metrics
    @property
    def relevant_indices(self):
        return ['SPY', 'QQQ', 'IBB', 'XBI']
    
    def get_beta_info(self,
                      lookback=252,
                      stock_ceiling_params=default_stock_ceiling_params,
                      index_floor_params=default_index_floor_params,
                      best_fit_param=BEST_FIT_PERCENTILE):
        """Get Beta info for the relevant indices. The user can input scrub_params or the other set of params."""
        beta_info = get_betas_multiple_indices(stock=self.stock,
                                               indices=self.relevant_indices,
                                               lookback=lookback,
                                               stock_ceiling_params=stock_ceiling_params,
                                               index_floor_params=index_floor_params,
                                               best_fit_param=best_fit_param)
        return beta_info

    @property
    def best_index(self):
        return 'SPY'

    @property
    def beta_to_best_index(self):
        return 1.0

    @property
    def beta_to_SPY(self):
        return 1.0

    def get_beta_to_index(self, index: 'str'):
        return 1.0


    """--------------------------------------------------------------------"""


    # Stock Events
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
        return [evt for evt in self.all_other_events if evt.stock == self.stock]
    
    @property
    def events(self):
        return tuple(self.earnings_events + [self.takeout_event] + [self.idio_vol] + self.other_events)
    
    @property
    def sorted_events(self):
        return sorted(self.events, key=lambda evt: Timing(evt.timing_descriptor).center_date)
    
    def get_event_timeline(self):
        get_event_timeline(self.events, self.stock, self.expiries)
    
    # Work-in-progress; think about how to use a cache for events
    @property
    def events_cache(self):
        return self.earnings_events


    """--------------------------------------------------------------------"""


    # Volatility / Options Calculations
    @property
    def expiries(self):
        return [dt.date(2018, 6, 21), dt.date(2018, 7, 21), dt.date(2018, 8, 21), dt.date(2018, 9, 21), dt.date(2018, 10, 21), dt.date(2018, 11, 21), dt.date(2018, 12, 21)]
    
    def strikes(self):
        return np.arange(.9, 1.1, .025)
    
    def get_term_structure(self, strikes=None, mc_iterations=10**6):
        print('These are the events:', self.events)
        term_struc = get_term_structure(self.events, self.expiries, strikes=strikes, mc_iterations=mc_iterations)
        return term_struc.round(2)
        return term_struc.iloc[[term_struc.index.get_loc(1.00, method='nearest')], :]

    #events_cache = {}
    def get_call_prices(self, expiry, strikes=None, pretty=True):
        return get_call_prices_from_events(self.events, expiry, strikes=strikes, pretty=pretty, symbol=self.stock)

    def get_vol_surface(self, expiry, strikes=None, pretty=True):
        return get_vol_surface_from_events(self.events, expiry, strikes=strikes, pretty=pretty)
    
    def get_option_sheet(self, expiry, strikes=None, pretty=True):
        return get_option_sheet_from_events(self.events, expiry, strikes=strikes, pretty=pretty)

    def get_vol_surface_spline(self, expiry):
        if expiry in self.vol_surface_spline_cache:
            vol_surface_spline = self.vol_surface_spline_cache[expiry]
        else:
            vol_surface = self.get_vol_surface(expiry, pretty=False)
            vol_surface_spline = get_vol_surface_spline(vol_surface)
            self.vol_surface_spline_cache[expiry] = vol_surface_spline
        return vol_surface_spline

    def get_implied_vol(self, Option):
        vol_surface_spline = self.get_vol_surface_spline(Option.Expiry)
        return vol_surface_spline(Option.Strike)
    
    def get_option_price(self, Option):
        implied_vol = self.get_implied_vol(Option)
        return get_option_price(Option, implied_vol)
