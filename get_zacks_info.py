import pandas as pd
from pprint import pprint

info = pd.read_csv('stock_screen.csv')
info.set_index('Ticker', inplace=True)
print(info.columns.tolist())

sectors = sorted(list(set(info.loc[:, 'Sector'])))
industries = sorted(list(set(info.loc[:, 'Industry'])))
print(sectors)
industries = [i.split(' - ')[0] for i in industries]
pprint(sorted(list(set(industries))))
symbols = info[info.Sector == 'Medical'].index.tolist()
print(symbols)
print(len(symbols))
