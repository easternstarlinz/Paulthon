import pandas as pd

core_scenarios = pd.read_excel('CLVS_RiskScenarios.xlsx',
                         header = [0],
                         index_col = [0],
                         sheet_name = 'Core_Scenarios')
#TimingMappings = TimingMappings.reset_index().set_index('level_1').loc[:, ['Start', 'End']]

distribution_df = pd.read_excel('CLVS_RiskScenarios.xlsx',
                         header = [0],
                         index_col = [0,1],
                         sheet_name = 'Sub_States')

distribution_df = distribution_df.reset_index().set_index('State')
print(distribution_df)
"""
#states = [i[1] for i in sub_states.index.values.tolist()]
#probs = sub_states.loc[:, 'Prob']
#pct_moves = sub_states.loc[:, 'Pct_Move']
#relative_prices = probs + 1

distribution_info = {'State': states ,
                     'Prob': probs,
                     'Pct_Move': pct_moves,
                     'Relative_Price': relative_prices}

#distribution_df = pd.DataFrame(distribution_info).set_index('State').loc[:, ['Prob', 'Pct_Move', 'Relative_Price']]
"""

# Create a Scenario where the Core Probability of Success is .90.
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

reset_core_prob_success(distribution_df, .99)




