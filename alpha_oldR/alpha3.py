from paul_resources import PriceTable, daily_returns, tprint, rprint, lprint
from beta_class_6 import Beta, ScrubParams, StockLineBetaAdjusted
import numpy as np
import pandas as pd
import math
from operator import mul
from functools import reduce
import matplotlib.pyplot as plt
from decorators import my_time_decorator
from paul_resources import HealthcareSymbols

def get_total_return(df: 'df of prices'):
    #return prices_df_stock.head(1).iloc[0] / prices_df_stock.tail(1).iloc[0] - 1
    print(df.columns.tolist(), df.head(1), df.tail(1), sep="\n"*2)
    return df.head(1).iloc[0, 0] / df.tail(1).iloc[0, 0] - 1

def calc_HV(df: 'df of daily returns'):
    return df.dropna(axis=0, how='any').iloc[:, 0].std(ddof=0)*math.sqrt(252)

def get_sample_size(df: 'df of daily_returns'):
    return df.shape[0]
    
@my_time_decorator
def alpha_df(df: 'df of prices', lookback):
    prices_df = df.head(lookback)
    #returns_df = daily_returns(prices_df).dropna(axis=0, how='any')
    returns_df = daily_returns(prices_df)
    #print(prices_df.isnull().values.ravel().sum())

    stocks = df.columns.values.tolist()
    total_returns = []
    HVs = []
    alpha_ratios = []
    adj_alpha_ratios = []
    sample_sizes = []
    betas = []
    times = []
    #correlations = []
    
    #for stock in stocks:
    #    result = prices_df[prices_df[stock].isnull()].index.tolist()
    #    print(stock, ": ", result, sep='')
    
    for stock in stocks:
        prices_df_stock = prices_df[stock].dropna(axis=0, how='any').to_frame()
        daily_returns_df_stock = daily_returns(prices_df_stock).dropna(axis=0, how='any')

        # Calculate Adjusted Returns
        index = 'IBB'
        if stock == 'SPY':
            index = 'IWM'
        beta_object = Beta(stock, index, 500, ScrubParams(.075, .0125, .8))
        beta = beta_object.beta
        #beta = 0
        if stock == 'SPY':
            beta = 0
        adj_stock_line = StockLineBetaAdjusted(stock, lookback, beta, index)
        
        prices_df_stock = adj_stock_line.prices_df
        daily_returns_df_stock = adj_stock_line.adjusted_returns

        num_observations = len(daily_returns_df_stock.values.tolist())

        #total_return = prices_df_stock.head(1).iloc[0] / prices_df_stock.tail(1).iloc[0] - 1
        #print('HEREEE', total_move)
        #total_return = get_total_return(prices_df_stock)
        total_return = adj_stock_line.total_return
        total_returns.append(total_return)
        
        HV = calc_HV(daily_returns_df_stock)
        HVs.append(HV)

        sample_size = get_sample_size(daily_returns_df_stock)
        sample_sizes.append(sample_size)

        alpha_ratio = total_return / HV
        alpha_ratios.append(alpha_ratio)

        # Should the Time Adjustment be sqrt(time)?
        adj_alpha_ratio = alpha_ratio * math.sqrt(252/num_observations)
        adj_alpha_ratio = alpha_ratio * (252/num_observations)
        std_dev_over_time_period = HV*math.sqrt(num_observations / 252)
        adj_alpha_ratio = total_return / std_dev_over_time_period
        adj_alpha_ratios.append(adj_alpha_ratio)

        betas.append(beta)

        #correlation = beta_object.corr
        #correlations.append(correlation)
        
        time = num_observations/252
        times.append(time)


    alpha_df_info = {'Stock': stocks,
                     'Total_Return': total_returns,
                     'HV': HVs,
                     'Alpha_Ratio': alpha_ratios,
                     'Adj_Alpha_Ratio': adj_alpha_ratios,
                     'Sample_Size': sample_sizes,
                     'Beta': betas,
                     #'Correlation': correlations,
                     'Time': times
                     }

    alpha_df = pd.DataFrame(alpha_df_info).set_index('Stock').loc[:, ['Total_Return',
                                                                      'HV',
                                                                      'Alpha_Ratio',
                                                                      'Adj_Alpha_Ratio',
                                                                      'Sample_Size',
                                                                      'Beta',
                                                                      'Time']].round(3)
    return alpha_df

stocks = PriceTable.columns.values.tolist()
#stocks = [i for i in stocks if i in {'SPY','IWM', 'QQQ', 'FB', 'NKTR', 'AAPL', 'NVDA'}]
stocks = [i for i in stocks if i in HealthcareSymbols]

prices_df = PriceTable.loc[:, stocks].head(252)
alpha_df = alpha_df(prices_df, 252)
alpha_df = alpha_df[alpha_df.HV < .4]
print(alpha_df.sort_values('Adj_Alpha_Ratio', ascending=False).to_string())

def graph():
    values = alpha_df['Adj_Alpha_Ratio'].tolist()
    bins = np.arange(-5., 5.5, .5)
    
    plt.hist(values, bins, histtype = 'bar', rwidth=.8)
    
    plt.xlabel('Adj_Alpha_Ratio')
    plt.ylabel('Frequency')
    plt.title('S&P 500 Alpha Distribution')
    plt.legend()
    plt.show()

graph()

def get_probability_density(distribution, target, greater_than = True):
    i = 0
    if greater_than is True:
        for number in distribution:
            if number > target:
                i += 1
    else:
        for number in distribution:
            if number < target:
                i += 1
    return i / len(distribution)



adj_alpha_ratios = alpha_df.loc[:, ['Adj_Alpha_Ratio']].values.tolist()
print(adj_alpha_ratios)

for i in np.arange(-3, 4, 1):
    if i >= 0:
        greater_than = True
        print_sym = ">"
    else:
        greater_than = False
        print_sym = "<"
    
    density = get_probability_density(adj_alpha_ratios, i, greater_than)
    print("{}{:.1f} SD: {:.1f}%".format(print_sym, i, density*100))
