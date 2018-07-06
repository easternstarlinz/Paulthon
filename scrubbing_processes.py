from ols_df_transform import create_ols_df
from utility.decorators import my_time_decorator, empty_decorator
from utility.finance import daily_returns, get_daily_returns, get_ETF_beta_to_SPY, get_total_return, calculate_percentile_value, get_symbol_from_returns_df, ceiling_scrub, floor_scrub, calculate_average_daily_move_from_returns

from scrub_params import ScrubParams

NO_USE_TIME_DECORATOR = True
if NO_USE_TIME_DECORATOR == True:
    my_time_decorator = empty_decorator

# The big difference between the two types of scrubbing is that in the original way, I delete the rows from the columns. In the second way, I want to show a NaN value. Which way is better and how big is the difference in methodology?
@my_time_decorator
def stock_ceiling_scrub_process(returns_df_to_scrub: 'DataFrame of daily returns (multiple stocks allowed)',
                                stock_move_ceiling,
                                stock_to_drive_scrubbing=False):
    """Eliminate data points for all stocks on days where the target stock moved more (absolute value) than the specified cutoff.
        For DataFrames with multiple stocks, the user can specify the target stock.
        For DataFrames with just one symbol (one column), the target stock is by default the only column."""
    if stock_move_ceiling:
    
        if stock_to_drive_scrubbing == False:
            stock_to_drive_scrubbing = get_symbol_from_returns_df(returns_df_to_scrub)
    
        scrubbed_df = returns_df_to_scrub[abs(returns_df_to_scrub[stock_to_drive_scrubbing]) <= stock_move_ceiling]
        return scrubbed_df
    
    else:
        return returns_df_to_scrub


def ceiling_scrub_process_by_percentile(returns_df, percentile_ceiling=100):
    """Scrub the returns above a certain percentile ceiling. This function is only for one stock at a time."""
    """Not using at the moment but don't delete yet"""
    ceiling_value = calculate_percentile_value(returns_df, percentile_ceiling)
    scrubbed_returns = stock_ceiling_scrub_process(returns_df_to_scrub=returns_df,
                                                   stock_move_ceiling=ceiling_value)
    return scrubbed_returns

def largest_abs_value_in_dataframe(dataframe):
    max_number = dataframe.max().item()
    min_number = dataframe.min().item()
    return max(abs(max_number), abs(min_number))


class Stock_Ceiling_Params(object):
    def __init__(self, initial_ceiling, SD_multiplier):
        self.initial_ceiling = initial_ceiling
        self.SD_multiplier = SD_multiplier

class Index_Floor_Params(object):
    def __init__(self, SD_multiplier):
        self.SD_multiplier = SD_multiplier


# Stock Ceiling Params
STOCK_CEILING_INITIAL_CEILING = .125
STOCK_CEILING_SD_MULTIPLIER = 3.0

default_stock_ceiling_params  = Stock_Ceiling_Params(initial_ceiling=STOCK_CEILING_INITIAL_CEILING,
                                                     SD_multiplier=STOCK_CEILING_SD_MULTIPLIER)

# Index Floor Params
INDEX_FLOOR_SD_MULTIPLIER = 1.0

default_index_floor_params = Index_Floor_Params(SD_multiplier=INDEX_FLOOR_SD_MULTIPLIER)


# Best Fit Param
BEST_FIT_PERCENTILE = 95

stock_ceiling_params = Stock_Ceiling_Params(initial_ceiling=STOCK_CEILING_INITIAL_CEILING,
                                            SD_multiplier=STOCK_CEILING_SD_MULTIPLIER)

index_floor_params = Index_Floor_Params(SD_multiplier=INDEX_FLOOR_SD_MULTIPLIER)

best_fit_param = BEST_FIT_PERCENTILE



def get_scrub_params(stock,
                     index,
                     lookback=252, 
                     stock_ceiling_params=default_stock_ceiling_params,
                     index_floor_params=default_index_floor_params,
                     best_fit_param=BEST_FIT_PERCENTILE):
    """Based on the returns data and , determine the scrub_params"""
    stock_returns_df = get_daily_returns(stock, lookback)
    index_returns_df = get_daily_returns(index, lookback)
    
    stock_ceiling = determine_stock_ceiling_for_scrub_process_from_stock_returns(stock_returns_df, stock_ceiling_params)
    index_floor = determine_index_floor_for_scrub_process_from_index_returns(index_returns_df, index_floor_params)
    
    scrub_params = ScrubParams(stock_ceiling, index_floor, best_fit_param)
    return scrub_params

