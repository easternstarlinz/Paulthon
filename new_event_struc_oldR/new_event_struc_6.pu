import pandas as pd
from collections import namedtuple
from paul_resources import tprint
import copy

core_scenarios = pd.read_excel('CLVS_RiskScenarios.xlsx',
                         header = [0],
                         index_col = [0],
                         sheet_name = 'Core_Scenarios')

distribution_info = pd.read_excel('CLVS_RiskScenarios.xlsx',
                         header = [0],
                         index_col = [0,1],
                         sheet_name = 'Sub_States')
#print(distribution_info)
#distribution_dff = distribution_info.reset_index().set_index('State')
#print(distribution_dff)

# Create a Scenario where the Core Probability of Success is .90.

#ResetParams = namedtuple('ResetParams', ['Core_Scenario', 'New_Params'])
#reset_params = ResetParams('CRL', crl_params)

#change_core_scenario(distribution_df, 'hi')
def change_core_scenario_relative_prob(core_scenario, state, new_prob):
    """Specify the core_scenario, and state that you want to change with the new relative probability"""
    # Calculate New Probabilities
    states = core_scenario.index.tolist()
    other_states = [i for i in states if i != state]
    
    old_prob = core_scenario.loc[state, 'Relative_Prob']
    old_total_prob_other_states = 1 - old_prob
    new_total_prob_other_states = 1 - new_prob
    
    # Set New Probabilities
    core_scenario.loc[state, 'Relative_Prob'] = new_prob
    for state in other_states:
        core_scenario.loc[state, 'Relative_Prob'] *= new_total_prob_other_states / old_total_prob_other_states
    return core_scenario


#def change_core_scenario(distribution_df, core_scenario):
#    states = list(core_scenario.iterrows())
#    for state in states:
#        distribution_df.loc[(core_scenario.name, state[0])] = state[1]
#    print("BARBARA", distribution_df.index.levels[0].tolist())
   
#    weighted_moves = []
#    for core_scen in distribution_df.index.levels[0].tolist():
#            probs = distribution_df.loc[core_scen].loc[:, 'Relative_Prob'].values.tolist()
#            pct_moves = distribution_df.loc[core_scen].loc[:, 'Pct_Move'].values.tolist()
#            weighted_move = sum([prob*pct_move for prob, pct in zip(probs, pct_moves)]
#            weighted_moves.append(weighted_move)
#    up_move = weighted_moves[0]
#    down_move = weighted_moves[1]
#    prob_success = -down_move / (up_move - down_move)
#    return distribution_df

class Distribution_MultiIndex(object):
    def __init__(self, df):
        self.input_df = df
        self.positive_scenario = df.loc[['Positive']]
        self.negative_scenario = df.loc[['Negative']]
        self.new = self.positive_scenario.append(self.negative_scenario)
        self.core_scenarios = df.index.levels[0].tolist()

    @property
    def core_scenario_dfs(self):
        return [self.input_df.loc[i] for i in self.core_scenarios]
    
   # @property
   # def positive_scenario(self):
   #     return copy.deepcopy(self.df.loc['Positive'])

   # @property
   # def negative_scenario(self):
   #     return self.df.loc['Negative']

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
        unchanged_states = [i for i in all_states if i != state]
    
        old_relative_prob = self.positive_scenario.loc[state, 'Relative_Prob']
        old_total_prob_other_states = 1 - old_relative_prob
        new_total_prob_other_states = 1 - new_relative_prob
    
        # Set New Probabilities
        self.positive_scenario.loc[state, 'Relative_Prob'] = new_relative_prob
        print(self.positive_scenario)
        for state in unchanged_states:
            self.positive_scenario.loc[state, 'Relative_Prob'] *= new_total_prob_other_states / old_total_prob_other_states
        return self.positive_scenario

    @property
    def df(self):
        self.df

