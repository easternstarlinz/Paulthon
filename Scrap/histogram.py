import datetime as dt
import pandas as pd
import math
import numpy as np
import random
import copy
import matplotlib.pyplot as plt
from collections import namedtuple
from statistics import mean
from paul_resources import InformationTable, tprint, rprint
from decorators import my_time_decorator
from py_vollib.black_scholes.implied_volatility import black_scholes, implied_volatility
from Option_Module import get_time_to_expiry
from random import choices

count = np.arange(90, 111, 1)
bins = np.arange(90-.5, 112-.5, 1)
bins = 3
result, binEdges = np.histogram(count, bins)
print(type(binEdges))
print("Hello Jane")
for i in binEdges:
    print(i)
#binEdges = np.arange(90, 111, 1)
#count = []

#for i in binEdges[:-1]:
#    count.extend([i]*1)
#binEdges = 3
print(mean(count))
print(count)
print(bins)
print(binEdges)

plt.hist(count, bins, histtype='bar', rwidth=.8, color = 'blue', label = 'Rel. Frequency')

plt.title('Monte Carlo Simulation\n Check it out')
plt.xlabel('Percent Move')
plt.ylabel('Relative Frequency')
plt.legend()
plt.show()

def mc_distribution_to_distribution(mc_distribution,
                                    bins = 10**3+1,
                                    to_csv=False,
                                    csv_file_name = None):
    
    count, binEdges = np.histogram(mc_distribution, bins)
    bincenters = .5*(binEdges[1:] + binEdges[:-1])
 
    probs = [i / sum(count) for i in count]
    relative_moves = [bincenter / mean(bincenters) for bincenter in bincenters]
    pct_moves = [relative_move - 1 for relative_move in relative_moves]

    distribution_info = {'State': np.array(range(len(count))),
                         'Prob': probs,
                         'Pct_Move': pct_moves,
                         'Relative_Move': relative_moves}

    if to_csv is True:
        distribution_df = distribution_info_to_distribution(distribution_info).distribution_df
        pd.to_csv(csv_file_name)

    return distribution_info_to_distribution(distribution_info)


class Distribution(object):
    """Types of Distributions:
        --DataFrame
        --DataFrame with Residual Volatilities
        --MonteCarlo Distribution"""
    
    def __init__(self, distribution_df):
        """DataFrame({Index: 'States', Columns: ['Prob', 'Pct_Move', 'Relative_Price']}") -> 'Distribution Object'"""
        self.distribution_df = distribution_df

    @property
    def average_move(self):
        return sum([state.Prob*state.Pct_Move for state in self.distribution_df.itertuples()])
    
    @property
    def mean_move(self):
        return math.sqrt(sum([state.Prob*state.Pct_Move**2 for state in self.distribution_df.itertuples()]))

    
    def mc_simulation(self, iterations):
        pct_moves = self.distribution_df.loc[:, 'Pct_Move'].values.tolist()
        weights = self.distribution_df.loc[:, 'Prob'].values.tolist()
        results = random.choices(pct_moves, weights=weights, k=iterations)
        results = np.array(results)
        return results


    def __add__(self, other):
        i  = 1
        new_states = []
        new_probs = []
        new_pct_moves = []
        new_relative_prices = []
        
        for self_state in self.distribution_df.itertuples():
            for other_state in other.distribution_df.itertuples():
                index = i
                #new_state = "{}; {}".format(self_state.Index, other_state.Index)
                new_prob = self_state.Prob*other_state.Prob
                new_relative_price = self_state.Relative_Price*other_state.Relative_Price
                new_pct_move = new_relative_price - 1

                new_states.append(i)
                new_probs.append(new_prob)
                new_relative_prices.append(new_relative_price)
                new_pct_moves.append(new_pct_move)

                i += 1

        new_distribution_info = {'State': new_states,
                                 'Prob': new_probs,
                                 'Pct_Move': new_pct_moves,
                                 'Relative_Price': new_relative_prices}

        new_distribution_df = pd.DataFrame(new_distribution_info)
        new_distribution_df.set_index('State', inplace=True)
        new_distribution_df = new_distribution_df.loc[:, ['Prob', 'Pct_Move', 'Relative_Price']]
        return Distribution(new_distribution_df)
