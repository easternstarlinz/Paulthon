import datetime as dt
import numpy as np
import pandas as pd
import pickle
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')
from bs4 import BeautifulSoup
import sklearn
from time_decorator import my_time_decorator
from paul_resources import HealthcareSymbols, PriceTable
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('yahoo_reader.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

"""
--------------------------------------------------------------------
The functions in this module are web scraping functions.
    1) Pull S&P 500 symbols from Wikipedia (and create pickle file).
        --get_sp500_symbols_from_wiki()    

    2) Get historical data for a single stock from Yahoo Finance
        --get_prices(symbol, start, end)

    3) Get historical data for multiple stocks from Yahoo Finance
        --make_price_table(symbols,start,end)

    4) Make pickle file for stock prices for a single symbol
        --pickle_prices(symbol, start, end)
--------------------------------------------------------------------
"""

def get_sp500_symbols_from_wiki():
    """Pull S&P 500 Symbols from Wikipedia (with the ability to add discretionary symbols)"""
    # Pull symbols from Wikipedia table
    sp500_symbols = pd.read_html('https://en.wikipedia.org/wiki/List_of_S&P_500_companies')[0][0][1:].reset_index(drop=True).tolist()
    discretionary_symbols = ['SPY', 'IWM', 'QQQ', 'IBB', 'XBI', 'XLP', 'XRT'] + HealthcareSymbols
    all_symbols = list(set(sp500_symbols, discretionary_symbols))
    sp500_symbols = pd.Series(all_symbols).sort_values().reset_index(drop=True)
    
    # Save to CSV
    sp500_symbols.to_csv('sp500_symbols.csv')

    # Save to Pickle
    pickle_file = open('sp500_symbols.pkl', 'wb')
    pickle.dump(sp500_symbols, pickle_file, pickle.HIGHEST_PROTOCOL)
    pickle_file.close()

    return sp500_symbols.values.tolist()
    

@my_time_decorator
def make_price_table(symbols: 'list',
                     start = dt.datetime(2016,1,1),
                     end = dt.datetime.today(),
                     file_name = 'default'):
    """Get prices from Yahoo's website for multiple symbols"""
    query_attempts = []
    failed_symbols = []
    
    def get_prices(symbol, start, end):
        #print("{}: Start: {}, End:{}".format(symbol, start, end))
        print(symbol)
        count = 1
        while count < 10:
            print(count)
            try:
                df = web.get_data_yahoo(symbol, start, end).set_index('date').round(2)
            except Exception:
                count += 1
                if count == 9:
                    logger.error("{} failed the query".format(symbol))
                    failed_symbols.append(symbol)
                    query_attempts.append(count)
            else:    
                logger.info("{}: Attempts: {}".format(symbol, count))
                query_attempts.append(count)
                return df.loc[:, ['adjclose']].rename(columns = {'adjclose' : symbol})
    
    price_table = get_prices(symbols[0], start, end)
    for symbol in symbols[1:]:
        try:
            price_table = price_table.join(get_prices(symbol, start, end))
        except Exception:
            pass
    
    print(query_attempts, failed_symbols, price_table, end= '\n')
    
    # Save Price Table and Query Details to CSV file
    price_table.to_csv(file_name + '.csv')
    #query_attempts.to_csv(str(file_name) + '_query_attempts.csv')
    #failed_symbols.to_csv(str(file_name) + '_failed_symbols.csv')

    # Save Price Table to Pickle File
    pickle_file = open(str(file_name) + '_price_table.pkl', 'wb')
    pickle.dump(price_table, pickle_file, pickle.HIGHEST_PROTOCOL)
    pickle_file.close()

    return(price_table)

def pickle_prices(symbol, start, end):
    """Download stock prices from Yahoo for one symbol to pickle file"""
    df = web.DataReader(symbol, 'yahoo', start, end).round(2)
    prices = df['Adj Close']
    pickle_file = open(str(symbol) + '_pickle_file.pkl', 'wb')
    pickle.dump(prices, pickle_file, pickle.HIGHEST_PROTOCOL)
    pickle_file.close()

#---------------------------------------------------------------------------------------
def test_yahoo_reader():
    symbol = 'A'
    start = dt.datetime(2016, 1, 1)
    end = dt.datetime.today()
    return web.get_data_yahoo(symbol, start, end).round(2)

if __name__ == '__main__':
    #symbols = get_sp500_symbols_from_wiki()
    symbols = ['XLV', 'XLF', 'XLE', 'AMLP', 'VFH', 'GDX', 'XLU']
    price_table = make_price_table(symbols,
            start = dt.datetime(2016,1,1),
                                   end = dt.datetime.today(),
                                   file_name='sp500_3')
    original_price_table = PriceTable
    new_price_table = pd.merge(original_price_table, price_table, left_index=True, right_index=True)
    
    pickle_file = open(str('sp500_3') + '_price_table.pkl', 'wb')
    pickle.dump(new_price_table, pickle_file, pickle.HIGHEST_PROTOCOL)
    pickle_file.close()
