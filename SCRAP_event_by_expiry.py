import datetime as dt
from option_model.Timing_Module import event_prob_by_expiry

expiry = dt.date(2018, 7, 1)
timing_descriptor = dt.date(2018, 7, 2)
timing_descriptor = 'Q1_2018'
timing_descriptor = '2018-05-01'

prob = event_prob_by_expiry(timing_descriptor, expiry)
print(prob)
