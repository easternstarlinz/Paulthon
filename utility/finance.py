import numpy as np
import pickle
import math
from collections import namedtuple

import sys
sys.path.append('/home/paul/Paulthon')

# Paul Data
from data.finance import PriceTable

# Brought this over from get_best_betas_2.py since I use the constants in many of the formulas
SD_Cutoff_Params = namedtuple('SD_Cutoff_Params', ['Stock_SD_Cutoff', 'Index_SD_Cutoff', 'Stock_SD_Percentile_Cutoff', 'Index_SD_Percentile_Cutoff'])

STOCK_SD_CUTOFF = 8.0
INDEX_SD_CUTOFF = 1.75
STOCK_SD_PERCENTILE_CUTOFF = 90
INDEX_SD_PERCENTILE_CUTOFF = 100
LOOKBACK_DEFAULT = 400
sd_cutoff_params = SD_Cutoff_Params(STOCK_SD_CUTOFF, INDEX_SD_CUTOFF, STOCK_SD_PERCENTILE_CUTOFF, INDEX_SD_PERCENTILE_CUTOFF)


# Utility Math Functions
def calculate_percentile_value(numbers: 'list of numbers', percentile):
    return np.nanpercentile(abs(numbers), percentile)

def calculate_HV_from_returns(returns):
    """Return the HV calculation for an array of returns. NaN values in the data are allowed, and will be ignored"""
    return np.nanstd(returns)*math.sqrt(252)

def calculate_average_daily_move_from_HV(HV):
    return HV / math.sqrt(252)

def calculate_average_daily_move_from_returns(returns: 'df of returns'):
    return np.nanstd(returns)

def calculate_SD_multiple_from_returns(returns_df, SD_multiplier):
    average_daily_move = calculate_average_daily_move_from_returns(returns_df)
    SD_multiple = average_daily_move*SD_multiplier
    return SD_multiple


# Get ETF beta to SPY from a pre-saved table
def get_ETF_beta_to_SPY(ETF):
    try:
        ETF_betas = pickle.load(open('/home/paul/Paulthon/DataFiles/Betas/ETF_betas.pkl', 'rb'))
        beta = ETF_betas.loc[ETF, ('SPY', 'Beta')]
        return beta
    except:
        print("{} is not in the ETF beta table".format(ETF))
        return 1.0


# Get Symbol
def get_symbol_from_returns_df(returns_df):
    return returns_df.columns[0]


# Get Stock Prices
def get_stock_prices_over_lookback(stock, lookback):
    """Keeping this for now but using the function below in practice. Will likely delete this function."""
    stock_prices = PriceTable.loc[:, stock].head(lookback)
    stock_prices = stock_prices[stock_prices.notnull()]
    return stock_prices

def get_stock_prices(stock, lookback=252):
    """Return a DataFrame of prices for a given stock and lookback"""
    price_table = PriceTable.loc[:, [stock]].head(lookback)
    return price_table


# Get Returns
def daily_returns(price_table: 'df of prices') -> 'df of daily_returns':
    return price_table / price_table.shift(-1) - 1

def get_daily_returns(stock, lookback=252):
    """Return a DataFrame of daily returns for a given stock and lookback"""
    price_table = get_stock_prices(stock, lookback)
    return daily_returns(price_table)

def get_total_return(stock, lookback):
    """Get the total return for a stock over a lookback (num. days)"""
    # Get prices over the lookback period
    stock_prices = get_stock_prices(stock, lookback)
    
    # Get start and end prices
    start_price = stock_prices.iloc[-1].item()
    end_price = stock_prices.iloc[0].item()
    
    #print('Start Price: ', start_price, 'End Price: ', end_price)
    # Calculate Total Teturn
    total_return = end_price / start_price - 1
    return total_return


#returns = get_daily_returns('XBI', lookback=20)
#symbol = get_symbol_from_returns_df(returns)
#print(symbol)


# Scrubbing Functionality
def scrub_func(daily_return, cutoff, reverse_scrub=False):
    """Scrub a data point based on the specified cutoff"""
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