nbix = Distribution_MultiIndex(distribution_info)
print("HELLO JANEEEEEEEEEEEEEEEEEE")
print(nbix.core_scenarios, nbix.core_scenario_dfs)
print(nbix.positive_scenario, nbix.negative_scenario)
#print(nbix.positive_scenario_wgt_move, nbix.negative_scenario_wgt_move, nbix.prob_success)
#print(nbix.set_positive_scenario_substate_prob('Approved', .99))
print(nbix.positive_scenario_wgt_move, nbix.prob_success)
print(nbix.positive_scenario)
print(nbix.negative_scenario)
print(nbix.new)
"""
def change_distribution(distribution_info, param):
    core_scenario = distribution_info.loc[param.Core_Scenario]
    core_scenario.name = param.Core_Scenario

    core_scenario = change_core_scenario_relative_prob(core_scenario, param.State, param.New_Prob)
    return change_core_scenario(distribution_info, core_scenario)

ResetParams = namedtuple('ResetParams', ['Core_Scenario', 'State', 'New_Prob'])
param = ResetParams('CRL', 'CRL - Minor Delay', .01)
new = change_distribution(distribution_info, param)
print(new)

ResetCoreScenario = namedtuple('ResetCoreScenario', ['Core_Scenario', 'New_Prob'])

param2 = namedtuple('Elagolix_Approved', .8)
def reset_core_scenario_prob(distribution_df, param):
    # Set the New Probabilities
    old_prob = distribution_df.loc[state, 'Prob']
    old_total_prob_other_states = 1 - old_prob
    new_total_prob_other_states = 1 - new_prob
    states = distribution_df.index.tolist()
    other_states = [i for i in states if i != state]
    
    # Set new probabilities
    distribution_df.loc[state, 'Prob'] = new_prob
    for state in other_states:
        distribution_df.loc[state, 'Prob'] *= new_total_prob_other_states / old_total_prob_other_states

    center_shift = sum([state.Prob*state.Pct_Move for state in distribution_df.itertuples()])
    
    for state in states:
        distribution_df.loc[state, 'Pct_Move'] += -center_shift
    new_valuation = sum([state.Prob*state.Pct_Move for state in distribution_df.itertuples()])


    print(new_valuation)
    print(distribution_df.round(3))

def reset_scenario_prob(distribution_df, state, new_prob):
    # Set the New Probabilities
    old_prob = distribution_df.loc[state, 'Prob']
    old_total_prob_other_states = 1 - old_prob
    new_total_prob_other_states = 1 - new_prob
    states = distribution_df.index.tolist()
    other_states = [i for i in states if i != state]
    
    # Set new probabilities
    distribution_df.loc[state, 'Prob'] = new_prob
    for state in other_states:
        distribution_df.loc[state, 'Prob'] *= new_total_prob_other_states / old_total_prob_other_states

    center_shift = sum([state.Prob*state.Pct_Move for state in distribution_df.itertuples()])
    
    for state in states:
        distribution_df.loc[state, 'Pct_Move'] += -center_shift
    new_valuation = sum([state.Prob*state.Pct_Move for state in distribution_df.itertuples()])


    print(new_valuation)
    print(distribution_df.round(3))
#print(distribution_df.round(3)) 
#reset_scenario_prob(distribution_df, 'Clean Approval', .9)
"""











