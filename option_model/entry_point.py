#import sys
#sys.stdout = None

import numpy as np
import datetime as dt

from option_model.Stock_Module import Stock
from utility.decorators import my_time_decorator
from beta_model.scrubbing_processes import Index_Floor_Params

@my_time_decorator
def run_all():
    symbol = 'NBIX'
    stock = Stock(symbol)
    
    index_floor_params = Index_Floor_Params(SD_multiplier=1.0)

    beta_info = stock.get_beta_info(index_floor_params=index_floor_params)
    print(beta_info.round(3).to_string())

    """
    stock.get_event_timeline()
    call_option = Option('Call', 1.0, expiry)
    put_option = Option('Put', 1.0, expiry)

    call_price = stock.get_option_price(call_option)
    put_price =  stock.get_option_price(put_option)
    #print("Call: {:.5f}, Put: {:.5f}".format(call_price, put_price))

    for strike in np.arange(1, 1.5, .01):
        option = Option('Call', strike, expiry)
        option_price = stock.get_option_price(option)
        #print('Strike: {:.2f}, Price: {:.4f}'.format(strike, option_price))
    #term_structure = crbp.get_term_structure()
    """
    print('Getting Event Timeline')
    #stock.get_event_timeline()
    expiry = dt.date(2018, 11, 20)
    strikes = np.arange(.9, 1.1, .025)
    events = stock.events
    option_sheet = stock.get_option_sheet(expiry, strikes = strikes)
    term_structure = stock.get_term_structure(strikes = strikes)
    print(events)
    print(term_structure.to_string())
    print(stock.events)
    beta_value = stock.best_beta_value
    stock.get_event_timeline()
    print('End of the Module')
run_all()
