import datetime as dt
from Timing_Module import event_prob_by_expiry

expiry = dt.date(2018, 7, 1)
timing_descriptor = dt.date(2018, 6, 1)

prob = event_prob_by_expiry(timing_descriptor, expiry)
print(prob)
