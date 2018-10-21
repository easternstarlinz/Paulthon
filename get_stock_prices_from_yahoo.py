import datetime as dt
import pandas as pd
import pickle
import logging

import pandas_datareader.data as web

from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

# Paul Utils
from utility.decorators import my_time_decorator
from utility.general import to_pickle_and_CSV, merge_dfs_horizontally, outer_join_dfs_horizontally

# Finance Data
from data.symbols import symbols, all_symbols

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
    1) Get historical data for multiple stocks from Yahoo Finance
        --make_price_table(symbols,start,end)
--------------------------------------------------------------------
"""
def orient_price_table(df):
    """Make sure that the price table is ordered with the first row being the most recent date down to the last row which is the oldest date"""
    first_row_index = df.head(1).index.item()
    last_row_index = df.tail(1).index.item()
    
    print(first_row_index, last_row_index)

    if first_row_index > last_row_index:
        return df
    else:
        return df[::-1]

@my_time_decorator
def make_price_table(symbols: 'list',
                     start = dt.datetime(2016,1,1),
                     end = dt.datetime.today(),
                     file_name = 'default'):
    """Get prices from Yahoo's website for multiple symbols"""
    query_attempts = {}
    data_points = {}
    failed_symbols = []
    
    def get_prices(symbol, start, end):
        #print("{}: Start: {}, End:{}".format(symbol, start, end))
        try:
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
                        query_attempts[symbol] = count
                else:    
                    logger.info("{}: Attempts: {}".format(symbol, count))
                    query_attempts[symbol] = count
                    
                    price_table = df.loc[:, ['adjclose']].rename(columns = {'adjclose' : symbol})
                    
                    data_points[symbol] = price_table.shape[0]
                    return price_table
        except Exception:
            print("Fetch Yahoo prices reached the general Exception clause")
            return None
    
    pool = ThreadPool(4)
    price_tables = pool.map(lambda stock: get_prices(stock, start, end), symbols)

    print('Query Attempts: ', query_attempts)
    print('Data Points: ', data_points)
    print('Failed Symbols: ', failed_symbols, end= '\n')
    #price_table = merge_dfs_horizontally(price_tables)
    price_table = outer_join_dfs_horizontally(price_tables)
    price_table = orient_price_table(price_table)

    to_pickle_and_CSV(price_table, file_name)
    return price_table


#---------------------------------------------------------------------------------------
def test_yahoo_reader():
    symbol = 'A'
    start = dt.datetime(2015, 1, 1)
    end = dt.datetime.today()
    return web.get_data_yahoo(symbol, start, end).round(2)

@my_time_decorator
def fetch_price_table():
    #symbols = indices
    #symbols = ['XBI', 'IBB', 'SPY', 'QQQ', 'SRPT', 'CRBP', 'NBIX', 'BIIB', 'ALNY', 'PFE']
    #symbols = ['AAAP', 'XBI', 'NBIX']
    #symbols = ['MCRB', 'JNCE', 'CBRE']
    #symbols = ['XBI', 'IBB']
    symbols = all_symbols
    
    #from data.finance import PriceTable as previous_price_table
    #symbols = ['XBI']

    file_name = '/Users/paulwainer/Paulthon/DataFiles/StockPrices/stock_prices'
    
    price_table = make_price_table(symbols,
                                   start = dt.datetime(2014,1,1),
                                   end = dt.datetime.today(),
                                   file_name = file_name)
   
    #price_table = outer_join_dfs_horizontally([previous_price_table, price_table])

    to_pickle_and_CSV(price_table, file_name)
    return price_table

if __name__ == '__main__':
    price_table = fetch_price_table()
    print(price_table)
