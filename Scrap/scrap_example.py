from Event_Module import IdiosyncraticVol
import datetime as dt
from Distribution_Module import Distribution, float_to_bs_distribution
import numpy as np
import pandas as pd

event = IdiosyncraticVol('CLVS', .1)
distribution = event.get_distribution(dt.date(2018,5,10))
print(distribution.mean_move, distribution.average_move, distribution.straddle)
distribution.get_histogram()

event_input_distribution = Distribution(event.event_input_distribution_df)
print(event_input_distribution.mean_move, event_input_distribution.average_move, event_input_distribution.straddle)

event_input_dist = event.event_input
print(event_input_dist.mean_move, event_input_dist.average_move, event_input_dist.straddle)

dist = float_to_bs_distribution(.5)
print("HERE",dist.mean_move, dist.average_move, dist.straddle)
