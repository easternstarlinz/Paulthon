import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd

import sys
sys.path.append('/home/paul/Paulthon')
from utility.general import dict_of_lists_to_unique_list

# Symbol Exclude Framework
excludes = {    
                'General'           :['BRK.B', 'BKNG', 'BHF', 'BF.B', 'CBRE', 'FTV', 'UA', 'WELL', 'XRX' 'BHH', 'AEE'],
                'Healthcare'        :['AAAP', 'BOLD', 'LNTH', 'MEDP', 'TCMD'],
                'Questionable'      :['EVRG']
           }


excludes = dict_of_lists_to_unique_list(excludes)

def scrub_symbol_excludes(symbols: 'iterable of symbols'):
    """If the list of symbols contains any excludes, eliminate the excludes from the list.
       In addition, eliminate duplicates and sort the list of symbols alphabetically."""
    return sorted(list(set([sym for sym in symbols if sym not in excludes])))


# Right now, my list of symbols comes from a Zachs Excel file
# Zach's Information Table
info = pd.read_csv('/home/paul/Paulthon/DataFiles/SectorInfo/stock_screen.csv').set_index('Ticker').rename(columns = {'Market Cap ': 'Market Cap', 'Last Close': 'Price'})

# Get list of sectors and industries
sectors = sorted(list(set(info.loc[:, 'Sector'])))
industries = sorted(list(set(info.loc[:, 'Industry'])))
industries = [i.split(' - ')[0] for i in industries]

# SP500 Symbols; Scraped from Wikipedia
sp500_symbols = pd.read_html('https://en.wikipedia.org/wiki/List_of_S&P_500_companies')[0][0][1:].reset_index(drop=True).tolist()

# Healthcare Symbols
healthcare_symbols = info[(info.Sector == 'Medical') & (info['Market Cap'] > 100) & (info['Price'] > 3.00)].index.tolist()

# Zachs Symbols
zachs_symbols = info.index.tolist()


symbols = {     'SP500'             :sp500_symbols,
                'Healthcare'        :healthcare_symbols,
                'Index'             :['SPY', 'IWM', 'QQQ', 'IBB', 'XBI']
                #'Zachs'             :zachs_symbols
          }

# In the symbols dictionary, scrub symbol excludes for each list
for key in symbols.keys():
    symbols[key] = scrub_symbol_excludes(symbols[key])

all_symbols = dict_of_lists_to_unique_list(symbols)
