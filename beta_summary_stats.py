import numpy as np
from statistics import mean
from collections import namedtuple
from paul_resources import get_ETF_beta_to_SPY, get_histogram_from_array
from paul_resources import Best_Betas, SPY_Betas_Raw, SPY_Betas_Scrubbed

etf = 'XLV'
beta = get_ETF_beta_to_SPY(etf)
print(beta, type(beta))

#---------------------------------------------------------------------------------------------------------#
BetaGrouping = namedtuple('BetaGrouping', ['Name', 'Values'])

best_betas = np.array(Best_Betas.loc[:, ('Best', 'Beta_to_SPY')].sort_index().tolist())
sorted_df= Best_Betas.loc[:, ('Best', 'Beta_to_SPY')].sort_index()
print(sorted_df)
SPY_betas_raw = np.array(SPY_Betas_Raw.loc[:, ('SPY', 'Beta')].sort_index().tolist())
SPY_betas_scrubbed = np.array(SPY_Betas_Scrubbed.loc[:, ('SPY', 'Beta')].sort_index().tolist())
#diffs = 
betas = SPY_betas_scrubbed


#get_histogram_from_array(betas, 20)
print(mean(best_betas), mean(SPY_betas_raw), mean(SPY_betas_scrubbed))

beta_groupings = [BetaGrouping('Best', best_betas), BetaGrouping('Raw', SPY_betas_raw), BetaGrouping('Scrubbed',SPY_betas_scrubbed)]
for grouping in beta_groupings:
    print(" * {} {} Mean: {:.2f}, STD: {:.2f}".format(grouping.Name, " "*(9 - len(grouping.Name)), mean(grouping.Values), np.nanstd(grouping.Values)))
    print(len(grouping.Values))
