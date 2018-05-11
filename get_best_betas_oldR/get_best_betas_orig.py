import pandas as pd
from paul_resources import HealthcareSymbols, tprint, PriceTable
from beta_class_7 import ScrubParams, Beta
from decorators import my_time_decorator
import pickle

lookback = 400
stock_cutoff = .0875
index_cutoff = .0125
percentile_cutoff = .85
stocks = HealthcareSymbols[0:1000]

@my_time_decorator
def get_best_betas():
    best_indices = []
    best_betas = []
    best_corrs = []

    for stock in stocks:
        indices = ['SPY', 'XLV', 'IBB', 'XBI']
        index_cutoffs = {'SPY': .015, 'XLV': .015, 'IBB': .015, 'XBI': .0225}
        outcomes = []
        for index in indices:
            index_cutoff = index_cutoffs[index]
            scrub_params = ScrubParams(stock_cutoff, index_cutoff, percentile_cutoff)
            beta = Beta(stock, index, lookback, scrub_params)
            outcomes.append((index, beta.beta, beta.corr))
        max_corr = max([i[2] for i in outcomes])
        best_fit = [i for i in outcomes if i[2] == max_corr][0]
        best_indices.append(best_fit[0])
        best_betas.append(best_fit[1])
        best_corrs.append(best_fit[2])

    info = {'Stock': stocks,
            'Index': best_indices,
            'Beta': best_betas,
            'Corr': best_corrs}

    return pd.DataFrame(info).set_index('Stock').loc[:, ['Index', 'Beta', 'Corr']]

best_betas = get_best_betas().sort_values(['Index', 'Beta'], ascending=[True, False])

print(best_betas.round(2).to_string())

best_betas.to_csv('best_betas.csv')

pickle_file = open('best_betas.pkl', 'wb')
pickle.dump(best_betas, pickle_file, pickle.HIGHEST_PROTOCOL)
pickle_file.close()
