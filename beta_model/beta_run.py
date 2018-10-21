from beta_model.beta_class import Beta, StockLineSimple, StockLineBetaAdjusted, StockChart
from beta_model.scrub_params import ScrubParams
from beta_model.scrubbing_processes import get_scrub_params, Index_Floor_Params, Stock_Ceiling_Params


def calculate_adjusted_beta(stock,
                            index,
                            lookback,
                            stock_ceiling_params,
                            index_floor_params,
                            best_fit_param):
    """Calculate the adjusted beta_value measurement for the stock and index over a lookback based on the three core adjustments:
        - Stock Ceiling: Scrub data points where the stock moved more than the specified threshold.
        - Index Floor: Scrub data points where the index moved less than the specified threshold.
        - Best Fit Param: Keep only the n-percentile best fit points in the OLS regression"""

    scrub_params = get_scrub_params(stock,
                                    index,
                                    lookback=lookback,
                                    stock_ceiling_params=stock_ceiling_params,
                                    index_floor_params=index_floor_params,
                                    best_fit_param=best_fit_param)

    beta_value = Beta(stock, index, lookback, scrub_params).beta_value
    return beta_value


def run():
    stock = 'NBIX'
    stock2 = 'NBIX'
    index = 'XBI'
    beta_lookback = 252
    chart_lookback = beta_lookback

    base = 100
    scrub_params = ScrubParams(.125, .01, 90)

    stock_ceiling_params = Stock_Ceiling_Params(initial_ceiling=.20, SD_multiplier=4.0)
    index_floor_params = Index_Floor_Params(SD_multiplier=1.0)

    scrub_params = get_scrub_params(stock,
                                    index,
                                    stock_ceiling_params=stock_ceiling_params,
                                    index_floor_params=index_floor_params)

    beta = Beta(stock, index, beta_lookback, scrub_params)
    print(beta.num_days_in_calculation)
    # print(beta_value.degrees_of_freedom)

    print(beta.beta_value)
    print(beta.beta1)

    # beta_value.describe()
    beta.show_scrub_trajectory()

    # beta2 = Beta(stock2, index, beta_lookback, scrub_params).beta_value
    # beta_value, beta2 = 0.0, 0.0

    # Stock Lines to plot
    stock_line = StockLineSimple(stock, chart_lookback, base)
    index_line = StockLineSimple(index, chart_lookback, base)
    stock_line_adj = StockLineBetaAdjusted(stock, chart_lookback, beta.beta_value, index, base)

    stock_lines = [stock_line.stock_line(color='red'),
                   index_line.stock_line(color='black'),
                   stock_line_adj.stock_line(color='blue'),
                   ]
    StockChart(stock_lines).run()

    Beta(stock, index, beta_lookback, ScrubParams(.075, .01, 95)).show_scrub_trajectory()
    print('End of Module')


run()
