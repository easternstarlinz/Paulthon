import numpy as np
import datetime as dt
import pandas as pd
import pickle
import math
import decimal
import copy
from functools import reduce
import pprint
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm
import pylab
import scipy.stats as ss
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from decorators import my_time_decorator
from ols import OLS
from ols2 import OLS as MainOLS
from scipy.interpolate import interp1d, UnivariateSpline
import logging

ManualSymbolExcludes = ['BRK.B', 'BKNG', 'BHF', 'BF.B', 'CBRE', 'FTV', 'UA', 'WELL', 'XRX' 'BHH', 'AEE']

PriceTable = pickle.load(open('sp500_prices.pkl', 'rb'))
PriceTable.index = pd.to_datetime(PriceTable.index)
stocks = PriceTable.columns.values.tolist()
SymbolExcludes = ManualSymbolExcludes + [i for i in stocks if PriceTable.loc[:, i].isnull().values.any()]

stocks = [i for i in stocks if i not in SymbolExcludes]
PriceTable = PriceTable.loc[:, stocks][::-1]
#print(PriceTable)

ETF_PriceTable = pickle.load(open('ETF_prices.pkl', 'rb'))
ETF_PriceTable.index = pd.to_datetime(ETF_PriceTable.index)
#print(ETF_PriceTable)

# Temporary Fix to use ETF_PriceTable in the Beta Module
#PriceTable = ETF_PriceTable

InformationTable = pd.read_csv('information_table.csv')
InformationTable.rename(columns = {'Last Close': 'Price', 'Ticker': 'Stock', 'Market Cap ': 'Market Cap'}, inplace=True)
InformationTable.set_index('Stock', inplace=True)

info = pd.read_csv('stock_screen.csv').set_index('Ticker').rename(columns = {'Market Cap ': 'Market Cap', 'Last Close': 'Price'})
HealthcareSymbols = info[(info.Sector == 'Medical') & (info['Market Cap'] > 750) & (info['Price'] > 3.00)].index.tolist()
HealthcareSymbols = [i for i in HealthcareSymbols if i not in {'AAAP', 'BOLD', 'LNTH', 'MEDP', 'TCMD'}]

Symbols = info.index.tolist()
SP500Symbols = pd.read_html('https://en.wikipedia.org/wiki/List_of_S&P_500_companies')[0][0][1:].reset_index(drop=True).tolist()
SP500Symbols = sorted([sym for sym in SP500Symbols if sym not in SymbolExcludes])


BestBetas = pickle.load(open('best_betas.pkl', 'rb'))

VolBeta = pd.read_csv('VolbetaDistribution.csv')
#EarningsEvents = pickle.load(open('EarningsEvents.pkl', 'rb')) # Can't include here because of circular imports.

TakeoutParams = pd.read_csv('TakeoutParams.csv').set_index('Stock')

def to_pickle(content, file_name):
    pickle_file = open('{}.pkl'.format(file_name), 'wb')
    pickle.dump(content, pickle_file, pickle.HIGHEST_PROTOCOL)
    pickle_file.close()

def to_pickle_and_CSV(content, file_name):
    to_pickle(content, file_name)
    content.to_csv("{}.csv".format(file_name))

def setup_standard_logger(file_name):
    # Logging Setup
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s', "%m/%d/%Y %H:%M")

    file_handler = logging.FileHandler('{}.log'.format(file_name))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

def daily_returns(price_table: 'df of prices') -> 'df of daily_returns':
    return price_table / price_table.shift(-1) - 1

def get_ETF_beta_to_SPY(ETF):
    ETF_betas = pickle.load(open('ETF_betas.pkl', 'rb'))
    try:
        beta = ETF_betas.loc[ETF, ('SPY', 'Beta')]
        return beta
    except:
        print("{} is not in the ETF beta table".format(ETF))
        return 1.0

Best_Betas = pickle.load(open('Best_Betas.pkl', 'rb'))
SPY_Betas_Raw = pickle.load(open('SPY_Betas_Raw.pkl', 'rb'))
SPY_Betas_Scrubbed = pickle.load(open('SPY_Betas_Scrubbed.pkl', 'rb'))

