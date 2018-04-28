import pandas as pd
pd.options.mode.chained_assignment = None
from collections import namedtuple
from paul_resources import tprint
import copy
from decorators import my_time_decorator
from Distribution_Module_2 import Distribution
core_scenarios = pd.read_excel('CLVS_RiskScenarios.xlsx',
                         header = [0],
                         index_col = [0],
                         sheet_name = 'Core_Scenarios')

distribution_info = pd.read_excel('CLVS_RiskScenarios.xlsx',
                         header = [0],
                         index_col = [0,1],
                         sheet_name = 'Sub_States')
distribution_dff = distribution_info.reset_index().set_index('State')

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
@my_time_decorator
def run():
    nbix = Distribution_MultiIndex(distribution_info)
    #nbix.set_substate_prob(('Negative', 'CRL - No Hope'), .99)
    #nbix.set_substate_prob(('Positive', 'Clean Approval'), .99)
    nbix.set_prob_success(.90)
    print(nbix.distribution_df.round(3))
    print(nbix.positive_scenario_wgt_move, nbix.negative_scenario_wgt_move, nbix.prob_success)
    #nbix = nbix.distribution_df.reset_index().set_index('State')
    print(nbix)
    print(nbix.mean_move, nbix.straddle, nbix.average_move)
    nbix.get_histogram()

#run()
