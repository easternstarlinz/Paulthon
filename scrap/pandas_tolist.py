import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import pylab

PriceTable = pickle.load(open('sp500_price_table.pkl', 'rb'))
PriceTable.index = pd.to_datetime(PriceTable.index)
stocks = PriceTable.columns.values.tolist()
stocks = [i for i in stocks if i not in  {'BHH', 'CBRE', 'WELL', 'BKNG', 'BHF', 'FTV', 'UA'}]
PriceTable = PriceTable.loc[:, stocks]

InformationTable = pd.read_csv('information_table.csv')
InformationTable.rename(columns = {'Last Close': 'Price', 'Ticker': 'Stock', 'Market Cap ': 'Market Cap'}, inplace=True)
InformationTable.set_index('Stock', inplace=True)

info = pd.read_csv('stock_screen.csv').set_index('Ticker')
print(info)
HealthcareSymbols = info[info.Sector == 'Medical'].index.tolist()

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

def get_histogram_from_array(results: 'array of numbers'):
    #start, end, interval = -.5, .5, .025
    #bins = np.arange(start - interval/2, end + interval/2, interval)
    
    bins=100
    plt.hist(results, bins, histtype='bar', rwidth=1.0, color = 'blue', label = 'Rel. Frequency')
    plt.title('Monte Carlo Simulation\n Simulated Distribution')
    plt.xlabel('Relative Price')
    plt.ylabel('Relative Frequency')
    plt.legend()
    plt.show()

def show_mc_distributions_as_line_chart(mc_distributions):
    i = 1
    for mc_distribution in mc_distributions:
        y, binEdges = np.histogram(mc_distribution, bins=np.arange(.5, 1.75, .025))
        bincenters = .5*(binEdges[1:] + binEdges[:-1])
        pylab.plot(bincenters, y, '-', label = "Events {}".format(i))
        i += 1
    pylab.legend()
    pylab.show()


class Aaron(object):
    pass

if __name__ == "__main__":
    print(PriceTable.index.values)
    print(PriceTable.index)
    print(type(PriceTable.index.values))
    print(type(PriceTable.index))
    print(PriceTable.index.values.tolist())
    print(PriceTable.index.tolist())
    print(type(PriceTable.index.values.tolist()[0]))
    print(type(PriceTable.index.tolist()[0]))
    
    tprint(InformationTable.columns)
