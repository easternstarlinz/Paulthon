import datetime as dt
import pandas as pd
import pickle
import logging

import pandas_datareader.data as web

from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

# Paul Utils
from utility.decorators import my_time_decorator
from utility.general import to_pickle_and_CSV
#from ETFs import indices

# Finance Data
from data.finance import AllSymbols

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
                        query_attempts.append(count)
                else:    
                    logger.info("{}: Attempts: {}".format(symbol, count))
                    query_attempts.append(count)
                    return df.loc[:, ['adjclose']].rename(columns = {'adjclose' : symbol})
        except Exception:
            return None
    
    pool = ThreadPool(4)
    price_tables = pool.map(lambda stock: get_prices(stock, start, end), symbols)
    
    #shapes = sorted([(df.columns.values.tolist(), df.shape) for df in price_tables], key=lambda x: x[1][0])
    #print(shapes)
    price_table = pd.concat(price_tables, axis=1)
    
    to_pickle_and_CSV(price_table, file_name)
    print(query_attempts, failed_symbols, price_table, end= '\n')
    return price_table

#---------------------------------------------------------------------------------------
def test_yahoo_reader():
    symbol = 'A'
    start = dt.datetime(2016, 1, 1)
    end = dt.datetime.today()
    return web.get_data_yahoo(symbol, start, end).round(2)

@my_time_decorator
def fetch_price_table():
    if __name__ == '__main__':
        #symbols = indices
        symbols = ['XBI', 'IBB', 'SPY', 'QQQ', 'SRPT', 'CRBP', 'NBIX', 'BIIB', 'ALNY', 'PFE']
        symbols = AllSymbols
        symbols = ['AAAP', 'XBI']
        file_name = '/home/paul/Paulthon/DataFiles/StockPrices/sp500_prices_paul'
        price_table = make_price_table(symbols,
                                       start = dt.datetime(2015,1,1),
                                       end = dt.datetime.today(),
                                       file_name = file_name)
       
        to_pickle_and_CSV(price_table, file_name)

fetch_price_table()
