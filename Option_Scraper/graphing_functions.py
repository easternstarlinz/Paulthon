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

def to_pickle(content, file_name):
    pickle_file = open('{}.pkl'.format(file_name), 'wb')
    pickle.dump(content, pickle_file, pickle.HIGHEST_PROTOCOL)
    pickle_file.close()

def to_pickle_and_CSV(content, file_name):
    to_pickle(content, file_name)
    content.to_csv("{}.csv".format(file_name))

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

def merge_dfs_horizontally(dfs: 'list of dfs'):
    if len(dfs) == 1:
        return dfs[0]
    else:
        return reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), dfs)

def append_dfs_vertically(dfs: 'list of dfs'):
    if len(dfs) == 1:
        return dfs[0]
    else:
        return reduce(lambda x, y: x.append(y), dfs)

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

def get_histogram_from_array(results: 'array of numbers', bins = 10**2, title = 'Monte Carlo Simulation\n Simulated Distribution'):
    #start, end, interval = -.5, .5, .025
    #bins = np.arange(start - interval/2, end + interval/2, interval)
    
    plt.hist(results, bins, histtype='bar', rwidth=1.0, color = 'blue', label = 'Rel. Frequency')
    plt.title(title)
    plt.xlabel('Relative Price')
    plt.ylabel('Relative Frequency')
    plt.legend()
    plt.show()


def show_mc_distributions_as_line_chart(mc_distributions, labels = None):
    i = 0
    for mc_distribution in mc_distributions:
        min_cutoff = np.percentile(mc_distribution, 0)
        max_cutoff = np.percentile(mc_distribution, 100)
        mc_distribution = [i for i in mc_distribution if (i > min_cutoff) and (i < max_cutoff)]
        
        #print('Percentiles', (np.percentile(mc_distribution, .1), np.percentile(mc_distribution, .9)))
        #print('Min_Max', (np.min(mc_distribution), np.max(mc_distribution)))
        
        bin_min = np.percentile(mc_distributions[-1], .25)
        bin_max = np.percentile(mc_distributions[-1], 99.75)
        y, binEdges = np.histogram(mc_distribution, bins=np.arange(bin_min, bin_max, .00875))
        
        bincenters = .5*(binEdges[1:] + binEdges[:-1])
        
        xnew = np.linspace(bin_min+.01, bin_max-.01, num=10**3, endpoint=True)

        #p = np.polyfit(bincenters, y, 3)
        #y_p = np.polyval(p, xnew)
        f = interp1d(bincenters, y, kind='cubic')
        #f = UnivariateSpline(bincenters, y, s=1)
        #f = UnivariateSpline(xnew, y, s=1)
        #pylab.plot(xnew, f(xnew), '-', label = "Events {}".format(i))
        
        if labels == None:
            label = "Distribution {}".format(i+1)
        else:
            label = labels[i]
        pylab.plot(bincenters, y, '-', label=label)
        i += 1
    pylab.legend()
    pylab.show()

if __name__ == '__main__':
    pass
