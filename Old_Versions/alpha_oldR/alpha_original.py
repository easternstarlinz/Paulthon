from paul_resources import PriceTable, daily_returns, tprint, rprint, lprint
from beta_class_5 import Beta, ScrubParams, StockLineBetaAdjusted
import numpy as np
import pandas as pd
import math
from operator import mul
from functools import reduce
import matplotlib.pyplot as plt

def alpha_df(df: 'df of prices', lookback):
    prices_df = df.head(lookback)
    #returns_df = daily_returns(prices_df).dropna(axis=0, how='any')
    returns_df = daily_returns(prices_df)
    #print(prices_df.isnull().values.ravel().sum())

    stocks = df.columns.values.tolist()
    #for stock in stocks:
    #    result = prices_df[prices_df[stock].isnull()].index.tolist()
    #    print(stock, ": ", result, sep='')

    total_returns = []
    HVs = []
    alpha_ratios = []
    adj_alpha_ratios = []
    sample_sizes = []
    
    for stock in stocks:
        prices_df_stock = prices_df[stock].dropna(axis=0, how='any')
        daily_returns_df_stock = daily_returns(prices_df_stock).dropna(axis=0, how='any')

        # Calculate Adjusted Returns
        index = 'SPY'
        beta = Beta(stock, index, lookback, ScrubParams(.075, .0125, .8)).beta_value
        beta = 0
        adj_stock_line = StockLineBetaAdjusted(stock, lookback, beta, index)
        
        prices_df_stock = adj_stock_line.prices_df
        daily_returns_df_stock = adj_stock_line.adjusted_returns

        total_move = prices_df_stock.head(1).iloc[0] / prices_df_stock.tail(1).iloc[0] - 1
        total_move = prices_df_stock.head(1).iloc[0, 0] / prices_df_stock.tail(1).iloc[0, 0] - 1
        total_returns.append(total_move)
        
        HV = daily_returns_df_stock.dropna(axis=0, how='any').std(ddof=0)*math.sqrt(252)
        HVs.append(HV)

        sample_size = daily_returns_df_stock.shape[0]
        sample_sizes.append(sample_size)

        alpha_ratio = total_move / HV
        alpha_ratios.append(alpha_ratio)

        adj_alpha_ratio = total_move*math.sqrt(252/lookback) / HV
        adj_alpha_ratios.append(adj_alpha_ratio)

    alpha_df_info = {'Stock': stocks,
                     'Total_Return': total_returns,
                     'HV': HVs,
                     'Alpha_Ratio': alpha_ratios,
                     'Adj_Alpha_Ratio': adj_alpha_ratios,
                     'Sample_Size': sample_sizes}

    alpha_df = pd.DataFrame(alpha_df_info)
    alpha_df = pd.DataFrame(list(zip(stocks, total_returns, HVs, alpha_ratios, adj_alpha_ratios, sample_sizes))).round(3)
    alpha_df.rename(index=str, columns={0: 'Stock', 1: 'Total_Return', 2: 'HV', 3: 'Alpha_Ratio', 4: 'Adj_Alpha_Ratio', 5: 'Sample_Size'}, inplace=True)
    alpha_df.set_index('Stock', inplace=True)
    return alpha_df

stocks = PriceTable.columns.values.tolist()
stocks = [i for i in stocks if i in {'AAPL', 'GOOG', 'FB', 'AMZN'}]

prices_df = PriceTable.loc[:, stocks]
alpha_df = alpha_df(prices_df, 252)
tprint(stocks)
print(alpha_df.sort_values('Adj_Alpha_Ratio', ascending=False))


def graph():
    values = alpha_df['Adj_Alpha_Ratio'].tolist()
    bins = np.arange(-5.5, 6.5, 1)
    
    plt.hist(values, bins, histtype = 'bar', rwidth=.8)
    
    plt.xlabel('Adj_Alpha_Ratio')
    plt.ylabel('Frequency')
    plt.title('S&P 500 Alpha Distribution')
    plt.legend()
    plt.show()

graph()
