import datetime as dt
import numpy as np
import pandas as pd
import pickle
import math
import decimal
import copy
import pprint
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm
import pylab
import scipy.stats as ss
import statsmodels.api as sm
from functools import reduce
from sklearn.linear_model import LinearRegression
from decorators import my_time_decorator
from scipy.interpolate import interp1d, UnivariateSpline
import logging

# Paul Modules
from ols import OLS
from ols2 import OLS as MainOLS

# File Saving Utility Functions
def to_pickle(content, file_name):
    pickle_file = open('{}.pkl'.format(file_name), 'wb')
    pickle.dump(content, pickle_file, pickle.HIGHEST_PROTOCOL)
    pickle_file.close()

def to_pickle_and_CSV(content, file_name):
    to_pickle(content, file_name)
    content.to_csv("{}.csv".format(file_name))

# Logging Utility Function
def setup_standard_logger(file_name):
    # Logging Setup
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s', "%m/%d/%Y %H:%M")

    file_handler = logging.FileHandler('{}.log'.format(file_name))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

# DataFrame Utility Functions
def merge_dfs_horizontally(dfs: 'list of dfs', suffixes=('_x', '_y')):
    if len(dfs) == 1:
        return dfs[0]
    else:
        return reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True, suffixes=suffixes), dfs)

def append_dfs_vertically(dfs: 'list of dfs'):
    if len(dfs) == 1:
        return dfs[0]
    else:
        return reduce(lambda x, y: x.append(y), dfs)

# Printing Utility Functions
def tprint(*args):
    print("TPrint Here--------")
    for arg in args:
        print("Type: ", type(arg), "\n", "Obj: ", arg, sep='')

def rprint(*args):
    print("RPrint Here--", end="")
    for arg in args:
        if args.index(arg) == len(args)-1:
            e = " \n"
        else:
            e = ", "
        if type(arg) is not str:
            print(round(arg, 3), end = e)
        else:
            print(arg, end = e)

def lprint(*args):
    print("LPrint Here--------")
    for arg in args:
        print("Len: ", len(arg), "\n", sep='')
