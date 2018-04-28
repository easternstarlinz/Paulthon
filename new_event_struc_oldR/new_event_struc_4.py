import pandas as pd
from paul_resources import tprint

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
crl = distribution_info.loc['CRL']
crl.name = 'CRL'
crl_substate = crl.loc['CRL - No Hope']
crl_substate.loc['Price'] = 1000

substates = list(crl.iterrows())
for substate in substates:
    distribution_info.loc[('CRL', substate[0])] = substate[1]

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


def change_core_scenario(distribution_df, core_scenario):
    states = list(core_scenario.iterrows())
    for state in states:
        distribution_df.loc[(core_scenario.name, state[0])] = state[1]
    return distribution_df


crl = change_core_scenario_relative_prob(crl, 'CRL - Minor Delay', .95)
print("BOBBY", crl)

distribution_info_new = change_core_scenario(distribution_info, crl)
print(distribution_info_new)

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
