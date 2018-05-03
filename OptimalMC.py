import datetime as dt
from datetime import timedelta
import numpy as np
import logging
import math

from Timing_Module import get_time_to_expiry
from Event_Module import Earnings, IdiosyncraticVol
from decorators import my_time_decorator

# Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s', "%m/%d/%Y %H:%M")

file_handler = logging.FileHandler('MC_Distributions.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

mc_iterations = 10**6
EarningsDist = Earnings('CRBP', .05, 'Q2_2018').get_distribution(dt.date(2018, 7, 1)).mc_simulation(mc_iterations)
IdiosyncraticVolDist = IdiosyncraticVol('CRBP', .10).get_distribution(dt.date.today() + timedelta(365)).mc_simulation(mc_iterations)

@my_time_decorator
def optimally_get_mc_distribution_for_IdiosyncraticVol(event, expiry):
    mc_distribution = (IdiosyncraticVolDist - 1)*(event.at_the_money_vol/.10)*math.sqrt(get_time_to_expiry(expiry)) + 1
    logger.info('IdioVol: {}'.format(np.average(mc_distribution)))
    return mc_distribution

@my_time_decorator
def optimally_get_mc_distribution_for_Earnings(event, expiry):
    mc_distribution = (EarningsDist - 1)*(event.mean_move/.0504) + 1
    logger.info('Earnings: {}'.format(np.average(mc_distribution)))
    return mc_distribution

@my_time_decorator
def optimally_get_mc_distribution_for_event(event, expiry):
    if isinstance(event, Earnings):
        return optimally_get_mc_distribution_for_Earnings(event, expiry)
    
    elif isinstance(event, IdiosyncraticVol):
        return optimally_get_mc_distribution_for_IdiosyncraticVol(event, expiry)
    
    else:
        mc_distribution = event.get_distribution(expiry).mc_simulation(mc_iterations)
        logger.info('Other: {}'.format(np.average(mc_distribution)))
    
    return mc_distribution