def ceiling_scrub(data_point, ceiling):
    if abs(data_point) < ceiling:
        return data_point
    else:
        return np.NaN

def floor_scrub(data_point, floor):
    if abs(data_point) > floor:
        return data_point
    else:
        return np.NaN



# Not using this as of now
def scrub_returns(returns,
                  percentile_cutoff=100,
                  reverse_scrub=False):
    """Scrub an array of returns based on a percentile_cutoff. The percentile_cutoff eliminates data points with the largest moves above the specified percentile_cutoff"""
    scrub_cutoff = calculate_percentile(returns, percentile_cutoff)
    returns = [scrub_func(daily_return, scrub_cutoff, reverse_scrub) for daily_return in returns.iloc[:, 0].tolist()]
    return returns



def get_scrubbed_HV_for_stock(stock,
                              lookback,
                              percentile_cutoff = STOCK_SD_PERCENTILE_CUTOFF):
    """Return the scrubbed HV for a stock over a specified lookback. Percentile_cutoff = 100 would return the standard HV calculation"""
    daily_returns = get_daily_returns(stock, lookback)
    daily_returns_scrubbed = scrub_returns(daily_returns, percentile_cutoff)
    return calculate_HV_from_returns(daily_returns_scrubbed)

def get_cutoff(stock,
              lookback = LOOKBACK_DEFAULT,
              percentile_cutoff = 100,
              std_dev_cutoff = 2):
    HV = get_scrubbed_HV_for_stock(stock, lookback, percentile_cutoff)
    return HV / math.sqrt(252) * std_dev_cutoff

def get_stock_cutoff(stock,
                     lookback = LOOKBACK_DEFAULT,
                     percentile_cutoff = STOCK_SD_PERCENTILE_CUTOFF,
                     std_dev_cutoff = STOCK_SD_CUTOFF):
    return get_cutoff(stock, lookback, percentile_cutoff, std_dev_cutoff)

def get_index_cutoff(index,
                     lookback = LOOKBACK_DEFAULT,
                     percentile_cutoff = INDEX_SD_PERCENTILE_CUTOFF,
                     std_dev_cutoff = INDEX_SD_CUTOFF):
    return get_cutoff(index, lookback, percentile_cutoff, std_dev_cutoff)


def get_scrub_params_from_sd_cutoff_params(stock,
                                        index,
                                        lookback,
                                        sd_cutoff_params,
                                        percentile_cutoff):
    index_cutoff = get_index_cutoff(index, lookback, sd_cutoff_params.Index_SD_Percentile_Cutoff, sd_cutoff_params.Index_SD_Cutoff)
    
    stock_cutoff_raw = get_stock_cutoff(stock, lookback, sd_cutoff_params.Stock_SD_Percentile_Cutoff, sd_cutoff_params.Stock_SD_Cutoff)
    stock_cutoff = max(.02 + index_cutoff*2, stock_cutoff_raw)
    return ScrubParams(stock_cutoff, index_cutoff, percentile_cutoff)


def get_num_days_above_cutoff(stock, lookback, cutoff, below_cutoff=False, absolute_value=False):
    # Get prices over the lookback period
    stock_prices = get_stock_prices_over_lookback(stock, lookback)
    
    # Get returns over the lookback period
    returns = daily_returns(stock_prices)


    if below_cutoff == False:
        if absolute_value == False:
            filtered_returns = returns[returns>cutoff]
        else:
            filtered_returns = returns[abs(returns)>cutoff]
    else:
        if absolute_value == False:
            filtered_returns = returns[returns<cutoff]
        else:
            filtered_returns = returns[abs(returns)<cutoff]
    
    total_days = len(returns.tolist())
    filtered_days = len(filtered_returns.tolist())
    return filtered_days / total_days

if __name__ == '__main__':
    num = get_num_days_above_cutoff('SPY', 450, .005, absolute_value = True)
    #print(num)

    num = get_num_days_above_cutoff('SPY', 450, -.01, below_cutoff=True)
    #print(num)
