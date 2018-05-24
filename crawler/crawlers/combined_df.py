import pickle

import sys
sys.path.append('/home/paul/Paulthon')

from utility.general import tprint, merge_dfs_horizontally, append_dfs_vertically, to_pickle_and_CSV

calls = pickle.load(open('calls.pkl', 'rb'))
puts = pickle.load(open('puts.pkl', 'rb'))

calls_index = calls.index.tolist()
puts_index = puts.index.tolist()


print(calls_index)
print(puts_index)

reidx_cols = ['Delta_C', 'Delta_P', 'IV_C', 'IV_P']
combined_df = merge_dfs_horizontally([calls, puts], suffixes=('_C', '_P')).loc[:, reidx_cols].round(2)
#combined_df = combined_df.apply(lambda x: float(x))
print(combined_df)

deltas = combined_df['Delta_C'].tolist()
print(deltas)
print(type(deltas[0]))
deltas = [float(i) for i in deltas]
print(deltas)
print(type(deltas[0]))

vols = combined_df['IV_C'].tolist()
vols = [float(i[:-1])/100 for i in vols]
combined_df['IV_C'] = vols
print(vols)
print(combined_df)


if __name__ == '__main__':
    pass
