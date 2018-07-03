import numpy as np
import datetime as dt


from Stock_Module import Stock
from Option_Module import Option
from utility.decorators import my_time_decorator

@my_time_decorator
def run_all():
    stock = Stock('NBIX')
    #expiry = dt.date(2018, 10, 1)

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
    stock.get_event_timeline()
    
    #strikes = np.arange(.9, 1.1, .025)
    #option_sheet = stock.get_option_sheet(expiry, strikes = strikes)
    #term_structure = stock.get_term_structure(strikes = strikes)
    #print(option_sheet)
    #print(stock.events)
    #print(term_structure.to_string())
    #print(stock.events)
run_all()
