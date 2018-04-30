import datetime as dt
import pandas as pd
from pandas.tseries.offsets import BDay
import math
import numpy as np
import random
import copy
from pprint import pprint
from ppretty import ppretty
import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
from collections import namedtuple
from statistics import mean
from py_vollib.black_scholes.implied_volatility import black_scholes, implied_volatility
import logging

from Option_Module import get_time_to_expiry
from Distribution_Module import Distribution, float_to_distribution
from paul_resources import InformationTable, tprint, rprint
from decorators import my_time_decorator



# Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s', "%m/%d/%Y %H:%M")

file_handler = logging.FileHandler('timing_descriptors.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


today = pd.datetime.today()


descriptors = pd.read_csv('TimingDescriptors.csv')

TimingMappings = pd.read_excel('TimingMappings.xlsx',
                         header = [0,1],
                         index_col = [0,1],
                         sheet_name = 'TimingMappings')
TimingMappings = TimingMappings.reset_index().set_index('level_1').loc[:, ['Start', 'End']]

mappings = pd.read_excel('TimingMappings.xlsx',
                         header = [0,1],
                         index_col = [0,1],
                         sheet_name = 'TimingMappings')

def validate_date_string(date_text):
    try:
        dt.datetime.strptime(date_text, '%Y-%m-%d')
    except:
        return False
    else:
        return True

def date_string_to_date(date_text):
    return dt.datetime.strptime(date_text, '%Y-%m-%d').date()


def get_date_from_timing_descriptor(timing_descriptor, which = 'Start'):
    
    #This logger statement produced an error.
    #logger.info('Timing Descriptor:', timing_descriptor)

    if timing_descriptor is None:
        return dt.date.today()
    elif validate_date_string(timing_descriptor):
        return date_string_to_date(timing_descriptor)
        #return dt.datetime.strptime(timing_descriptor, '%Y-%m-%d').date()
    elif isinstance(timing_descriptor, (dt.date, dt.datetime)):
        return timing_descriptor
    else:
        try:
            timing_period = timing_descriptor[0:-5]
            
            year = int("{}".format(timing_descriptor[-4:]))
            month = TimingMappings.loc[timing_period, (which, 'Month')]
            day = TimingMappings.loc[timing_period, (which, 'Day')]
    
            return dt.date(year, month, day)

        except:
            raise ValueError('Incorrect data format for timing_descriptor')


#@my_time_decorator
def event_prob_by_expiry(timing_descriptor = None,
                         expiry = None,
                         reference_date = dt.date.today()):
    """I need to optimze this function for accuracy and speed"""
    if timing_descriptor is None:
        return 1.0
    
    if expiry is None:
        return 1.0
    
    if isinstance(expiry, dt.datetime):
        expiry = expiry.date()
    
    if validate_date_string(timing_descriptor):
        timing_descriptor = date_string_to_date(timing_descriptor)

    if isinstance(timing_descriptor, dt.datetime):
        timing_descriptor = timing_descriptor.date()

    if isinstance(timing_descriptor, dt.date):
        if timing_descriptor < reference_date:
            return 0
        elif  timing_descriptor <= expiry:
            return 1.0
        else:
            return 0.0
            
    else:
        event_start_date = get_date_from_timing_descriptor(timing_descriptor, 'Start')
        
        if event_start_date > expiry:
            return 0
        
        event_end_date = get_date_from_timing_descriptor(timing_descriptor, 'End')
        
        if event_end_date < reference_date:
            return 0

        else:
            current_event_start_date = max(reference_date, event_start_date)
            #days_to_expiry = max((expiry - reference_date).days, 0) + 1
            event_days_before_expiry = (expiry - current_event_start_date).days + 1
            total_event_days = (event_end_date - current_event_start_date).days + 1
            
            """
            logger.info(timing_descriptor, isinstance(timing_descriptor, dt.date), type(timing_descriptor))
            logger.info("Ref Date: {}, Event_Start_Date: {}, Current_Event_Start_Date: {}, Event_End_Date: {}, Expiry: {}, Days_Before_Expiry: {}, Total_Event_Days: {}".format(reference_date,
                                                event_start_date,
                                                current_event_start_date,
                                                event_end_date,
                                                expiry,
                                                event_days_before_expiry,
                                                total_event_days))
            """

        """
        event_days_before_expiry = total_event_days - (expiry - evvent_start_date
        event_days_before_expiry = 0
        date = max(reference_date, event_start_date)
        while date <= event_end_date and date <= expiry:
           event_days_before_expiry += 1
           date += timedelta(1)
        """
        return event_days_before_expiry / total_event_days
    
"""
if __name__ == '__main__':
    prob = event_prob_by_expiry('2H_2018', dt.date(2018, 9, 25))
    print(prob)
"""
#print(years, guidance, halves, months, weeks)
class Timing(object):
    def __init__(self, timing_descriptor: 'str or date'  = None, reference_date = dt.date.today()):
        if timing_descriptor is None:
            self.timing_descriptor = dt.date.today()
        self.timing_descriptor = timing_descriptor
        self.reference_date = reference_date

    @property
    def timing_descriptor_abbrev(self):
        return self.timing_descriptor[0:-5]

    @property
    def event_start_date(self):
        return get_date_from_timing_descriptor(self.timing_descriptor, 'Start')

    @property
    def event_end_date(self):
        return get_date_from_timing_descriptor(self.timing_descriptor, 'End')
    
    @property
    def timing_duration(self):
        return self.event_end_date - self.event_start_date

    @property
    def center_date(self):
        time_delta = self.event_end_date - self.event_start_date
        return self.event_start_date + time_delta / 2

    @property
    def current_event_start_date(self):
        if self.reference_date > self.event_end_date:
            return "Event has passed"
        else:
            return max(self.event_start_date, self.reference_date)
    
    @property
    def current_event_end_date(self):
        if self.reference_date > self.event_end_date:
            return "Event has passed"
        else:
            return self.event_end_date
    
    @property
    def current_center_date(self):
        time_delta = self.current_event_end_date - self.current_event_start_date
        return self.current_event_start_date + time_delta / 2

    def get_event_prob_by_expiry(self, expiry):
        return event_prob_by_expiry(self.timing_descriptor, expiry)


if __name__ == '__main__':
    print(Timing('2H_2018').center_date)
    t = Timing('2H_2018')
    pprint(vars(t))
    pprint(dir(t))
