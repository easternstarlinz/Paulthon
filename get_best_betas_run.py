from beta_class import Beta
from get_best_betas_2 import get_betas_multiple_indices, find_best_index, get_betas_multiple_stocks, find_best_index_multiple_stocks

beta = Beta('PFE', 'QQQ')
beta.show_scrub_trajectory()

stock = 'NBIX'
indices = ['XBI', 'IBB', 'SPY', 'QQQ']
betas = get_betas_multiple_indices(stock, indices)
print(betas.to_string())
best_index = find_best_index(stock, indices)
print('Best Index: ', best_index)

stocks = ['NBIX', 'ALNY', 'PFE', 'CRBP']
index = 'IBB'
betas = get_betas_multiple_stocks(stocks, index)
print('Hello World!')
print(betas.to_string())

best_betas_df = find_best_index_multiple_stocks(stocks, indices)
print(best_betas_df.to_string())

