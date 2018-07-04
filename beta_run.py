from beta_class import Beta, ScrubParams, StockLineSimple, StockLineBetaAdjusted, StockChart
from utility.general import tprint

def run():
    stock = 'NBIX'
    stock2 = 'NBIX'
    index = 'XBI'
    beta_lookback = 252
    chart_lookback = beta_lookback

    base = 100
    scrub_params = ScrubParams(.125, .01, .9)

    beta = Beta(stock, index, beta_lookback, scrub_params)
    print(beta.num_days_in_calculation)
    #print(beta.degrees_of_freedom)
   
    print(beta.beta)
    print(beta.beta1)
    
    beta.describe()
    beta.show_scrub_trajectory()
    
    #beta2 = Beta(stock2, index, beta_lookback, scrub_params).beta
    #beta, beta2 = 0.0, 0.0
    
    """
    # Stock Lines to plot
    stock_line = StockLineSimple(stock, chart_lookback, base)
    index_line = StockLineSimple(index, chart_lookback, base)
    stock_line_adj = StockLineBetaAdjusted(stock, chart_lookback, beta, index, base)
    tprint(stock_line_adj.prices_df.round(2))
    
    stock_line_adj2 = StockLineBetaAdjusted(stock2, chart_lookback, beta2, index, base)

    stock_lines = [stock_line.stock_line(color = 'red'),
                   index_line.stock_line(color = 'black'),
                   stock_line_adj.stock_line(color = 'blue'),
                   #stock_line_adj2.stock_line(color = 'c')
                   ]
    StockChart(stock_lines).run()

    Beta(stock, index, beta_lookback, ScrubParams(.075, .01, .8)).show_scrub_trajectory()
    """
run()
