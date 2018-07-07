from data.symbols import all_symbols

excludes = {    
                'General'           :['BRK.B', 'BKNG', 'BHF', 'BF.B', 'CBRE', 'FTV', 'UA', 'WELL', 'XRX' 'BHH', 'AEE'],
                'Healthcare'        :['AAAP', 'BOLD', 'LNTH', 'MEDP', 'TCMD'],
           }

please = ('XBI' in all_symbols)

from data.finance import PriceTable
print(PriceTable.loc[:, ['XBI']])

from utility.finance import get_stock_prices, get_daily_returns
stock_prices = get_stock_prices('NBIX', lookback=252)
print(stock_prices)
daily_returns = get_daily_returns('NBIX', lookback=252)
print(daily_returns)

print(sorted(PriceTable.columns.tolist()))

from scrubbing_processes import get_scrub_params

scrub_params = get_scrub_params('NBIX', 'XBI')
print(scrub_params)

def func1():
    func2()

def func2():
    print('Hi')

func1()
