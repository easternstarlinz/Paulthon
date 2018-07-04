from ols_df_transform import create_ols_df
from utility.decorators import my_time_decorator, empty_decorator

NO_USE_TIME_DECORATOR = True
if NO_USE_TIME_DECORATOR == True:
    my_time_decorator = empty_decorator

@my_time_decorator
def stock_ceiling_scrub_process(returns_df_to_scrub: 'DataFrame of daily returns for the stock and index',
                                stock_to_drive_scrubbing,
                                stock_move_ceiling):
    """Eliminate data points where the stock moved greater (absolute value) than the specified stock cutoff.
       This process imposes a celing for the magnitude of stock moves included in the sample."""
    if stock_move_ceiling < 1.0:
        scrubbed_df = returns_df_to_scrub[abs(returns_df_to_scrub[stock_to_drive_scrubbing]) <= stock_move_ceiling]
        return scrubbed_df
    else:
        return returns_df_to_scrub

@my_time_decorator
def index_floor_scrub_process(returns_df_to_scrub: 'DataFrame of daily returns for the stock and index',
                              index_to_drive_scrubbing,
                              index_move_floor):
    """Eliminate data points where the index moved less than the index cutoff"""
    if index_move_floor > 0:
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
    if percentile_cutoff < 1.0:
        ols_df_to_scrub = create_ols_df(returns_df_to_scrub)

        best_fit_cutoff = ols_df_to_scrub['error_squared'].quantile(percentile_cutoff)
        scrubbed_ols_df = ols_df_to_scrub[ols_df_to_scrub['error_squared'] <= best_fit_cutoff]
        scrubbed_df = scrubbed_ols_df.loc[:, [stock, index]]
        return scrubbed_df
    else:
        return returns_df_to_scrub
