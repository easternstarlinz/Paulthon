from All_Events import Stock
from Option_Module import Option
import datetime as dt

crbp = Stock('CRBP')

#crbp.get_event_timeline()
expiry = dt.date(2018, 10, 1)
call_option = Option('Call', 1.0, expiry)
put_option = Option('Put', 1.0, expiry)

call_price = crbp.get_option_price(call_option)
put_price =  crbp.get_option_price(put_option)
print("Call: {:.5f}, Put: {:.5f}".format(call_price, put_price))

term_structure = crbp.get_term_structure()
vol_surface = crbp.get_vol_surface(expiry)
print(vol_surface)

