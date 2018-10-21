import pandas as pd
import datetime as dt
from functools import reduce
from biotech_class_run_9 import get_total_mc_distribution, get_option_sheet_from_mc_distribution
from option_model.Event_Module import IdiosyncraticVol, SysEvt_PresElection, Event, TakeoutEvent
from option_model.Distribution_Module import Distribution, Distribution_MultiIndex
from paul_resources import show_mc_distributions_as_line_chart
# Define Events

event8_info = pd.read_excel('CLVS_RiskScenarios.xlsx',
                         header = [0],
                         index_col = [0,1],
                         sheet_name = 'Sub_States')

event0 = IdiosyncraticVol('CLVS', .2)
event1 = SysEvt_PresElection('CLVS', .02, 'Q2_2018')
event2 = Event('CLVS', .05, 'Q2_2018', 'Q2_Earnings')
event3 = Event('CLVS', .05, 'Q3_2018', 'Q3_Earnings')
event4 = Event('CLVS', .075, 'Q3_2018', 'Investor_Day')
event5 = Event('CLVS', .1, 'Q2_2018', 'FDA_Approval')
event6 = TakeoutEvent('CLVS', 1)
event7 = Event('CLVS', Distribution(pd.read_csv('CLVS.csv')), 'Q3_2019', 'Ph3_Data')
event8 = Event('CLVS', Distribution_MultiIndex(event8_info), 'Q2_2018', 'Elagolix_Approval')
events = [event0, event1, event2, event3, event4, event5, event6, event7]
events = [event0,  event8]

# Define Expiries
expiry1 = dt.date(2018, 4, 27)
expiry2 = dt.date(2018, 5, 21)
expiry3 = dt.date(2018, 7, 18)
expiry4 = dt.date(2018, 10, 20)
expiry5 = dt.date(2019, 1, 20)
expiries = [expiry1, expiry2, expiry3, expiry4, expiry5]

# Define Event Groupings
event_groupings = {}
for i in range(len(events)):
    event_groupings[i] = [events[i] for i in range(i+1)]

def term_structure(events, expiries):
    mc_distributions = list(map(lambda expiry: get_total_mc_distribution(events, expiry), expiries))
    implied_vols = list(map(lambda dist, expiry: get_option_sheet_from_mc_distribution(dist, expiry).loc[:, ['IV']], mc_distributions, expiries))
    show_mc_distributions_as_line_chart(mc_distributions)
    return reduce(lambda x,y: pd.merge(x, y, left_index=True, right_index=True), implied_vols)

term_structure = term_structure(events, expiries)
print(term_structure)

#expiry = dt.date(2018, 6, 15)
#mc_iterations = 10**6
#option_info = option_sheet(event_groupings.values(), expiry, mc_iterations)
print(option_info)
#def spread(options, events)