def get_total_return(stock, lookback):
    stock_prices = PriceTable.loc[:, stock].head(lookback)
    stock_prices = stock_prices[stock_prices.notnull()]
    #print(stock_prices.to_string())
    start_price = stock_prices.iloc[-1]
    end_price = stock_prices.iloc[0]
    total_return = end_price / start_price - 1
    #print(start_price, end_price)
    return total_return

def get_num_days_above_cutoff(stock, lookback, cutoff, below_cutoff=False, absolute_value=False):
    stock_prices = PriceTable.loc[:, stock].head(lookback)
    stock_prices = stock_prices[stock_prices.notnull()]
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
    print(type(returns))
    print(filtered_days, total_days)
    return filtered_days / total_days

num = get_num_days_above_cutoff('SPY', 450, .005, absolute_value = True)
print(num)

num = get_num_days_above_cutoff('SPY', 450, -.01, below_cutoff=True)
print(num)






#num = get_total_return('SPY', 400)
#print(num)

def merge_dfs_horizontally(dfs: 'list of dfs'):
    if len(dfs) == 1:
        return dfs[0]
    else:
        return reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), dfs)

def append_dfs_vertically(dfs: 'list of dfs'):
    if len(dfs) == 1:
        return dfs[0]
    else:
        return reduce(lambda x, y: x.append(y), dfs)


def tprint(*args):
    print("TPrint Here--------")
    for arg in args:
        print("Type: ", type(arg), "\n", "Obj: ", arg, sep='')

def rprint(*args):
    print("RPrint Here--", end="")
    for arg in args:
        if args.index(arg) == len(args)-1:
            e = " \n"
        else:
            e = ", "
        if type(arg) is not str:
            print(round(arg, 3), end = e)
        else:
            print(arg, end = e)

def lprint(*args):
    print("LPrint Here--------")
    for arg in args:
        print("Len: ", len(arg), "\n", sep='')

def get_histogram_from_array(results: 'array of numbers', bins = 10**2, title = 'Monte Carlo Simulation\n Simulated Distribution'):
    #start, end, interval = -.5, .5, .025
    #bins = np.arange(start - interval/2, end + interval/2, interval)
    
    plt.hist(results, bins, histtype='bar', rwidth=1.0, color = 'blue', label = 'Rel. Frequency')
    plt.title(title)
    plt.xlabel('Relative Price')
    plt.ylabel('Relative Frequency')
    plt.legend()
    plt.show()


def show_mc_distributions_as_line_chart(mc_distributions, labels = None):
    i = 0
    for mc_distribution in mc_distributions:
        min_cutoff = np.percentile(mc_distribution, 0)
        max_cutoff = np.percentile(mc_distribution, 100)
        mc_distribution = [i for i in mc_distribution if (i > min_cutoff) and (i < max_cutoff)]
        
        #print('Percentiles', (np.percentile(mc_distribution, .1), np.percentile(mc_distribution, .9)))
        #print('Min_Max', (np.min(mc_distribution), np.max(mc_distribution)))
        
        bin_min = np.percentile(mc_distributions[-1], .25)
        bin_max = np.percentile(mc_distributions[-1], 99.75)
        y, binEdges = np.histogram(mc_distribution, bins=np.arange(bin_min, bin_max, .00875))
        
        bincenters = .5*(binEdges[1:] + binEdges[:-1])
        
        xnew = np.linspace(bin_min+.01, bin_max-.01, num=10**3, endpoint=True)

        #p = np.polyfit(bincenters, y, 3)
        #y_p = np.polyval(p, xnew)
        f = interp1d(bincenters, y, kind='cubic')
        #f = UnivariateSpline(bincenters, y, s=1)
        #f = UnivariateSpline(xnew, y, s=1)
        #pylab.plot(xnew, f(xnew), '-', label = "Events {}".format(i))
        
        if labels == None:
            label = "Distribution {}".format(i+1)
        else:
            label = labels[i]
        pylab.plot(bincenters, y, '-', label=label)
        i += 1
    pylab.legend()
    pylab.show()

if __name__ == '__main__':
    pass
