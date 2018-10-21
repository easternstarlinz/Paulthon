
def create_beta_object(stock,
                       index,
                       lookback=252,
                       stock_ceiling_params=default_stock_ceiling_params,
                       index_floor_params=default_index_floor_params,
                       best_fit_param=BEST_FIT_PERCENTILE):
    """Calculate the adjusted beta_value measurement for the stock and index over a lookback based on the three core adjustments:
        - Stock Ceiling: Scrub data points where the stock moved more than the specified threshold.
        - Index Floor: Scrub data points where the index moved less than the specified threshold.
        - Best Fit Param: Keep only the n-percentile best fit points in the OLS regression"""

    scrub_params = get_scrub_params(stock,
                                    index,
                                    lookback=lookback,
                                    stock_ceiling_params=default_stock_ceiling_params,
                                    index_floor_params=default_index_floor_params,
                                    best_fit_param=BEST_FIT_PERCENTILE)
    
    beta = Beta(stock, index, lookback, scrub_params)
    return beta

