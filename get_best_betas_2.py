import pandas as pd
import numpy as np
import math
import pickle
from functools import reduce
import itertools
from paul_resources import HealthcareSymbols, Symbols, tprint, PriceTable, daily_returns, setup_standard_logger, ETF_PriceTable, merge_dfs_horizontally, append_dfs_vertically, to_pickle_and_CSV, get_ETF_beta_to_SPY
from beta_class import ScrubParams, Beta
from decorators import my_time_decorator, empty_decorator
from collections import namedtuple
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from ETFs import indices as ETFs

# Standard Module Setup
NO_USE_TIMING_DECORATOR = False
if NO_USE_TIMING_DECORATOR:
    my_time_decorator = empty_decorator

logger = setup_standard_logger('Get_Best_Beta')


CutoffParams = namedtuple('CutoffParams', ['Stock_STD_Cutoff', 'Index_STD_Cutoff', 'Percentile_Cutoff'])

STOCK_STD_CUTOFF = 8.0
INDEX_STD_CUTOFF = 1.75
LOOKBACK_DEFAULT = 400
cutoff_params = CutoffParams(STOCK_STD_CUTOFF, INDEX_STD_CUTOFF, 95)

def get_stock_prices(stock, lookback):
    return PriceTable.loc[:, [stock]]

def get_daily_returns(stock, lookback):
    price_table = get_stock_prices(stock, lookback)
    return daily_returns(price_table)

def scrub_func(daily_return, cutoff, reverse_scrub = False):
    if not reverse_scrub:
        if abs(daily_return) < cutoff:
            return daily_return
        else:
            return np.NaN
    else:
        if abs(daily_return) > cutoff:
            return daily_return
        else:
            return np.NaN

def scrub_returns(returns, percentile_cutoff = 90, reverse_scrub = False):
    scrub_cutoff = np.nanpercentile(abs(returns), percentile_cutoff)
    returns = [scrub_func(daily_return, scrub_cutoff, reverse_scrub) for daily_return in returns.iloc[:, 0].tolist()]
    #returns.apply(scrub_func, cutoff=scrub_cutoff, reverse_scrub=reverse_scrub)
    return returns

def get_HV_from_returns(returns):
    return np.nanstd(returns)*math.sqrt(252)

def get_scrubbed_HV_for_stock(stock, lookback, percentile_cutoff = 90):
    daily_returns = get_daily_returns(stock, lookback)
    daily_returns_scrubbed = scrub_returns(daily_returns, percentile_cutoff)
    return get_HV_from_returns(daily_returns_scrubbed)

def get_cutoff(stock, lookback = LOOKBACK_DEFAULT, percentile_cutoff = 90, std_dev_cutoff = 2):
    HV = get_scrubbed_HV_for_stock(stock, lookback, percentile_cutoff)
    return HV / math.sqrt(252) * std_dev_cutoff

def get_stock_cutoff(stock, lookback = LOOKBACK_DEFAULT, percentile_cutoff = 90, std_dev_cutoff = STOCK_STD_CUTOFF):
    return get_cutoff(stock, lookback, percentile_cutoff, std_dev_cutoff)

def get_index_cutoff(index, lookback = LOOKBACK_DEFAULT, percentile_cutoff = 90, std_dev_cutoff = INDEX_STD_CUTOFF):
    return get_cutoff(index, lookback, percentile_cutoff, std_dev_cutoff)


def get_scrub_params_from_cutoff_params(stock, index, lookback, cutoff_params, percentile_cutoff):
    index_cutoff = get_index_cutoff(index, lookback, cutoff_params.Percentile_Cutoff, cutoff_params.Index_STD_Cutoff)
    
    stock_cutoff_raw = get_stock_cutoff(stock, lookback, cutoff_params.Percentile_Cutoff, cutoff_params.Stock_STD_Cutoff)
    stock_cutoff = max(index_cutoff*2.25, stock_cutoff_raw)
    return ScrubParams(stock_cutoff, index_cutoff, percentile_cutoff)

@my_time_decorator
def get_betas_multiple_stocks(stocks,
             index,
             lookback,
             cutoff_params = cutoff_params,
             percentile_cutoff = .85,
             to_file = False,
             file_name = 'default'):
    
    # Log
    #logger.info(stocks, index, lookback)
    
    # Calculate ScrubParams
    scrub_params_all =  [get_scrub_params_from_cutoff_params(stock, index, lookback, cutoff_params, percentile_cutoff) for stock in stocks]
    
    # Establish Table Info
    betas = [Beta(stock, index, lookback, scrub_params) for stock, scrub_params in zip(stocks, scrub_params_all)]
    beta_values= [beta.beta for beta in betas]
    corrs = [beta.corr for beta in betas]
    stock_cutoffs = [scrub_params.stock_cutoff for scrub_params in scrub_params_all]
    index_cutoffs = [scrub_params.index_cutoff for scrub_params in scrub_params_all]
    percentile_cutoffs = [percentile_cutoff for stock in range(len(stocks))]
    index_betas_to_SPY = [get_ETF_beta_to_SPY(index) for stock in range(len(stocks))]
    betas_to_SPY = [get_ETF_beta_to_SPY(index)*beta_values[i] for i in range(len(stocks))]

    # Create DataFrame
    table_info = list(zip(beta_values, corrs, stock_cutoffs, index_cutoffs, percentile_cutoffs, index_betas_to_SPY, betas_to_SPY))
    InfoLabels = ['Beta', 'Corr', 'Stock_Cutoff', 'Index_Cutoff', 'Percentile_Cutoff', 'Index_Beta_to_SPY', 'Beta_to_SPY']
    index_row = pd.Index(stocks, name = 'Stock')
    iterables_columns = [[index], InfoLabels]
    index_column = pd.MultiIndex.from_product(iterables_columns, names = ['Index', 'Beta_Info'])
    df = pd.DataFrame(table_info, index = index_row, columns = index_column)
    
    if to_file:
        to_pickle_and_CSV(df, file_name)
    
    return df