"""
# Create a Scenario where the Core Probability of Success is .90.
reset_params = {'Elagolix Approved': .95, 'CRL': 'Clean Approval': .95}
reset_params = [{'Core_Scenario': ('Elagolix Approved', .95)}
                , 'State': ('Clean Approval', .95)}]
ResetParams = namedtuple('ResetParams', ['Core_Scenario', 'Core_Scenario_Value', 'Sub_State', 'Sub_State_Value'])

ResetParams = namedtuple('ResetParams', ['Core_Scenario', 'State', 'Relative_Prob'])
reset_params = ResetParams('Elagolix Approved', 'Clean Approval', .95)

def reset_scenarios(distribution_df, reset_params):
    core_scenario_states = [state for state in distribution_df.itertuples(() if state.Core_Scenario == reset_params.Core_Scenario]
    core_scenario_other_states = [state for state in core_scenario_states ifstate != reset_params.State]

    original_relative_prob = distribution_df.loc[reset_params.State, 'Relative_Prob']
    core_scenario_other_states_total_prob_original = 1 - original_relative_prob
    core_scenario_other_states_total_prob_new = 1 - reset_params.Relative_Prob
    core_scenario_other_relative_probs_mult = core_scenario_other_states_total_prob_new / core_scenario_other_states_total_prob_new

    # Set new Relative Probabilities
    distribution_df.loc[reset_params.State, 'Relative_Prob'] = reset_params.Relative_Prob
    for state in other_states:
        distribution_df.loc[state, 'Prob'] *= new_total_prob_other_states / old_total_prob_other_states


    # Set the New Relative Probabilities
    old_prob = distribution_df.loc[state, 'Prob']
    old_total_prob_other_states = 1 - old_prob
    new_total_prob_other_states = 1 - new_prob
    states = distribution_df.index.tolist()
    other_states = [i for i in states if i != state]
    
    # Set new probabilities
    distribution_df.loc[state, 'Prob'] = new_prob
    for state in other_states:
        distribution_df.loc[state, 'Prob'] *= new_total_prob_other_states / old_total_prob_other_states

    center_shift = sum([state.Prob*state.Pct_Move for state in distribution_df.itertuples()])
    
    for state in states:
        distribution_df.loc[state, 'Pct_Move'] += -center_shift
    new_valuation = sum([state.Prob*state.Pct_Move for state in distribution_df.itertuples()])


    print(new_valuation)
    print(distribution_df.round(3))
print(distribution_df.round(3)) 
reset_scenario_prob(distribution_df, 'Clean Approval', .9)

"""

"""

# Create a Scenario where the Core Probability of Success is .90.
def reset_scenario_prob(distribution_df, state, new_prob):
    # Set the New Probabilities
    old_prob = distribution_df.loc[state, 'Prob']
    old_total_prob_other_states = 1 - old_prob
    new_total_prob_other_states = 1 - new_prob
    states = distribution_df.index.tolist()
    other_states = [i for i in states if i != state]
    
    # Set new probabilities
    distribution_df.loc[state, 'Prob'] = new_prob
    for state in other_states:
        distribution_df.loc[state, 'Prob'] *= new_total_prob_other_states / old_total_prob_other_states

    center_shift = sum([state.Prob*state.Pct_Move for state in distribution_df.itertuples()])
    
    for state in states:
        distribution_df.loc[state, 'Pct_Move'] += -center_shift
    new_valuation = sum([state.Prob*state.Pct_Move for state in distribution_df.itertuples()])


    print(new_valuation)
    print(distribution_df.round(3))
print(distribution_df.round(3)) 
reset_scenario_prob(distribution_df, 'Clean Approval', .9)


def reset_core_prob_success(distribution_df, new_core_prob_success):
    core_up_pct_move = core_scenarios.loc['Elagolix Approved', 'Pct_Move']
    core_down_pct_move = core_scenarios.loc['CRL', 'Pct_Move']
    valuation_band = core_up_pct_move - core_down_pct_move
    print(core_up_pct_move, core_down_pct_move, valuation_band)

    core_prob_success = core_scenarios.loc['Elagolix Approved', 'Prob']

    new_core_up_pct_move = valuation_band*(1 - new_core_prob_success)
    new_core_down_pct_move = new_core_up_pct_move - valuation_band
    up_pct_move_diff = new_core_up_pct_move - core_up_pct_move
    down_pct_move_diff = new_core_down_pct_move - core_down_pct_move


    distribution_df['Pct_Move'] += up_pct_move_diff*(distribution_df['Core_Scenario']== 'Elagolix Approved') + down_pct_move_diff*(distribution_df['Core_Scenario'] == 'CRL')
    distribution_df['Prob'] = distribution_df['Relative_Prob']*(new_core_prob_success*(distribution_df['Core_Scenario']== 'Elagolix Approved') + (1 - new_core_prob_success)*(distribution_df['Core_Scenario'] == 'CRL'))
    #distribution_df['Pct_Move'] = 3*(distribution_df['Core_Scenario']== 'Elagolix Approved') + 30*(distribution_df['Core_Scenario'] == 'CRL')
    
    print(distribution_df.round(3))

#reset_core_prob_success(distribution_df, .99)



"""
