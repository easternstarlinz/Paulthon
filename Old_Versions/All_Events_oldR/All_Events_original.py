import pandas as pd
import datetime as dt
from option_model.Event_Module import IdiosyncraticVol, TakeoutEvent, Earnings, Event, ComplexEvent, SysEvt_PresElection
from option_model.Distribution_Module import Distribution, Distribution_MultiIndex
from option_model.Timing_Module import Timing
from option_model.earnings_events import get_earnings_events
from paul_resources import TakeoutParams
# Define Events

class Stock(object):
    def __init__(self, stock):
        self.stock = stock

    @property
    def earnings_events(self):
        return get_earnings_events(self.stock)

    @property
    def takeout_event(self):
        return TakeoutEvent(self.stock, TakeoutParams.loc[self.stock, 'Bucket'])

    @property
    def events(self):
        return self.earnings_events + [self.takeout_event]


event8_info = pd.read_excel('CLVS_RiskScenarios.xlsx',
                         header = [0],
                         index_col = [0,1],
                         sheet_name = 'Sub_States')

idio = IdiosyncraticVol('CLVS', .05)
takeout = TakeoutEvent('CLVS', 2)
pres_elec = SysEvt_PresElection('CLVS', .02)
earns_q2 = Earnings('CLVS', .05, dt.date(2018, 5, 15), 'Q2_2018')
earns_q3 = Earnings('CLVS', .05, dt.date(2018, 8, 15), 'Q3_2018')
earns_q4 = Earnings('CLVS', .05, dt.date(2018, 11, 15), 'Q4_2018')
fda_meeting = Event('CLVS', .1, 'Q2_2018', 'FDA Meeting')
data = Event('CLVS', Distribution(pd.read_csv('CLVS.csv')), 'Q2_2018', 'Ph3_Data')
elagolix = ComplexEvent('CLVS', Distribution_MultiIndex(event8_info), dt.date(2018,6,1), 'Elagolix Approval')
events = [idio, takeout, pres_elec, earns_q2, earns_q3, earns_q4, fda_meeting, elagolix]
earnings = get_earnings_events('CLVS')
sorted_events = sorted(events, key=lambda evt: Timing(evt.timing_descriptor).center_date)
print(earnings)



crbp = Stock('CRBP')
print(crbp)
print(crbp.stock)
print(crbp.earnings_events)
print(TakeoutParams)
print(crbp.takeout_event)
print(crbp.events)
