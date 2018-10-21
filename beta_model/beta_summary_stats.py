import numpy as np
from statistics import mean
from collections import namedtuple
from paul_resources import get_ETF_beta_to_SPY, get_histogram_from_array, merge_dfs_horizontally
from paul_resources import Best_Betas, SPY_Betas_Raw, SPY_Betas_Scrubbed
import matplotlib.pyplot as plt


etf = 'XLV'
beta = get_ETF_beta_to_SPY(etf)
#print(beta_value, type(beta_value))

#---------------------------------------------------------------------------------------------------------#
print(SPY_Betas_Scrubbed.round(3).sort_values([('SPY', 'Corr')], ascending=False).to_string())
#print(SPY_Betas_Raw.round(3).sort_values([('SPY', 'Corr')], ascending=False).to_string())

def compare_raw_v_scrubbed():
    raw = SPY_Betas_Raw
    scrubbed = SPY_Betas_Scrubbed
    raw = raw[raw[('SPY', 'Return')] > .40]
    scrubbed = scrubbed[scrubbed[('SPY', 'Return')] > .40]

    idio_returns = np.array(scrubbed.loc[:, ('SPY', 'Idio_Return')].sort_index().tolist())
    total_returns = np.array(scrubbed.loc[:, ('SPY', 'Return')].sort_index().tolist())
    print("Total Returns: {:.2f}, Idio Returns: {:.2f}".format(mean(total_returns), mean(idio_returns)))

    SPY_betas_raw = np.array(raw.loc[:, ('SPY', 'Beta')].sort_index().tolist())
    SPY_betas_scrubbed = np.array(scrubbed.loc[:, ('SPY', 'Beta')].sort_index().tolist())
    diffs = SPY_betas_scrubbed - SPY_betas_raw
    print(mean(SPY_betas_raw), mean(SPY_betas_scrubbed), mean(diffs))

    raw = raw.loc[:, [('SPY', 'Corr'), ('SPY', 'Beta')]]
    scrubbed = scrubbed.loc[:, [('SPY', 'Corr'), ('SPY', 'Beta')]]
    
    
    combined = merge_dfs_horizontally([raw, scrubbed])
    combined['Corr_Diff'] = scrubbed.loc[:, [('SPY', 'Corr')]] - raw.loc[:, [('SPY', 'Corr')]]
    combined['Beta_Diff'] = scrubbed.loc[:, [('SPY', 'Beta')]] - raw.loc[:, [('SPY', 'Beta')]]
    print(combined.sort_values([('SPY_y', 'Corr')], ascending=False).round(3).to_string())
    print(combined.shape)
    return combined

df = compare_raw_v_scrubbed()

BetaGrouping = namedtuple('BetaGrouping', ['Name', 'Values'])

best_betas = np.array(Best_Betas.loc[:, ('Best', 'Beta_to_SPY')].sort_index().tolist())
sorted_df= Best_Betas.loc[:, ('Best', 'Beta_to_SPY')].sort_index()

SPY_betas_raw = np.array(SPY_Betas_Raw.loc[:, ('SPY', 'Beta')].sort_index().tolist())
SPY_betas_scrubbed = np.array(SPY_Betas_Scrubbed.loc[:, ('SPY', 'Beta')].sort_index().tolist())
diffs = SPY_betas_scrubbed - SPY_betas_raw
idio_returns = np.array(SPY_Betas_Scrubbed.loc[:, ('SPY', 'Idio_Return')].sort_index().tolist())
total_returns = np.array(SPY_Betas_Scrubbed.loc[:, ('SPY', 'Return')].sort_index().tolist())

#plt.scatter(SPY_betas_scrubbed, idio_returns, label = 'Betas v. Idio Returns')
#plt.scatter(SPY_betas_scrubbed, total_returns, label = 'Betas v. Total Returns')
#plt.scatter(total_returns, idio_returns, label = 'Total Returns v. Idio Returns')
plt.scatter(SPY_betas_raw, diffs, label = 'Raw Betas v. Diffs')
plt.xlim(0, 2.25)
plt.ylim(-.5, .5)
plt.show()

betas = SPY_betas_scrubbed

#get_histogram_from_array(SPY_betas_raw, 20, title = 'Raw SPY Betas')
#get_histogram_from_array(SPY_betas_scrubbed, 20, title = 'Scrubbed SPY Betas')
get_histogram_from_array(diffs, 20, title = 'Diffs')
#get_histogram_from_array(diffs, 20, title = 'Diffs')
print(mean(best_betas), mean(SPY_betas_raw), mean(SPY_betas_scrubbed))

beta_groupings = [BetaGrouping('Best', best_betas), BetaGrouping('Raw', SPY_betas_raw), BetaGrouping('Scrubbed',SPY_betas_scrubbed)]
for grouping in beta_groupings:
    print(" * {} {} Mean: {:.2f}, STD: {:.2f}".format(grouping.Name, " "*(9 - len(grouping.Name)), mean(grouping.Values), np.nanstd(grouping.Values)))
    #print(len(grouping.Values))


print("Total Returns: {:.2f}, Idio Returns: {:.2f}".format(mean(total_returns), mean(idio_returns)))

