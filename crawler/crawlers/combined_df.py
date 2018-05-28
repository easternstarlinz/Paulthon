import pickle

import sys
sys.path.append('/home/paul/Paulthon')

from utility.general import tprint, merge_dfs_horizontally, append_dfs_vertically, to_pickle_and_CSV


calls = pickle.load(open('calls.pkl', 'rb'))
puts = pickle.load(open('puts.pkl', 'rb'))
print('************')
print(calls)
print(puts)

reidx_cols = ['Delta_C', 'Delta_P', 'IV_C', 'IV_P']
combined_df = merge_dfs_horizontally([calls, puts], suffixes=('_C', '_P')).loc[:, reidx_cols].round(2)
#combined_df = combined_df.apply(lambda x: float(x))
print(combined_df)




"""
# Greeks df
df = pickle.load(open('greeks_df.pkl', 'rb'))

# Unaffected df
print('---------***-------')
print(df)

# Transform 'Strike' values to floats
df.index = df.index.astype(float)
print('---------***-------')
print(df)

# Transform 'Delta' values to floats
deltas = df['Delta'].tolist()
deltas = [float(i) for i in deltas]
df['Delta'] = deltas
print('---------***-------')
print(df)

# Transform 'IV' values to floats
vols = df['IV'].tolist()
vols = [float(i[:-1])/100 for i in vols]
df['IV'] = vols
print('---------***-------')
print(df)
"""
if __name__ == '__main__':
    pass
