import pandas as pd
import matplotlib.pyplot as plt

import statsmodels.formula.api as sm
import statsmodels.api as sm

# Paul Utils
from utility.general import tprint
from utility.finance import daily_returns
from data.finance import PriceTable

from beta_model.beta_class import Beta

class ScrubParams(object):
    """Three Parameters for Scrubbing Process; Sequentially Optional"""
    def __init__(self,
                    stock_cutoff: 'float' = None,
                    index_cutoff: 'float' = None,
                    percentile_cutoff: 'float' = None):
        self.stock_cutoff = stock_cutoff
        self.index_cutoff = index_cutoff
        self.percentile_cutoff = percentile_cutoff

    def __repr__(self):
        return "ScrubParams({:2f}, {:2f}, {:0f})".format(self.stock_cutoff, self.index_cutoff, self.percentile_cutoff)

def OLS_df(df: 'DataFrame of (stock, index) daily returns') -> 'DataFrame of (stock, index) daily returns with y_hat, error, error_squared':
    stock = df.columns[0]
    index = df.columns[1]
    
    model = sm.OLS(df[stock], df[index], missing = 'drop')
    results = model.fit()

    df['y_hat'] = df[index]*results.params[index]
    df['error'] = df[stock] - df['y_hat']
    df['error_squared'] = df['error']*df['error']
    return df


class StockLineSimple(object):
    def __init__(self, stock: 'str', lookback: 'int', base = None):
        self.stock = stock
        self.lookback = lookback
        if base is None:
            self.base = self.stock
        else:
            self.base = base

        self.price_table = PriceTable.head(self.lookback)[[self.stock]]
        self.daily_returns = daily_returns(self.price_table).head(self.lookback)

    @property
    def stock_base_price(self):
        return self.price_table.tail(1)[self.stock].iloc[0]
        
    @property   
    def base_price(self):
        if self.base == self.stock:
            return self.price_table.tail(1)[self.stock].iloc[0]
        elif type(self.base) is str:
            return PriceTable.head(self.lookback).tail(1)[self.base].iloc[0]
        elif type(self.base) == float or type(self.base == int):
            return self.base
        else:
            raise ValueError
    
    @property
    def prices_df(self):
        mult = self.base_price / self.stock_base_price
        return self.price_table.iloc[::-1] * mult
    
    @property
    def total_return(self):
        return self.prices_df.tail(1).iloc[0, 0] / self.prices_df.head(1).iloc[0,0] - 1

    @property
    def stock_line_name(self):
        if self.stock == self.base:
            return "{}".format(self.stock)
        else:
            return "{} (Base: {})".format(self.stock, self.base)  
    
    def stock_line(self, color, name = None):
        if name is None:
            name = self.stock_line_name
        return (self.prices_df, color, name)

class StockLineBetaAdjusted(StockLineSimple):
    def __init__(self, stock: 'str', lookback: 'int', beta: 'float', index: 'str', base = None):
        super().__init__(stock, lookback, base)
        self.beta = beta
        self.index = index
    
    @property
    def adjusted_returns_df_column_name(self):
        return "{}_Adj.".format(self.stock)
    
    @property
    def adjusted_returns_scrubbed_df_column_name(self):
        return "{}_Adj_Scrubbed".format(self.stock)
    
    @property   
    def adjusted_returns(self):
        index_prices = PriceTable.head(self.lookback).loc[:, [self.index]]
        index_returns = daily_returns(index_prices)
        
        adj_returns = (1 + self.daily_returns[self.stock]) / (1 + index_returns[self.index]*self.beta) - 1
        adj_returns.name = self.adjusted_returns_df_column_name
        return adj_returns.to_frame()


    def adjusted_returns_scrubbed(self, stock_cutoff = .075):
        adjusted_returns_scrubbed_df =  self.adjusted_returns[abs(self.adjusted_returns[self.adjusted_returns_df_column_name]) <= stock_cutoff]
        adjusted_returns_scrubbed_df.columns = [self.adjusted_returns_scrubbed_df_column_name]
        return adjusted_returns_scrubbed_df
    
    @property
    def prices_df(self):
        dates = list(reversed(self.adjusted_returns.index.values))
        returns = list(reversed(self.adjusted_returns.iloc[:,0].tolist()))
        prices = [self.base_price]
        for i in range(1, len(dates)):
            daily_move = returns[i]
            prices.append((1 + daily_move)*prices[i-1])
        prices_df = pd.DataFrame({'Dates': dates, 'Adj_Prices': prices}).set_index('Dates')
        return prices_df

    @property
    def chart_name(self):
        return "{}; Index: {}, Beta: {:.2}".format(self.stock, self.index, self.beta)


class StockChart(object):
    def __init__(self, stock_lines: 'list of stock lines'):
        self.stock_lines = stock_lines

    def run(self):
        fig = plt.figure()
        ax1 = plt.subplot2grid((1,1), (0,0)) #ax1 is a subplot, ax2 would be a second subplot
        ax1.grid(True, color='gray', linestyle='-', linewidth=.5)
        
        for stock_line in self.stock_lines:
            prices_df = stock_line[0]
            c = stock_line[1]
            l = stock_line[2]
            x = prices_df.index.tolist()
            y = prices_df.iloc[:, 0].tolist()
            ax1.plot(x, y, color = c, label = l)
        
        
        plt.title("Stock Chart\nPut More Information Here")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.xticks(rotation=45)
        plt.style.use('ggplot')
        plt.legend()
        plt.subplots_adjust(left=.09, bottom=.12, right =.94, top=.9, wspace=.2, hspace=0)
        
        plt.show()

if __name__ == '__main__':
    stock = 'FB'
    stock2 = 'AAPL'
    index = 'QQQ'
    beta_lookback = 252
    chart_lookback = beta_lookback

    base = 100
    beta = Beta(stock, index, beta_lookback, ScrubParams(.075, .01, .8)).beta_value
    beta2 = Beta(stock2, index, beta_lookback, ScrubParams(.075, .01, .8)).beta_value
#beta_value, beta2 = 0.0, 0.0

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