@my_time_decorator
def get_betas_for_multiple_stocks_and_indices(stocks,
                                              indices,
                                              lookback,
                                              cutoff_params,
                                              percentile_cutoff,
                                              to_file = False,
                                              file_name = 'default'):
    beta_info_by_index = [get_betas_multiple_stocks(stocks, index, lookback, cutoff_params, percentile_cutoff) for index in indices]
    return merge_dfs_horizontally(beta_info_by_index)

def get_best_betas(stocks,
                   indices,
                   lookback,
                   cutoff_params,
                   percentile_cutoff,
                   to_file = False,
                   file_name = 'default'):
    """Returns a DataFrame of best betas based on highest correlation for a set of symbols and ETFs."""

    df = get_betas_for_multiple_stocks_and_indices(stocks, indices, lookback, cutoff_params, percentile_cutoff)
    combinations = list(itertools.product(indices, ['Corr']))
    corr_df = df.loc[:, combinations].round(2)
    df['Best'] = corr_df.idxmax(axis=1)
    best = [i[0] for i in df.loc[:, 'Best'].tolist()]
    
    pairs = list(zip(stocks, best))
    info = []
    for stock, index in pairs:
        b = get_betas_multiple_stocks([stock], index, lookback, cutoff_params, percentile_cutoff)
        b.columns.set_levels(['Best'], level=0, inplace=True)
        b[('Best', 'Index')] = index
        info.append(b)
    
    df = append_dfs_vertically(info)
    a = df.loc[:, [('Best', 'Beta'), ('Best', 'Corr'), ('Best', 'Stock_Cutoff'), ('Best', 'Index_Cutoff')]]
    a = df.loc[:, [('Best', column) for column in ['Beta', 'Corr', 'Stock_Cutoff', 'Index_Cutoff', 'Index_Beta_to_SPY', 'Beta_to_SPY']]]
    b = df.loc[:, [('Best', 'Index')]]
    df = merge_dfs_horizontally([b, a]).sort_values([('Best', 'Index'), ('Best', 'Corr')], ascending=[True, False], inplace=False)
    print(df.round(2).to_string())
    
    if to_file:
        to_pickle_and_CSV(df, file_name)
    return df

lookback = 450
#stock_cutoff = .0875
#index_cutoff = .0125
percentile_cutoff = 1.00
cutoff_params = CutoffParams(2.75, 1.5, 95)


stocks = ['AAPL', 'GOOG', 'FB']
indices = ['SPY', 'QQQ']
stocks = ['AAPL', 'GOOG', 'FB', 'AMZN', 'ALNY', 'CRBP', 'NBIX', 'SRPT']
indices = ['SPY', 'QQQ', 'XLV', 'IBB', 'XBI']
stocks = HealthcareSymbols

#best_betas = get_best_betas(stocks, indices, lookback, cutoff_params, percentile_cutoff, to_file = True, file_name = 'Best_Betas')
#df = best_betas.round(2).sort_values([('Best', 'Corr')], ascending=False)
#print(df.to_string())

def calculate_ETF_betas_to_SPY():
    indices = ['SPY']
    stocks = [etf for etf in ETFs if etf != 'SPY']
    #stocks = ['XLV', 'XBI', 'XLI', 'XLF', 'XRT', 'XLP']
    stocks = HealthcareSymbols
    #cutoff_params = CutoffParams(10, .01, 100)
    #percentile_cutoff = 1.0
    betas = get_betas_multiple_stocks(stocks, indices[0], lookback, cutoff_params, percentile_cutoff, to_file=True, file_name = 'SPY_Betas_Scrubbed')
    df = betas.round(2).sort_values([(indices[0],'Corr')], ascending=False)
    print(df.to_string())
    return df

calculate_ETF_betas_to_SPY()


columns = ['Beta', 'Corr']
columns = ['Corr']
combinations = list(itertools.product(indices, columns))
#print(best_beta_results.loc[:, combinations].round(2))

#print(best_beta_results.loc[:, list(zip(indices, ['Beta' for i in indices]))].round(3))
#print(best_beta_results.loc[:, [('SPY', 'Beta'), ('IBB', 'Beta')]].round(3))
#print(best_beta_results.loc[:, [('SPY', 'Beta'), ('SPY', 'Corr')]].round(3))
#print(best_beta_results.loc[:, [('SPY', 'Beta'), ('SPY', 'Corr'), ('IBB', 'Beta'), ('IBB', 'Corr')]].round(3))

    
def get_multiple_indices(stocks, indices):
    for index in indices:
        df = get_both(stocks, index)





"""
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
"""
