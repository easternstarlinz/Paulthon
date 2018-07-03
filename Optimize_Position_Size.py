# Standard Packages
import pandas as pd
import numpy as np
import datetime as dt
from statistics import mean

# Paul Packages
from Stock_Module import Stock
from Option_Module import get_time_to_expiry
from Event_Module import IdiosyncraticVol
from Distribution_Module import Distribution, mc_distribution_to_distribution
from CreateMC import get_total_mc_distribution_from_events_vanilla
from Optimization_Formulas import find_maximum, kelly_criterion

# Paul General Formulas
from utility.graphing import get_histogram_from_array

# Declare Expiry
expiry = dt.date(2019, 5, 15)

# Declare Events
event = Stock.elagolix
vol = IdiosyncraticVol('NBIX', .20)

# Create MC_Distribution and distribution_df for the Combined Event
df = event.event_input_distribution_df
mc_dist = get_total_mc_distribution_from_events_vanilla([event, vol], expiry=expiry, mc_iterations=10**5)
get_histogram_from_array(mc_dist, bins = 2*10**1 +1, title='Expected GE Distribution')

mc_distribution_to_distribution(mc_dist, bins=5*10**1+1, to_file=True, file_name='Elagolix_Dist')
combined_dist = Distribution(pd.read_csv('Elagolix_Dist.csv'))
df = combined_dist.distribution_df
#print(df.to_string())

# Source Probs, Pct_Moves, Max_Loss for the Combined Event
probs = df.loc[:, 'Prob'].tolist()
pct_moves = df.loc[:, 'Pct_Move'].tolist()
max_loss = min(pct_moves)

event_pct_moves = event.event_input_distribution_df.loc[:, 'Pct_Move'].tolist()
print(event_pct_moves)
max_loss_event_only = min(event_pct_moves)
#max_loss = -1
#pct_moves = [pct_move/-max_loss for pct_move in pct_moves]

#-----------------------------Portfolio Parameters-------------------------------#
capital_allocation = 100*10**6
portfolio_max_drawdown_percent = .05
portfolio_max_drawdown = portfolio_max_drawdown_percent*capital_allocation

time_to_expiry = get_time_to_expiry(expiry)
Xguess = min(max(.1, 4-4*5*time_to_expiry), .9)
Xguess = .5
increment = .05
print('Xguess: {:.2f}'.format(Xguess))
optimal_size = find_maximum(f=kelly_criterion,
                            Xguess=Xguess,
                            increment=increment,
                            print_guesses=True,
                            probs=probs,
                            pct_moves=pct_moves)

#capital_deployed = maximum*(1/-max_loss)
capital_deployed = optimal_size
max_drawdown = max_loss*capital_deployed
max_drawdown_event_only = max_loss_event_only*capital_deployed

optimal_size_dollars = optimal_size*portfolio_max_drawdown
optimal_size_percent_of_capital = optimal_size_dollars / capital_allocation
max_drawdown_dollars = max_loss*optimal_size_dollars
max_drawdown_event_only_dollars = max_loss_event_only*optimal_size_dollars
max_drawdown_percent_of_capital = max_drawdown_dollars / capital_allocation
max_drawdown_percent_of_portfolio_max_drawdown = max_drawdown_dollars / portfolio_max_drawdown
max_drawdown_event_only_percent_of_portfolio_max_drawdown = max_drawdown_event_only_dollars / portfolio_max_drawdown

#----------------Print Statements------------------------------------#
print('\n---------------MC Distribution Summary Statistics---------------')
print('MC Iterations: {:,.0f}, Mean: {:.2f}'.format(len(mc_dist), np.mean(mc_dist)))
print("Combined Dist. Average Move: {:.2f}".format(combined_dist.average_move))
print("Combined Dist. Mean Sqrt Move: {:.2f}".format(combined_dist.mean_move))

print('\n---------------Optimal Sizing; Absolute Basis-----------------')
print('Optimal Size (% of Risk Dollars): {:.2f}'.format(optimal_size))
print('Capital_Deployed (% of Risk Dollars): {:.2f}'.format(capital_deployed))
print('Max Drawdown (% of Risk Dollars): {:.2f}'.format(max_drawdown))

print('\n--------------Drawdown Expectations as % of Capital / Risk---------')
print('Max Exp. Drawdown (% of Capital): {:.2f}%'.format(max_drawdown_percent_of_capital*100))
print('Max Exp. Drawdown (% of Portfolio Max Drawdown): {:.2f}%'.format(max_drawdown_percent_of_portfolio_max_drawdown*100))
print('Max Exp. Drawdown - Event Only (% of Portfolio Max Drawdown): {:.2f}%'.format(max_drawdown_event_only_percent_of_portfolio_max_drawdown*100))

print('\n--------------Sizing ($) for $100mm Portoflio; 5.0% Drawdown Limit-------')
print('Optimal Size ($): ${:,.0f}'.format(optimal_size_dollars))
print('Max Expcted Loss ($): ${:,.0f}'.format(max_drawdown_dollars))
print('% of Capital Deployed: {:.2f}%'.format(optimal_size_percent_of_capital*100))

if __name__ == '__main__':
    pass
