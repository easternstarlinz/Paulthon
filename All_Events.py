import pandas as pd
import datetime as dt
from Event_Module import IdiosyncraticVol, TakeoutEvent, Earnings, Event, ComplexEvent, SysEvt_PresElection
from Distribution_Module import Distribution, Distribution_MultiIndex
from Timing_Module import Timing
from Events_sqlite import get_earnings_events
from paul_resources import TakeoutParams
from decorators import my_time_decorator
from timeline_chart import get_event_timeline
from term_structure import term_structure
# Define Events

class Stock(object):
    elagolix_info = pd.read_excel('CLVS_RiskScenarios.xlsx',
                             header = [0],
                             index_col = [0,1],
                             sheet_name = 'Sub_States')

    fda_meeting = Event('CLVS', .1, 'Q2_2018', 'FDA Meeting')
    data = Event('CLVS', Distribution(pd.read_csv('CLVS.csv')), 'Q2_2018', 'Ph3_Data')
    elagolix = ComplexEvent('CLVS', Distribution_MultiIndex(elagolix_info), dt.date(2018,6,1), 'Elagolix Approval')
    all_other_events = [data, fda_meeting, elagolix]

    def __init__(self, stock):
        self.stock = stock

    @property
    def idio_vol(self):
        return IdiosyncraticVol(self.stock, .10)

    @property
    def earnings_events(self):
        return get_earnings_events(self.stock)

    @property
    def takeout_event(self):
        return TakeoutEvent(self.stock, TakeoutParams.loc[self.stock, 'Bucket'])
    
    @property
    def other_events(self):
        if self.stock == 'CLVS':
            return self.all_other_events
        else:
            return []

    @property
    def events(self):
        return self.earnings_events + [self.takeout_event] + [self.idio_vol] + self.other_events
    
    @property
    def sorted_events(self):
        return sorted(self.events, key=lambda evt: Timing(evt.timing_descriptor).center_date)

    
    def get_event_timeline(self):
        get_event_timeline(self.events, self.stock)

    def get_term_structure(self):
        term_struc = term_structure(self.events, self.expiries, metric = 'IV', mc_iterations = 10**5)
        return term_struc.iloc[[term_struc.index.get_loc(1.00, method='nearest')], :]
        #return term_structure(self.events, self.expiries, metric = 'IV', mc_iterations = 10**5)

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





@my_time_decorator
def run():
    stock = Stock('VRTX')
    #stock.get_event_timeline()
    term_structure = stock.get_term_structure()
    #print(stock.sorted_events)
    print(term_structure)
    #print(stock.expiries)
run()
