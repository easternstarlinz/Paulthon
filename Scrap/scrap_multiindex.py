import pandas as pd
import datetime as dt
from Distribution_Module_2 import float_to_volbeta_distribution
info = {'Strike': [.9, 1.0, 1.1],
        'Price': [.25, .30, .35],
        'IV': [.25, .30, .35]}

df = pd.DataFrame(info).set_index('Strike')
df.name = 'SRPT'

iterables = [['SRPT'], ['Strike', 'Price', 'IV']]
index = pd.MultiIndex.from_product(iterables, names = ['Stock', 'Option_Info'])

info = [[.9, 1.0, 1.1, 1.2, 1.3],
        [.2, .175, .15, .125, .1],
        [.25, .30, .35, .4, .45]]

info = [[.9, .2, .25],
        [1.0, .175, .30],
        [1.1, .15, .35],
        [1.25, .125, .40],
        [1.3, .1, .45]]


df = pd.DataFrame(info, columns = index)
df.name = 'SRPT'
pd.set_option('display.multi_sparse', False)

iterables = [['SRPT'], ['Strike', 'Price', 'IV']]
index = pd.MultiIndex.from_product(iterables, names = ['Stock', 'Option_Info'])

info = [[.2, .25],
        [.175, .30],
        [.15, .35],
        [.125, .40],
        [.1, .45]]

# Column indices
expiry = dt.date(2018, 5, 20)
iterables = [['SRPT'], [expiry], ['Price', 'IV']]
index_c = pd.MultiIndex.from_product(iterables, names = ['Stock', 'Expiry', 'Option_Info'])

# Row indices
strikes = [.9, 1.0, 1.1, 1.2, 1.3]
index_r = pd.Index(strikes, name = 'Strike')

df = pd.DataFrame(info, index = index_r, columns = index_c)
#pd.set_option('display.multi_sparse', False)
my_slice = df.loc[:,[('SRPT', expiry, 'IV')]]

dist = float_to_volbeta_distribution(.3)
print(dist.average_move, dist.mean_move, dist.straddle)
dist.get_histogram()
