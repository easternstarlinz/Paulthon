import copy
import pprint
from pprint import pprint
import statsmodels.formula.api as sm
import statsmodels.api as sm
import copy
from beta_class import Beta, ScrubParams
from StockLine_Module import StockLineBetaAdjusted

from utility.finance import daily_returns

if __name__ == '__Main__':
    stock = 'ABBV'
    index = 'XLV'
    beta_lookback = 400
    lookback = beta_lookback
    scrub_params = ScrubParams(.075, .01, .8)
    beta = Beta(stock, index, beta_lookback, scrub_params).beta

    stock_line = StockLineBetaAdjusted(stock, lookback, beta, index)
    adjusted_returns = stock_line.adjusted_returns
    #print(adjusted_returns)

class Beta_StepTwo(Beta):
    def __init__(self,
                 stock: 'str',
                 index: 'str',
                 lookback: 'int',
                 ScrubParams: 'obj'):
        super().__init__(stock, index, lookback, ScrubParams)
    
        beta_value = Beta(self.stock, self.index, self.lookback, self.ScrubParams).beta
        #print("{}, {}, Beta: {}".format(self.stock, self.index, beta_value))
        self.stock_line = copy.deepcopy(StockLineBetaAdjusted(self.stock, self.lookback, beta_value, self.index))
        self.adjusted_returns = self.stock_line.adjusted_returns
        self.adjusted_returns_df_column_name = self.stock_line.adjusted_returns_df_column_name
        print(self.stock, self.index) 
    
    """
    @property
    def stock_line(self):
        beta_value = Beta(self.stock, self.index, self.lookback, self.ScrubParams).beta
        print("{}, {}, Beta: {}".format(self.stock, self.index, beta_value))
        return copy.deepcopy(StockLineBetaAdjusted(self.stock, self.lookback, beta_value, self.index))

    @property
    def adjusted_returns(self):
        return self.stock_line.adjusted_returns
    
    @property
    def adjusted_returns_df_column_name(self):
        return self.stock_line.adjusted_returns_df_column_name
    """

    @property
    def initial_scrub(self):
        if self.ScrubParams.stock_cutoff:
            #print(self.stock, self.index)
            return self.daily_returns[abs(self.adjusted_returns[self.adjusted_returns_df_column_name]) <= self.ScrubParams.stock_cutoff]
            return self.daily_returns[abs(self.daily_returns[self.stock]) <= self.ScrubParams.stock_cutoff]
        else:
            return None
