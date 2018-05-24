import pickle

import sys
sys.path.append('/home/paul/Paulthon')

from utility.general import tprint, merge_dfs_horizontally, to_pickle_and_CSV

base = pickle.load(open('base.pkl', 'rb'))
greeks = pickle.load(open('greeks.pkl', 'rb'))
greeks = greeks[:-1]
greeks_index = greeks.index.tolist()
greeks_index = [float(i) for i in greeks_index]
greeks.index = greeks_index
print(base)
print(greeks)

combined_df = merge_dfs_horizontally([base, greeks])
print(combined_df)


if __name__ == '__main__':
    base_index = base.index.tolist()
    greeks_index = greeks.index.tolist()[:-1]
    print(base_index)
    print(greeks_index)
    greeks_index = [float(i) for i in greeks_index]
    print(base_index == greeks_index)
    print(base_index)
    print(greeks_index)
