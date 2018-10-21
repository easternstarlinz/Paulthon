import itertools
import inspect
from data.symbols import symbols

from beta_model.get_best_betas_2 import get_betas_over_iterable
import matplotlib.pyplot as plt
from pandas.tools.plotting import table

stock = ['NBIX']
index = ['SPY', 'QQQ', 'XBI', 'IBB']
lookback = [252]

stock = ['NBIX', 'CRBP', 'PFE', 'MRK']
index = ['XBI']
lookback = [200]

stock = ['KMB']
index = ['SPY']
lookback = [100, 200, 300, 400, 500]

stock = symbols['SP500'][0:10]
index = ['SPY']
lookback = [252]


combos = itertools.product(stock, index, lookback)

betas_df = get_betas_over_iterable(stock, index, lookback)
print(betas_df.round(3).to_string())
print(betas_df.describe().round(3).to_string())

ax = plt.subplot(111, frame_on=False)
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
table(ax, betas_df)
plt.savefig('betas.png')


def my_func(stock, index, lookback):
    _, _, _, params = inspect.getargvalues(inspect.currentframe())
    print(params)

#my_func(stock, index, lookback)

