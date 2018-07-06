#!/usr/bin/env python 
"""
Retrieve intraday stock data from Google Finance.
"""
import sys
import csv
import datetime
import re

import pandas as pd
import requests

def get_google_finance_intraday(ticker, exchange, period=60, days=1):
    """
    Retrieve intraday stock data from Google Finance.
    Parameters
    ----------
    ticker : str
        Company ticker symbol
    exchange : str
        Exchange of ticker
    period : int
        Interval between stock values in seconds.
    days : int
        Number of days of data to retrieve.
    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the opening price, high price, low price,
        closing price, and volume. The index contains the times associated with
        the retrieved price values.
    """

    uri = 'https://www.google.com/finance/getprices' \
          '?i={period}&p={days}d&f=d,o,h,l,c,v&q={ticker}&x={exchange}'.format(ticker=ticker,
                                                                          period=period,
                                                                          days=days,
                                                                          exchange=exchange)
    page = requests.get(uri)
    reader = csv.reader(page.content.splitlines())
    columns = ['Close', 'High', 'Low', 'Open', 'Volume']
    rows = []
    times = []
    for row in reader:
        if re.match('^[a\d]', row[0]):
            if row[0].startswith('a'):
                start = datetime.datetime.fromtimestamp(int(row[0][1:]))
                times.append(start)
            else:
                times.append(start+datetime.timedelta(seconds=period*int(row[0])))
            rows.append(map(float, row[1:]))
    if len(rows):
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'),
                            columns=columns)
    else:
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("\nUsage: google_financial_intraday.py EXCHANGE SYMBOL\n\n")
    else:
        exchange = sys.argv[1]
        ticker = sys.argv[2]
        print("--------------------------------------------------")
        print("Processing %s" % ticker)
        print(get_google_finance_intraday(ticker,exchange,60,2))
        print("--------------------------------------------------")
