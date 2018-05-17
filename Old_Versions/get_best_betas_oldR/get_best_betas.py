import pandas as pd
import numpy as np
import math
from paul_resources import HealthcareSymbols, tprint, PriceTable, daily_returns, setup_standard_logger
from beta_class import ScrubParams, Beta
from decorators import my_time_decorator, empty_decorator
import pickle
from collections import namedtuple
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

# Standard Module Setup
NO_USE_TIMING_DECORATOR = True
if NO_USE_TIMING_DECORATOR:
    my_time_decorator = empty_decorator

logger = setup_standard_logger('Get_Best_Beta')

lookback = 400
stock_cutoff = .0875
index_cutoff = .0125
percentile_cutoff = .85
stocks = HealthcareSymbols[0:1000]

STOCK_STD_CUTOFF = 4.0
INDEX_STD_CUTOFF = 1.75

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

def get_cutoff(stock, lookback = 400, percentile_cutoff = 90, std_dev_cutoff = 2):
    HV = get_scrubbed_HV_for_stock(stock, lookback, percentile_cutoff)
    return HV / math.sqrt(252) * std_dev_cutoff

def get_stock_cutoff(stock, lookback = 400, percentile_cutoff = 90, std_dev_cutoff = STOCK_STD_CUTOFF):
    return get_cutoff(stock, lookback, percentile_cutoff, std_dev_cutoff)

def get_index_cutoff(index, lookback = 400, percentile_cutoff = 90, std_dev_cutoff = INDEX_STD_CUTOFF):
    return get_cutoff(index, lookback, percentile_cutoff, std_dev_cutoff)

Option = namedtuple('Option', ['Option_Type', 'Strike', 'Expiry'])

CutoffParams = namedtuple('CutoffParams', ['Stock_STD_Cutoff', 'Index_STD_Cutoff', 'Percentile_Cutoff'])

cutoff_params = CutoffParams(STOCK_STD_CUTOFF, INDEX_STD_CUTOFF, 95)

def get_scrub_params_from_cutoff_params(stock, index, lookback, cutoff_params, percentile_cutoff):
    stock_cutoff = get_stock_cutoff(stock, lookback, cutoff_params.Percentile_Cutoff, cutoff_params.Stock_STD_Cutoff)
    index_cutoff = get_index_cutoff(index, lookback, cutoff_params.Percentile_Cutoff, cutoff_params.Index_STD_Cutoff)
    return ScrubParams(stock_cutoff, index_cutoff, percentile_cutoff)

@my_time_decorator
def get_beta(stock,
             index,
             lookback,
             cutoff_params = cutoff_params,
             percentile_cutoff = .80):
    scrub_params =  get_scrub_params_from_cutoff_params(stock, index, lookback, cutoff_params, percentile_cutoff) 
    beta = Beta(stock, index, lookback, scrub_params)
    beta_value = beta.beta
    corr = beta.corr
    
    #logger.info(stock, index, lookback)
    #logger.info('Symbol: {}, Beta: {:.2f}, Corr: {:.2f}'.format(stock, beta_value, corr))
    return Beta(stock, index, lookback, scrub_params).beta

@my_time_decorator
def get_corr(stock,
             index,
             lookback,
             cutoff_params = cutoff_params,
             percentile_cutoff = .80):
    scrub_params =  get_scrub_params_from_cutoff_params(stock, index, lookback, cutoff_params, percentile_cutoff) 
    beta = Beta(stock, index, lookback, scrub_params)
    beta_value = beta.beta
    corr = beta.corr
    return Beta(stock, index, lookback, scrub_params).corr


def get_betas(stocks, index, lookback):
    return [get_beta(stock, index, lookback) for stock in stocks]

def get_corrs(stocks, index, lookback):
    return [get_corr(stock, index, lookback) for stock in stocks]

@my_time_decorator
def get_betas_df(stocks, betas, corrs, index):
    content_label = index
    index_r = pd.Index(stocks, name = 'Strike')
    iterables_c = [[index], ['Beta']]
    index_c = pd.MultiIndex.from_product(iterables_c, names = [index, 'Beta_Info'])
    df = pd.DataFrame(betas, index = index_r, columns = index_c)
    return df
    return df[df[(expiry, content_label)] > .0025].round(4)

@my_time_decorator
def get_betas_df(stocks, betas, corrs, index):
    beta_info = list(zip(betas, corrs))
    content_label = index
    index_r = pd.Index(stocks, name = 'Strike')
    iterables_c = [[index], ['Beta', 'Corr']]
    index_c = pd.MultiIndex.from_product(iterables_c, names = [index, 'Beta_Info'])
    df = pd.DataFrame(beta_info, index = index_r, columns = index_c)
    return df
    return df[df[(expiry, content_label)] > .0025].round(4)

@my_time_decorator
def get_corrs_df(stocks, betas, corrs, index):
    content_label = index
    index_r = pd.Index(stocks, name = 'Strike')
    iterables_c = [[index], ['Corr']]
    index_c = pd.MultiIndex.from_product(iterables_c, names = [index, 'Beta_Info'])
    df = pd.DataFrame(corrs, index = index_r, columns = index_c)
    return df

def get_both(beta_df, corrs_df):
    return beta_df.join(corrs_df)

def get_multiple_indices(stocks, indices):
    for index in indices:
        df = get_both(stocks, index)


stocks = ['AAPL', 'GOOG', 'FB']
stocks = ['SRPT', 'AAPL', 'CRBP']
stocks = HealthcareSymbols[-5:]
index = 'SPY'
betas = get_betas(stocks, index, lookback = 400)
corrs = get_corrs(stocks, index, lookback = 400)
beta_df = get_betas_df(stocks, betas, corrs, index)
corrs_df = get_corrs_df(stocks, betas, corrs, index)
both = beta_df.join(corrs_df)
print(beta_df.round(3).sort_values((index, 'Corr'), ascending=False).to_string())

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

"""
best_betas = get_best_betas().sort_values(['Index', 'Beta'], ascending=[True, False])

print(best_betas.round(2).to_string())

best_betas.to_csv('best_betas.csv')

pickle_file = open('best_betas.pkl', 'wb')
pickle.dump(best_betas, pickle_file, pickle.HIGHEST_PROTOCOL)
pickle_file.close()
"""
