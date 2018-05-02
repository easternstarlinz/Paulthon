from All_Events import Stock
from Option_Module import Option
import datetime as dt
from decorators import my_time_decorator
import numpy as np

@my_time_decorator
def run_all():
    stock = Stock('CRBP')

    stock.get_event_timeline()
    expiry = dt.date(2018, 10, 1)
    call_option = Option('Call', 1.0, expiry)
    put_option = Option('Put', 1.0, expiry)

    call_price = stock.get_option_price(call_option)
    put_price =  stock.get_option_price(put_option)
    print("Call: {:.5f}, Put: {:.5f}".format(call_price, put_price))

    for strike in np.arange(1, 1.5, .01):
        option = Option('Call', strike, expiry)
        option_price = stock.get_option_price(option)
        #print('Strike: {:.2f}, Price: {:.4f}'.format(strike, option_price))
    #term_structure = crbp.get_term_structure()
    vol_surface = stock.get_vol_surface(expiry, pretty = True)
    call_prices = stock.get_call_prices(expiry, pretty = True)
    #print(call_prices)
run_all()
