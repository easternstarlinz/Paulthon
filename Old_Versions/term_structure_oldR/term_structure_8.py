import pandas as pd
import datetime as dt
from functools import reduce
from biotech_class_run_9 import get_total_mc_distribution, get_option_sheet_from_mc_distribution
from option_model.Event_Module import IdiosyncraticVol, SysEvt_PresElection, Event, TakeoutEvent, Earnings
from option_model.Distribution_Module import Distribution, Distribution_MultiIndex
from paul_resources import show_mc_distributions_as_line_chart
from option_model.Option_Module import Option, OptionPriceMC
from decorators import my_time_decorator
import logging

# Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)

formatter = logging.Formatter('%(levelname)s:%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

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

idio = IdiosyncraticVol('CLVS', .15)
earns_q2 = SysEvt_PresElection('CLVS', .02, 'Q2_2018')
earns_q3 = Earnings('CLVS', .05, 'Q2_2018', 'Q2_Earnings')
earns_q4 = Earnings('CLVS', .05, 'Q3_2018', 'Q3_Earnings')
event4 = Earnings('CLVS', .05, 'Q4_2018', 'Q4_Earnings')
event5 = Event('CLVS', .1, 'Q2_2018', 'FDA_Approval')
takeout = TakeoutEvent('CLVS', 2)
event7 = Event('CLVS', Distribution(pd.read_csv('CLVS.csv')), 'Q2_2018', 'Ph3_Data')
event8 = Event('CLVS', Distribution_MultiIndex(event8_info), 'Q2_2018', 'Elagolix_Approval')
events = [idio, earns_q2, earns_q3, earns_q4, takeout, event8]
events = [takeout]

events_bid = [event.event_bid for event in events]
events_ask = [event.event_ask for event in events]

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

"""
expiry = dt.date(2018, 10, 1)
bid_ask_sheet = bid_ask(events_bid, events, events_ask, expiry, 'IV', mc_iterations=3*10**6)
print(bid_ask_sheet.round(3))
print("Takeout Assumptions-- Prob: {:2f}, Premium: {:2f}".format(event6_ask.takeout_prob, event6_ask.takeout_premium))
"""

def option_pricing():
    option_type = 'Call'
    strike = 1.0
    expiry = dt.date(2018, 10, 10)
    option = Option(option_type, strike, expiry)

    mc_distribution = get_total_mc_distribution(events, expiry, mc_iterations=10**6)
    option_price = OptionPriceMC(option, mc_distribution)
    print("Expiry: {}, Price: {}".format(expiry, option_price))

def spread_pricing(options: 'list of options', quantities: 'list of quantities', events, events_bid, events_ask, mc_iterations=10**6):
    mc_distribution = get_total_mc_distribution(events, options[0].Expiry, mc_iterations=mc_iterations)
    mc_distribution_bid = get_total_mc_distribution(events_bid, options[0].Expiry, mc_iterations=mc_iterations)
    mc_distribution_ask = get_total_mc_distribution(events_ask, options[0].Expiry, mc_iterations=mc_iterations)
     
    option_prices = []
    for i in range(len(options)):
        #mc_distribution = get_total_mc_distribution(events, option.Expiry, mc_iterations=mc_iterations)
        if quantities[i] > 0:
            option_price = OptionPriceMC(options[i], mc_distribution_bid)
            side = 'Bid'
        else:
            option_price = OptionPriceMC(options[i], mc_distribution_ask)
            side = 'Ask'
        print("Strike: {:.3f}, {} Price: {:.3f}".format(options[i].Strike, side, option_price))
        """
        try:
            call_spread = option_prices[-1] - option_price
            print("Call Spread: {:2f}".format(call_spread))
        except Exception:
            pass
        """
        option_prices.append(option_price)
    
    spread_price = sum([option_price*quantity for option_price, quantity in zip(option_prices, quantities)])
    print("Spread Price: {:.3f}".format(spread_price))
    return spread_price

def spread_pricing(options: 'list of options', quantities: 'list of quantities', events, description = None, mc_iterations=10**6):
    mc_distribution = get_total_mc_distribution(events, options[0].Expiry, mc_iterations=mc_iterations)
     
    option_prices = []
    for i in range(len(options)):
        option_price = OptionPriceMC(options[i], mc_distribution)
        option_prices.append(option_price)
        logger.info("Strike: {:.3f}, {} Price: {:.3f}".format(options[i].Strike, description, option_price))
    
    spread_price = sum([option_price*quantity for option_price, quantity in zip(option_prices, quantities)])
    logger.info("Spread Price: {:.3f}".format(spread_price))
    return spread_price

@my_time_decorator
def spread_pricing_bid_ask(options: 'list of options', quantities: 'list of quantities', event_groupings, event_grouping_names, mc_iterations=10**6):
    spread_prices = []
    for i in range(len(event_groupings)):
        spread_price = spread_pricing(options, quantities, event_groupings[i], event_grouping_names[i], mc_iterations)
        spread_prices.append(spread_price)
    
    info = {'Level': event_grouping_names,
            'Spread': spread_prices}

    info = pd.DataFrame(info).set_index('Level')
    return info

option_type = 'Call'
expiry = dt.date(2018, 8, 1)

option1 = Option(option_type, 1.10, expiry)
option2 = Option(option_type, 1.10, expiry)
option3 = Option(option_type, 1.10, expiry)

options = [option1, option2, option3]
quantities = [1, 1, 1]

event_groupings = [events_bid, events, events_ask]
event_grouping_names = ['Bid', 'Mid', 'Ask']

spread_prices = spread_pricing_bid_ask(options, quantities, event_groupings, event_grouping_names, mc_iterations = 10**6)
print(spread_prices.round(3))
print(events_bid, events, events_ask, end = "\n")
