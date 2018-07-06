# Standard Modules
import pandas as pd
import numpy as np
import math
import pickle
import itertools
from collections import namedtuple
#from multiprocessing import Pool

# Paul Modules
from beta_class import ScrubParams, Beta
from Beta_StepTwo import Beta_StepTwo

# Paul Utils
from utility.decorators import my_time_decorator, empty_decorator
from utility.general import tprint, setup_standard_logger, merge_dfs_horizontally, append_dfs_vertically, to_pickle_and_CSV
from utility.finance import daily_returns, get_ETF_beta_to_SPY, get_total_return, calculate_percentile, get_symbol_from_returns_df, get_stock_prices, get_daily_returns, scrub_func, calculate_HV_from_returns, scrub_returns

# Finance Data
from data.finance import PriceTable, ETF_PriceTable, Symbols, HealthcareSymbols, SP500Symbols
from data.ETFs import indices as ETFs

NO_USE_TIMING_DECORATOR = False
if NO_USE_TIMING_DECORATOR:
    my_time_decorator = empty_decorator

logger = setup_standard_logger('Get_Best_Beta')


SD_Cutoff_Params = namedtuple('SD_Cutoff_Params', ['Stock_SD_Cutoff', 'Index_SD_Cutoff', 'Stock_SD_Percentile_Cutoff', 'Index_SD_Percentile_Cutoff'])


STOCK_SD_PERCENTILE_CUTOFF = 90
STOCK_SD_CUTOFF = 8.0

INDEX_SD_PERCENTILE_CUTOFF = 100
INDEX_SD_CUTOFF = 1.75

LOOKBACK_DEFAULT = 400
sd_cutoff_params = SD_Cutoff_Params(STOCK_SD_CUTOFF, INDEX_SD_CUTOFF, STOCK_SD_PERCENTILE_CUTOFF, INDEX_SD_PERCENTILE_CUTOFF)


@my_time_decorator
def get_betas_multiple_stocks(stocks,
             index,
             lookback,
             sd_cutoff_params = sd_cutoff_params,
             percentile_cutoff = .85,
             to_file = False,
             file_name = 'default'):
    
    # Log
    #logger.info(stocks, index, lookback)
    
    # Calculate ScrubParams
    scrub_params_all =  [get_scrub_params_from_sd_cutoff_params(stock, index, lookback, sd_cutoff_params, percentile_cutoff) for stock in stocks]
    
    # Establish Table Info
    betas = [Beta_StepTwo(stock, index, lookback, scrub_params) for stock, scrub_params in zip(stocks, scrub_params_all)]
    beta_values= [beta.beta for beta in betas]
    corrs = [beta.corr for beta in betas]
    stock_cutoffs = [scrub_params.stock_cutoff for scrub_params in scrub_params_all]
    index_cutoffs = [scrub_params.index_cutoff for scrub_params in scrub_params_all]
    percentile_cutoffs = [percentile_cutoff for stock in range(len(stocks))]
    index_betas_to_SPY = [get_ETF_beta_to_SPY(index) for stock in range(len(stocks))]
    betas_to_SPY = [get_ETF_beta_to_SPY(index)*beta_values[i] for i in range(len(stocks))]
    returns = [get_total_return(stock, lookback) for stock in stocks]
    index_returns = [get_total_return(index, lookback) for stock in stocks]
    idio_returns = [(1+returns[i])/(1+index_returns[i]*beta_values[i]) - 1 for i in range(len(stocks))]
    percent_days_in_calc = [beta.percent_days_in_calculation for beta in betas]
    # Create DataFrame
    table_info = list(zip(beta_values, corrs, stock_cutoffs, index_cutoffs, percentile_cutoffs, index_betas_to_SPY, betas_to_SPY, returns, index_returns, idio_returns, percent_days_in_calc))
    InfoLabels = ['Beta', 'Corr', 'Stock_Cutoff', 'Index_Cutoff', 'Percentile_Cutoff', 'Index_Beta_to_SPY', 'Beta_to_SPY', 'Return', 'Index_Return', 'Idio_Return', 'Percent_Days']
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
                                              sd_cutoff_params,
                                              percentile_cutoff,
                                              to_file = False,
                                              file_name = 'default'):
    beta_info_by_index = [get_betas_multiple_stocks(stocks, index, lookback, sd_cutoff_params, percentile_cutoff) for index in indices]
    return merge_dfs_horizontally(beta_info_by_index)

def get_best_betas(stocks,
                   indices,
                   lookback,
                   sd_cutoff_params,
                   percentile_cutoff,
                   to_file = False,
                   file_name = 'default'):
    """Returns a DataFrame of best betas based on highest correlation for a set of symbols and ETFs."""

    df = get_betas_for_multiple_stocks_and_indices(stocks, indices, lookback, sd_cutoff_params, percentile_cutoff)
    combinations = list(itertools.product(indices, ['Corr']))
    corr_df = df.loc[:, combinations].round(2)
    df['Best'] = corr_df.idxmax(axis=1)
    best = [i[0] for i in df.loc[:, 'Best'].tolist()]
    
    pairs = list(zip(stocks, best))
    info = []
    for stock, index in pairs:
        b = get_betas_multiple_stocks([stock], index, lookback, sd_cutoff_params, percentile_cutoff)
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
sd_cutoff_params = SD_Cutoff_Params(2.75, 1.5, 95, 100)


stocks = ['AAPL', 'GOOG', 'FB']
indices = ['SPY', 'QQQ']
stocks = ['AAPL', 'GOOG', 'FB', 'AMZN', 'ALNY', 'CRBP', 'NBIX', 'SRPT']
indices = ['SPY', 'QQQ', 'XLV', 'IBB', 'XBI']
stocks = HealthcareSymbols[0:5]
stocks = [i for i in HealthcareSymbols if i in SP500Symbols]
stocks = [i for i in stocks if i not in {'AAAP', 'ABMD'}]
stocks = stocks[0:5]
print(stocks)
best_betas = get_best_betas(stocks, indices, lookback, sd_cutoff_params, percentile_cutoff, to_file = False, file_name = 'Best_Betas')
#df = best_betas.round(2).sort_values([('Best', 'Corr')], ascending=False)
#print(df.to_string())

#stocks = [etf for etf in ETFs if etf != 'SPY']
#stocks = ['XLV', 'XBI', 'XLI', 'XLF', 'XRT', 'XLP']
#stocks = HealthcareSymbols[0:25]
#stocks = SP500Symbols

def calculate_betas_to_SPY(stocks):
    indices = ['SPY']
    #sd_cutoff_params = SD_Cutoff_Params(3, 1.5, 90, 97.5)
    sd_cutoff_params = SD_Cutoff_Params(3, 1.0, 90, 97.5)
    percentile_cutoff = .85
    betas = get_betas_multiple_stocks(stocks, indices[0], lookback, sd_cutoff_params, percentile_cutoff, to_file=True, file_name = 'SPY_Betas_Scrubbed')
    df = betas.round(3).sort_values([(indices[0],'Corr')], ascending=False)
    print(df.to_string())
    return df


def calculate_raw_betas_to_SPY(stocks):
    sd_cutoff_params = SD_Cutoff_Params(15, .01, 100, 100)
    percentile_cutoff = 1.0
    betas = get_betas_multiple_stocks(stocks, indices[0], lookback, sd_cutoff_params, percentile_cutoff, to_file=True, file_name = 'SPY_Betas_Raw')
    df = betas.round(3).sort_values([(indices[0],'Corr')], ascending=False)
    print(df.to_string())

#calculate_betas_to_SPY(stocks)
#calculate_raw_betas_to_SPY(stocks)


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
