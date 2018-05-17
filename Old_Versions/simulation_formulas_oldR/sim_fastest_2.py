"""
formula for black scholes distribution:
S_t = S_o*exp(r*t - vol^2/2 + z*vol*sqrt(t)"""

import math
import random
import numpy as np
import itertools
import tkinter as tk
import matplotlib.pyplot as plt
from scipy.stats import norm
from time_decorator import my_time_decorator
import pandas as pd

def list_average(list_of_nums):
    """Compute the Average Value in a List"""
    return sum(list_of_nums)/float(len(list_of_nums))

#@my_time_decorator
def create_rand_nums(iterations:'int'=10**5) -> 'np_array':
    """Create a Numpy Array of Random Numbers"""
    return np.array([random.normalvariate(0,1) for i in range(iterations)])

#@my_time_decorator
def black_scholes_simulation(rand_nums: 'np_array', t = 1.0) -> 'np_array':
    """Run Black Scholes Simulation using an Array of already created Random Numbers as the Input"""
    stock, r, t, vol = 100, 0, t, .17
    stock_futures = stock*np.e**(r*t - (vol**2)*(t/2) + rand_nums*vol*np.sqrt(t))
    return stock_futures

rand_nums = create_rand_nums(iterations = 10**6)
simulation_results = black_scholes_simulation(rand_nums)
print([list_average(l) for l in [rand_nums, simulation_results]])

############################# Graph Component #####################################

def black_scholes_single_path_simulation(iterations = 10**5):
    daily_returns = []
    for i in range(iterations):
        rand_num = create_rand_nums(iterations = 1)
        price = black_scholes_simulation(rand_num, 1/252)
        daily_return = (price/100 - 1)[0]
        daily_returns.append(daily_return)
    return daily_returns

def run_vol_of_vol_calculations():
    rolling_timeframes = [5, 10, 100, 1000]
    vol_of_vols = []
    vols = []
    
    for rolling_timeframe in rolling_timeframes:
        daily_returns = pd.DataFrame(black_scholes_single_path_simulation(10**5))
        rolling_hvs = daily_returns.rolling(window = rolling_timeframe).std()*math.sqrt(252)
        
        vol_of_vol = np.nanstd(rolling_hvs)*math.sqrt(1)
        vol_of_vols.append(vol_of_vol)
        
        vol = np.nanstd(daily_returns)*math.sqrt(252)
        vols.append(vol)
        print("{}: {:.3f}".format(rolling_timeframe, vol_of_vol))
    
    info = {'Iterations': rolling_timeframes, 'Vol_of_Vol': vol_of_vols, 'Vol': vols}
    info_df = pd.DataFrame(info)
    info_df.set_index('Iterations', inplace=True)
    info_df = info_df.loc[:, ['Vol_of_Vol', 'Vol']]
    return info_df

vol_of_vol_df = run_vol_of_vol_calculations()
print(vol_of_vol_df)

@my_time_decorator
def run_histogram():
    """Create a Histogiram of the Simulation Results"""
    stock = 100
    bins = [float(i) for i in np.arange(stock*.2, stock*3.0, stock*.05)]

    plt.hist(simulation_results, bins, histtype='bar', rwidth=0.8, color='purple')

    plt.xlabel('St. Dev. Moves')
    plt.ylabel('Relative Frequency')
    plt.title('Beautiful Probabilitiy Distribution\nSmooth and Pretty!\n{:,d} Iterations'.format(len(simulation_results)))
    plt.legend()
    plt.show()

run_histogram()
