import pandas as pd
import datetime as dt
from functools import reduce
from biotech_class_run_9 import get_total_mc_distribution, get_option_sheet_from_mc_distribution, option_sheet
from Event_Module import IdiosyncraticVol, SysEvt_PresElection, Event, TakeoutEvent
from Distribution_Module import Distribution, Distribution_MultiIndex
from paul_resources import show_mc_distributions_as_line_chart
from Option_Module import Option, OptionPriceMC

# Define Expiries
expiry1 = dt.date(2018, 5, 21)
expiry2 = dt.date(2018, 6, 21)
expiry3 = dt.date(2018, 7, 21)
expiry4 = dt.date(2018, 8, 21)
expiry5 = dt.date(2018, 9, 21)
expiry6 = dt.date(2018, 10, 21)
expiry6 = dt.date(2018, 11, 21)
expiry6 = dt.date(2018, 12, 21)
expiries = [expiry1, expiry2, expiry3, expiry4, expiry5, expiry6]
expiries = [expiry1, expiry3, expiry5]
expiries = [expiry3]

# Define Events
event8_info = pd.read_excel('CLVS_RiskScenarios.xlsx',
                         header = [0],
                         index_col = [0,1],
                         sheet_name = 'Sub_States')

event0 = IdiosyncraticVol('CLVS', .15)
event1 = SysEvt_PresElection('CLVS', .02, 'Q2_2018')
event2 = Event('CLVS', .05, 'Q2_2018', 'Q2_Earnings')
event3 = Event('CLVS', .05, 'Q3_2018', 'Q3_Earnings')
event4 = Event('CLVS', .075, 'Q3_2018', 'Investor_Day')
event5 = Event('CLVS', .1, 'Q2_2018', 'FDA_Approval')
event6 = TakeoutEvent('CLVS', 4)
event7 = Event('CLVS', Distribution(pd.read_csv('CLVS.csv')), 'Q2_2018', 'Ph3_Data')
event8 = Event('CLVS', Distribution_MultiIndex(event8_info), 'Q3_2018', 'Elagolix_Approval')
events = [event0, event1, event2, event3, event4, event5, event6, event7, event8]
events = [event0, event6]

event0_bid = IdiosyncraticVol('CLVS', .15)
event1_bid = SysEvt_PresElection('CLVS', .01, 'Q2_2018')
event2_bid = Event('CLVS', .035, 'Q2_2018', 'Q2_Earnings')
event3_bid = Event('CLVS', .035, 'Q3_2018', 'Q3_Earnings')
event4_bid = Event('CLVS', .05, 'Q3_2018', 'Investor_Day')
event5_bid = Event('CLVS', .08, 'Q2_2018', 'FDA_Approval')
event6_bid = TakeoutEvent('CLVS', 4)
event7_bid = Event('CLVS', Distribution(pd.read_csv('CLVS.csv')), 'Q2_2018', 'Ph3_Data')
event8_bid = Event('CLVS', Distribution_MultiIndex(event8_info), 'Q3_2018', 'Elagolix_Approval')
events_bid = [event0, event1, event2, event3, event4, event5, event6, event7, event8]
events_bid = [event0_bid]

event0_ask = IdiosyncraticVol('CLVS', .15)
event1_ask = SysEvt_PresElection('CLVS', .03, 'Q2_2018')
event2_ask = Event('CLVS', .075, 'Q2_2018', 'Q2_Earnings')
event3_ask = Event('CLVS', .075, 'Q3_2018', 'Q3_Earnings')
event4_ask = Event('CLVS', .09, 'Q3_2018', 'Investor_Day')
event5_ask = Event('CLVS', .125, 'Q2_2018', 'FDA_Approval')
event6_ask = TakeoutEvent('CLVS', 2)
event7_ask = Event('CLVS', Distribution(pd.read_csv('CLVS.csv')), 'Q2_2018', 'Ph3_Data')
event8_ask = Event('CLVS', Distribution_MultiIndex(event8_info), 'Q3_2018', 'Elagolix_Approval')
events_ask = [event0, event1, event2, event3, event4, event5, event6, event7, event8]
events_ask = [event0_ask, event5, event6_ask]
events_ask = [event0_ask, event6_ask]



# Define Event Groupings
event_groupings = {}
for i in range(len(events)):
    event_groupings[i] = [events[i] for i in range(i+1)]

def term_structure(events, expiries, metric = 'IV', mc_iterations = 10**5):
    mc_distributions = list(map(lambda expiry: get_total_mc_distribution(events, expiry, mc_iterations=mc_iterations), expiries))
    implied_vols = list(map(lambda dist, expiry: get_option_sheet_from_mc_distribution(dist, expiry).loc[:, [(expiry, metric)]], mc_distributions, expiries))
    show_mc_distributions_as_line_chart(mc_distributions, labels = expiries)
    return reduce(lambda x,y: pd.merge(x, y, left_index=True, right_index=True), implied_vols)

#term_structure = term_structure(events, expiries, 'IV', mc_iterations=10**6)
#print(term_structure.round(3))
#expiry = dt.date(2018, 6, 15)
#mc_iterations = 10**6
#option_info = option_sheet(event_groupings.values(), expiry, mc_iterations)
#print(option_info)

#def spread(options, events):

def individual_option_pricing():
    option_type = 'Call'
    strike = 1.0
    expiry = dt.date(2018, 5, 10)

    expiries = pd.date_range(pd.datetime.today(), periods=100).tolist()
    expiries = [expiry]*100
    print(isinstance(expiries[0], dt.datetime))
    for expiry in expiries:
        option = Option(option_type, strike, expiry)
        mc_distribution = get_total_mc_distribution(events, expiry, mc_iterations=10**6)

        option_price = OptionPriceMC(option, mc_distribution)
        print((expiry, option_price))

def bid_ask(events_bid, events, events_ask, expiry, metric = 'IV', mc_iterations = 10**5):
    mc_distributions = list(map(lambda events: get_total_mc_distribution(events, expiry, mc_iterations=mc_iterations), [events_bid, events, events_ask]))
    implied_vols = list(map(lambda dist: get_option_sheet_from_mc_distribution(dist, expiry).loc[:, [(expiry, metric)]], mc_distributions))
    show_mc_distributions_as_line_chart(mc_distributions, labels = ['Bid - {}'.format(metric), 'Mid - {}'.format(metric), 'Ask - {}'.format(metric)])
    return reduce(lambda x,y: pd.merge(x, y, left_index=True, right_index=True), implied_vols)

expiry = dt.date(2018, 10, 1)
bid_ask_sheet = bid_ask(events_bid, events, events_ask, expiry, 'IV', mc_iterations=3*10**6)
print(bid_ask_sheet.round(3))
print("Takeout Assumptions-- Prob: {:2f}, Premium: {:2f}".format(event6_ask.takeout_prob, event6_ask.takeout_premium))
