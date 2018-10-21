from data.finance import PriceTable
from utility.finance import get_total_return
print(PriceTable)

total_return = get_total_return('NBIX', lookback=252)
print('Total Return: ', total_return) 
