import datetime as dt
import pandas as pd
import pickle

"""
Symbols:
    Symbol Excludes
    Symbols
    SP500Symbols
    HealthcareSymbols

Prices
    PriceTable
    ETF_PriceTable

SectorInfo
    InformationTable
        
Betas
    SPY_Betas_Raw
    SPY_Betas_Scrubbed
    Best_Betas

Distributions
    VolBeta

EventParams
    TakeoutParams

Distributions
    VolBeta
"""

# Symbols Excludes
GeneralExcludes = {'BRK.B', 'BKNG', 'BHF', 'BF.B', 'CBRE', 'FTV', 'UA', 'WELL', 'XRX' 'BHH', 'AEE'}
HealthcareExcludes = {'AAAP', 'BOLD', 'LNTH', 'MEDP', 'TCMD'}
ManualExcludes = set.intersection(GeneralExcludes, HealthcareExcludes)


# Prices
PriceTable = pickle.load(open('/home/paul/Paulthon/DataFiles/StockPrices/sp500_prices_paul.pkl', 'rb'))
PriceTable.index = pd.to_datetime(PriceTable.index)
stocks = PriceTable.columns.values.tolist()
AutomaticExcludes = {i for i in stocks if PriceTable.loc[:, i].isnull().values.any()}
SymbolExcludes = set.intersection(ManualExcludes, AutomaticExcludes)

stocks = [i for i in stocks if i not in SymbolExcludes]
PriceTable = PriceTable.loc[:, stocks][::-1]

ETF_PriceTable = pickle.load(open('/home/paul/Paulthon/DataFiles/StockPrices/ETF_prices.pkl', 'rb'))
ETF_PriceTable.index = pd.to_datetime(ETF_PriceTable.index)

# Temporary Fix to use ETF_PriceTable in the Beta Module
#PriceTable = ETF_PriceTable


# Sector Info
InformationTable = pd.read_csv('/home/paul/Paulthon/DataFiles/SectorInfo/information_table.csv')
InformationTable.rename(columns = {'Last Close': 'Price', 'Ticker': 'Stock', 'Market Cap ': 'Market Cap'}, inplace=True)
InformationTable.set_index('Stock', inplace=True)

# Zach's Information Table
info = pd.read_csv('/home/paul/Paulthon/DataFiles/SectorInfo/stock_screen.csv').set_index('Ticker').rename(columns = {'Market Cap ': 'Market Cap', 'Last Close': 'Price'})

# Get list of sectors and industries
sectors = sorted(list(set(info.loc[:, 'Sector'])))
industries = sorted(list(set(info.loc[:, 'Industry'])))
industries = [i.split(' - ')[0] for i in industries]

# Get list of symbols
HealthcareSymbols = info[(info.Sector == 'Medical') & (info['Market Cap'] > 100) & (info['Price'] > 3.00)].index.tolist()
HealthcareSymbols = [i for i in HealthcareSymbols if i not in SymbolExcludes]

Symbols = info.index.tolist()
SP500Symbols = pd.read_html('https://en.wikipedia.org/wiki/List_of_S&P_500_companies')[0][0][1:].reset_index(drop=True).tolist()
SP500Symbols = sorted([sym for sym in SP500Symbols if sym not in SymbolExcludes])

AllSymbols = set(HealthcareSymbols).union(set(SP500Symbols))
print(AllSymbols)


# Distributions
VolBeta = pd.read_csv('/home/paul/Paulthon/Events/Distributions/VolbetaDistribution.csv')
#EarningsEvents = pickle.load(open('EarningsEvents.pkl', 'rb')) # Can't include here because of circular imports.


# Event Params
TakeoutParams = pd.read_csv('/home/paul/Paulthon/Events/Parameters/TakeoutParams.csv').set_index('Stock')
TakeoutBuckets = pd.read_csv('/home/paul/Paulthon/Events/Parameters/TakeoutBuckets.csv').set_index('Rank')


# Betas
BestBetas = pickle.load(open('/home/paul/Paulthon/DataFiles/Betas/best_betas.pkl', 'rb'))
Best_Betas = pickle.load(open('/home/paul/Paulthon/DataFiles/Betas/Best_Betas.pkl', 'rb'))
SPY_Betas_Raw = pickle.load(open('/home/paul/Paulthon/DataFiles/Betas/SPY_Betas_Raw.pkl', 'rb'))
SPY_Betas_Scrubbed = pickle.load(open('/home/paul/Paulthon/DataFiles/Betas/SPY_Betas_Scrubbed.pkl', 'rb'))
ETF_Betas_to_SPY = pickle.load(open('/home/paul/Paulthon/DataFiles/Betas/ETF_betas.pkl', 'rb'))
