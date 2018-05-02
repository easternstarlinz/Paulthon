import numpy as np
import datetime as dt
import pandas as pd
import pickle
import math
import decimal
import copy
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

PriceTable = pickle.load(open('sp500_3_price_table.pkl', 'rb'))
PriceTable.index = pd.to_datetime(PriceTable.index)
stocks = PriceTable.columns.values.tolist()
stocks = [i for i in stocks if i not in  {'BHH', 'CBRE', 'WELL', 'BKNG', 'BHF', 'FTV', 'UA'}]
PriceTable = PriceTable.loc[:, stocks]

InformationTable = pd.read_csv('information_table.csv')
InformationTable.rename(columns = {'Last Close': 'Price', 'Ticker': 'Stock', 'Market Cap ': 'Market Cap'}, inplace=True)
InformationTable.set_index('Stock', inplace=True)

info = pd.read_csv('stock_screen.csv').set_index('Ticker').rename(columns = {'Market Cap ': 'Market Cap', 'Last Close': 'Price'})
HealthcareSymbols = info[(info.Sector == 'Medical') & (info['Market Cap'] > 750) & (info['Price'] > 3.00)].index.tolist()
HealthcareSymbols = [i for i in HealthcareSymbols if i not in {'AAAP', 'BOLD', 'LNTH', 'MEDP', 'TCMD'}]

Symbols = info.index.tolist()

BestBetas = pickle.load(open('best_betas.pkl', 'rb'))

VolBeta = pd.read_csv('VolbetaDistribution.csv')
#EarningsEvents = pickle.load(open('EarningsEvents.pkl', 'rb')) # Can't include here because of circular imports.

TakeoutParams = pd.read_csv('TakeoutParams.csv').set_index('Stock')

def to_pickle(content, file_name):
    pickle_file = open('{}.pkl'.format(file_name), 'wb')
    pickle.dump(content, pickle_file, pickle.HIGHEST_PROTOCOL)
    pickle_file.close()

def daily_returns(price_table: 'df of prices') -> 'df of daily_returns':
    return price_table / price_table.shift(-1) - 1

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

def get_histogram_from_array(results: 'array of numbers', bins = 10**2):
    #start, end, interval = -.5, .5, .025
    #bins = np.arange(start - interval/2, end + interval/2, interval)
    
    plt.hist(results, bins, histtype='bar', rwidth=1.0, color = 'blue', label = 'Rel. Frequency')
    plt.title('Monte Carlo Simulation\n Simulated Distribution')
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
    #print(info.to_string())
