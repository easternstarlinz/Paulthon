import datetime as dt
import pandas as pd
import math
import numpy as np
import random
import copy
import matplotlib.pyplot as plt
from collections import namedtuple
from statistics import mean
from paul_resources import InformationTable, tprint, rprint, get_histogram_from_array
from decorators import my_time_decorator
from py_vollib.black_scholes.implied_volatility import black_scholes, implied_volatility
from Option_Module import get_time_to_expiry
import logging

# Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(message)s')

file_handler = logging.FileHandler('mc_transform.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

#logging.disable(logging.CRITICAL)

class Distribution(object):
    """
    Distribution object-- DataFrame wrapped as an object to provide attributes and methods.
        -mean_move (sqrt)
        -average move
        -straddle
        -method to return MonteCarlo simulation of size n iterations
    Methodology to add: DataFrame with Residual Volatilities
    """
    def __init__(self, distribution_df):
        """DataFrame({Index: 'States', Columns: ['Prob', 'Pct_Move', 'Relative_Price']}") -> 'Distribution Object'"""
        self.distribution_df = distribution_df

    @property
    def average_move(self):
        return sum([state.Prob*state.Pct_Move for state in self.distribution_df.itertuples()])
    
    @property
    def straddle(self):
        return sum([state.Prob*abs(state.Pct_Move) for state in self.distribution_df.itertuples()])

    @property
    def mean_move(self):
        return math.sqrt(sum([state.Prob*state.Pct_Move**2 for state in self.distribution_df.itertuples()]))

    def mc_simulation(self, iterations = 10**6):
        relative_prices = self.distribution_df.loc[:, 'Relative_Price'].values.tolist()
        weights = self.distribution_df.loc[:, 'Prob'].values.tolist()
        results = random.choices(relative_prices, weights=weights, k=iterations)
        results = np.array(results)
        return results

    def get_histogram(self, iterations = 10**6, bins = 10**2):
        simulation_results = self.mc_simulation(iterations = iterations)
        get_histogram_from_array(simulation_results, bins = bins)
        

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

        #return distribution_info_to_distribution(new_distribution_info)
        new_distribution_df = pd.DataFrame(new_distribution_info).set_index('State').loc[:, ['Prob', 'Pct_Move', 'Relative_Price']]
        return Distribution(new_distribution_df)

    def __mul__(self, other):
        states = [state.Index for state in self.distribution_df.itertuples()]
        probs = [state.Prob for state in self.distribution_df.itertuples()]
        new_pct_moves = []
        new_relative_prices = []
        
        for state in self.distribution_df.itertuples():
            new_pct_move = state.Pct_Move*other
            new_relative_price = new_pct_move + 1
            
            new_pct_moves.append(new_pct_move)
            new_relative_prices.append(new_relative_price)

        new_distribution_info = {'State': states,
                                 'Prob': probs,
                                 'Pct_Move': new_pct_moves,
                                 'Relative_Price': new_relative_prices}
        
        new_distribution_df = pd.DataFrame(new_distribution_info).set_index('State').loc[:, ['Prob', 'Pct_Move', 'Relative_Price']]
        return Distribution(new_distribution_df)
        
class Distribution_MultiIndex(Distribution):
    def __init__(self, df):
        self.input_df = df
        self.positive_scenario = df.loc[['Positive']]
        self.negative_scenario = df.loc[['Negative']]
        self.new = self.positive_scenario.append(self.negative_scenario)
        self.core_scenarios = df.index.levels[0].tolist()
        self.all_states = df.loc[['Positive', 'Negative']].index.tolist()
    @property
    def core_scenario_dfs(self):
        return [self.input_df.loc[i] for i in self.core_scenarios]

    @property
    def positive_scenario_states(self):
        return self.positive_scenario.index.tolist()

    @property
    def negative_scenario_states(self):
        return self.negative_scenario.index.tolist()

    @property
    def positive_scenario_wgt_move(self):
        probs = self.positive_scenario.loc[:, 'Relative_Prob'].values.tolist()
        pct_moves = self.positive_scenario.loc[:, 'Pct_Move'].values.tolist()
        return sum([prob*pct_move for prob, pct_move in zip(probs, pct_moves)])
    
    @property
    def negative_scenario_wgt_move(self):
        probs = self.negative_scenario.loc[:, 'Relative_Prob'].values.tolist()
        pct_moves = self.negative_scenario.loc[:, 'Pct_Move'].values.tolist()
        return sum([prob*pct_move for prob, pct_move in zip(probs, pct_moves)])
    
    @property 
    def prob_success(self):
        return -self.negative_scenario_wgt_move / (self.positive_scenario_wgt_move - self.negative_scenario_wgt_move)

    def set_positive_scenario_substate_prob(self, state, new_relative_prob):
        all_states = self.positive_scenario_states
        unchanged_states = [i for i in all_states if i[1] != state]
        
        old_relative_prob = self.positive_scenario.loc[('Positive', state), 'Relative_Prob']
        old_total_prob_other_states = 1 - old_relative_prob
        new_total_prob_other_states = 1 - new_relative_prob
        adjustment_mult = new_total_prob_other_states / old_total_prob_other_states

        # Set New Probabilities
        self.positive_scenario.loc[('Positive', state), 'Relative_Prob'] = new_relative_prob
        for i in unchanged_states:
            self.positive_scenario.loc[('Positive', i[1]), 'Relative_Prob'] *= adjustment_mult
    
    def set_negative_scenario_substate_prob(self, state, new_relative_prob):
        all_states = self.negative_scenario_states
        unchanged_states = [i for i in all_states if i[1] != state]
        
        old_relative_prob = self.negative_scenario.loc[('Negative', state), 'Relative_Prob']
        old_total_prob_other_states = 1 - old_relative_prob
        new_total_prob_other_states = 1 - new_relative_prob
        adjustment_mult = new_total_prob_other_states / old_total_prob_other_states

        # Set New Probabilities
        self.negative_scenario.loc[('Negative', state), 'Relative_Prob'] = new_relative_prob
        for i in unchanged_states:
            self.negative_scenario.loc[('Negative', i[1]), 'Relative_Prob'] *= adjustment_mult
    
    def set_substate_prob(self, state, new_relative_prob):
        if state[0] == 'Positive':
            all_states = self.positive_scenario_states
            unchanged_states = [i for i in all_states if i != state]
           
            old_relative_prob = self.positive_scenario.loc[state, 'Relative_Prob']
            old_total_prob_other_states = 1 - old_relative_prob
            new_total_prob_other_states = 1 - new_relative_prob
            adjustment_mult = new_total_prob_other_states / old_total_prob_other_states

            # Set New Probabilities
            self.positive_scenario.loc[state, 'Relative_Prob'] = new_relative_prob
            for i in unchanged_states:
                self.positive_scenario.loc[i, 'Relative_Prob'] *= adjustment_mult
        elif state[0] == 'Negative':
            all_states = self.negative_scenario_states
            unchanged_states = [i for i in all_states if i != state]
           
            old_relative_prob = self.negative_scenario.loc[state, 'Relative_Prob']
            old_total_prob_other_states = 1 - old_relative_prob
            new_total_prob_other_states = 1 - new_relative_prob
            adjustment_mult = new_total_prob_other_states / old_total_prob_other_states

            # Set New Probabilities
            self.negative_scenario.loc[state, 'Relative_Prob'] = new_relative_prob
            for i in unchanged_states:
                self.negative_scenario.loc[i, 'Relative_Prob'] *= adjustment_mult
        else:
            raise ValueError
        
        self.calc_absolute_probs()

    def calc_absolute_probs(self):    
        for state in self.positive_scenario_states:
            self.positive_scenario.loc[state, 'Prob'] = self.positive_scenario.loc[state, 'Relative_Prob']*self.prob_success
        for state in self.negative_scenario_states:
            self.negative_scenario.loc[state, 'Prob'] = self.negative_scenario.loc[state, 'Relative_Prob']*(1-self.prob_success)

    def set_prob_success(self, new_prob_success):
        for state in self.positive_scenario_states:
            self.positive_scenario.loc[state, 'Prob'] = self.positive_scenario.loc[state, 'Relative_Prob']*new_prob_success
        for state in self.negative_scenario_states:
            self.negative_scenario.loc[state, 'Prob'] = self.negative_scenario.loc[state, 'Relative_Prob']*(1-new_prob_success)

        center_shift = sum([state.Prob*state.Pct_Move for state in self.distribution_df.itertuples()])
        for state in self.positive_scenario_states:
            self.positive_scenario.loc[state, 'Pct_Move'] += -center_shift
            self.positive_scenario.loc[state, 'Relative_Price'] = self.positive_scenario.loc[state, 'Pct_Move'] + 1
        for state in self.negative_scenario_states:
            self.negative_scenario.loc[state, 'Pct_Move'] += -center_shift
            self.negative_scenario.loc[state, 'Relative_Price'] = self.negative_scenario.loc[state, 'Pct_Move'] + 1

    @property
    def distribution_df(self):
        return self.positive_scenario.append(self.negative_scenario)

#--------------------------------------Functions in the Distribution_Module---------------------------------#
def float_to_distribution(move_input: 'float', csv_file):
    distribution_df = pd.read_csv(csv_file).set_index('State')
    mean_move = Distribution(distribution_df).mean_move
    distribution_df.loc[:, 'Pct_Move'] *= (move_input/mean_move)
    distribution_df.loc[:, 'Relative_Price'] = distribution_df.loc[:, 'Pct_Move'] + 1
    #new_dist = Distribution(distribution_df)
    #print(new_dist.mean_move, new_dist.average_move, new_dist.straddle)
    return Distribution(distribution_df)

def float_to_event_distribution(move_input: 'float'):
    return float_to_distribution(move_input, 'Event.csv')

def float_to_volbeta_distribution(move_input: 'float'):
    return float_to_distribution(move_input, 'VolbetaDistribution.csv')

def float_to_bs_distribution(move_input: 'float'):
    return float_to_distribution(move_input, 'BlackScholes.csv')

def distribution_info_to_distribution(distribution_info):
    distribution_df = pd.DataFrame(distribution_info).set_index('State').loc[:, ['Prob', 'Pct_Move', 'Relative_Price']]
    return Distribution(distribution_df)

def mc_distribution_to_distribution(mc_distribution,
                                    bins = 10**4+1,
                                    to_csv=False,
                                    csv_file_name = None):
    
    mean_mc_price = mean(mc_distribution)
    
    counts, binEdges = np.histogram(mc_distribution, bins)
    binCenters = .5*(binEdges[1:] + binEdges[:-1])
    
    probs = [i / sum(counts) for i in counts]
    relative_moves = [binCenter / mean_mc_price for binCenter in binCenters]
    pct_moves = [relative_move - 1 for relative_move in relative_moves]

    distribution_info = {'State': np.array(range(len(counts))),
                         'Prob': probs,
                         'Pct_Move': pct_moves,
                         'Relative_Price': relative_moves}

    if to_csv is True:
        distribution_df = distribution_info_to_distribution(distribution_info).distribution_df
        distribution_df.to_csv(csv_file_name)
    
    logger.info("Iterations: {:,}".format(sum(counts)))
    logger.info("Total Prob: {:.2f}".format(sum(probs)))
    logger.info("Mean Stock Price: {}".format(mean_mc_price))

    return distribution_info_to_distribution(distribution_info)


def float_to_histogram(move_input: 'float'):
    bs_distribution_original = float_to_bs_distribution(.3)
    #logger.info("Original: {:.2f}".format(bs_distribution_original.mean_move))
    mc_distribution = bs_distribution_original.mc_simulation(10**6)
    bs_distribution_created = mc_distribution_to_distribution(mc_distribution)
    #logger.info("Created: {.2f}".format(bs_distribution_created.mean_move))
    
if __name__ == '__main__':
    bs_distribution_original = float_to_bs_distribution(.3)
    print("Original: {:.2f}".format(bs_distribution_original.mean_move))
    mc_distribution = bs_distribution_original.mc_simulation(10**6)
    bs_distribution_created = mc_distribution_to_distribution(mc_distribution)
    print("Created: {:.2f}".format(bs_distribution_created.mean_move))

# IS IT BAD THAT DISTRIBUTION_MODULE IMPORT DISTRIBUTION TRANSFORMS WHICH IMPORTS DISTRIBUTIONMODULE?
