import pandas as pd
import datetime as dt
from option_model.Event_Module import IdiosyncraticVol, TakeoutEvent, Event, ComplexEvent
from option_model.Distribution_Module import Distribution, Distribution_MultiIndex
from option_model.Timing_Module import Timing
from option_model.earnings_events import get_earnings_events
from paul_resources import TakeoutParams
from decorators import my_time_decorator
from option_model.timeline_chart import get_event_timeline
# Define Events

class Stock(object):
    event8_info = pd.read_excel('CLVS_RiskScenarios.xlsx',
                             header = [0],
                             index_col = [0,1],
                             sheet_name = 'Sub_States')

    fda_meeting = Event('CLVS', .1, 'Q2_2018', 'FDA Meeting')
    data = Event('CLVS', Distribution(pd.read_csv('CLVS.csv')), 'Q2_2018', 'Ph3_Data')
    elagolix = ComplexEvent('CLVS', Distribution_MultiIndex(event8_info), dt.date(2018,6,1), 'Elagolix Approval')
    all_other_events = [data, fda_meeting, elagolix]

    def __init__(self, stock):
        self.stock = stock

    @property
    def idio_vol(self):
        return IdiosyncraticVol(self.stock, .05)

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

@my_time_decorator
def run():
    stock = Stock('VRTX')
    print(stock.sorted_events)
    stock.get_event_timeline()
run()