def initial_scrub_process(returns_df, STOCK_CEILING_INITIAL_SCRUB):
    if STOCK_CEILING_INITIAL_SCRUB:
        initial_scrub = stock_ceiling_scrub_process(returns_df, STOCK_CEILING_INITIAL_SCRUB)
        return initial_scrub
    else:
        return returns_df

def calculate_SD_multiple_from_returns(returns_df, SD_multiplier):
    average_daily_move = calculate_average_daily_move_from_returns(returns_df)
    SD_multiple = average_daily_move*SD_multiplier
    return SD_multiple


def determine_stock_ceiling_for_scrub_process_from_stock_returns(returns_df,
                                                                 stock_ceiling_params=default_stock_ceiling_params):
    """Dead description: Weinerize the returns with a percentile cutoff. The purpose of the normalization process is to scrub away outsized moves for all stocks, while taking into account that some stocks on average move more than other stocks.
    A percentile cutoff is intuitive because a 3.0% move for AAPL may be outsized whereas a 3.0% move for SRPT would be standard daily volatility."""
    initial_scrub = initial_scrub_process(returns_df, stock_ceiling_params.initial_ceiling)
    stock_ceiling = calculate_SD_multiple_from_returns(initial_scrub, stock_ceiling_params.SD_multiplier)
    return stock_ceiling

def determine_stock_ceiling_for_scrub_process(stock,
                                              lookback=252,
                                              stock_ceiling_params=default_stock_ceiling_params):
    returns_df = get_daily_returns(stock, lookback)
    stock_ceiling = determine_stock_ceiling_for_scrub_process_from_stock_returns(returns_df, stock_ceiling_params)
    return stock_ceiling



def determine_index_floor_for_scrub_process_from_index_returns(returns_df,
                                                               index_floor_params=default_index_floor_params):
    index_floor = calculate_SD_multiple_from_returns(returns_df,
                                                     SD_multiplier=index_floor_params.SD_multiplier)    
    return index_floor

def determine_index_floor_for_scrub_process(stock,
                                            lookback=252,
                                            stock_ceiling_params=default_index_floor_params):
    returns_df = get_daily_returns(stock, lookback)
    stock_ceiling = determine_index_floor_for_scrub_process_from_index_returns(returns_df, stock_ceiling_params)
    return stock_ceiling

#returns = get_daily_returns('NBIX', lookback=252)
#stock_ceiling_for_scrub_process = determine_stock_ceiling_for_scrub_process_from_stock_returns(returns)

if __name__ == '__main__':
    stock_ceiling = determine_stock_ceiling_for_scrub_process('NBIX')
    print('Stock Ceiling:', stock_ceiling)
    index_floor = determine_index_floor_for_scrub_process('XBI')
    print('Index Floor:', index_floor)

    scrub_params = get_scrub_params('NBIX', 'XBI')
    print(scrub_params)

    #daily_returns = get_daily_returns('XBI', lookback=50)
    #scrubbed_returns = ceiling_scrub_process_by_percentile(daily_returns, percentile_ceiling=90)
    #print(scrubbed_returns)

@my_time_decorator
def index_floor_scrub_process(returns_df_to_scrub: 'DataFrame of daily returns for the stock and index',
                              index_to_drive_scrubbing,
                              index_move_floor):
    """Eliminate data points where the index moved less than the index cutoff"""
    if index_move_floor:
        scrubbed_df = returns_df_to_scrub[abs(returns_df_to_scrub[index_to_drive_scrubbing]) >= index_move_floor]
        return scrubbed_df
    else:
        return returns_df_to_scrub

@my_time_decorator
def best_fit_scrub_process(returns_df_to_scrub: 'DataFrame of daily returns and OLS info. for the stock and index',
                           stock,
                           index,
                           percentile_cutoff):
    """Create an OLS regression, and add the best fit line to the returns DataFrame.
       Keep the n percentile data points that have the best fit based on OLS regression"""
    if percentile_cutoff:
        ols_df_to_scrub = create_ols_df(returns_df_to_scrub)

        best_fit_cutoff = ols_df_to_scrub['error_squared'].quantile(percentile_cutoff/100)
        scrubbed_ols_df = ols_df_to_scrub[ols_df_to_scrub['error_squared'] <= best_fit_cutoff]
        scrubbed_df = scrubbed_ols_df.loc[:, [stock, index]]
        return scrubbed_df
    else:
        return returns_df_to_scrub
