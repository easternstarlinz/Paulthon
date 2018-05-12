import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as spo
import math
import sympy as sym
from Stock_Module import Stock
from decorators import my_time_decorator

def f(X):
    """Given a scalar X, return some value (a real number)."""
    Y = (X - 1.5)**2 + 0.5
    print("X = {}, Y = {}".format(X, Y)) # for tracking
    return Y

def test_run(function, Xguess):
    #Xguess = 2.0
    min_result = spo.minimize(function, Xguess, method='SLSQP', options={'disp':True})
    print("Minima found at:")
    print("X = {}, Y = {}".format(min_result.x, min_result.fun))

    # Plot function values, mark minima
    Xplot = np.linspace(0.5, 2.5, 21)
    Yplot = f(Xplot)
    plt.plot(Xplot, Yplot)
    plt.plot(min_result.x, min_result.fun, 'ro')
    plt.title("Minima of an objective function")
    plt.show()

def f2(X):
    """Given a scalar X, return some value (a real number)."""
    Y = (X - 1.5)**4 + 0.5
    print("X = {}, Y = {}".format(X, Y)) # for tracking
    return Y

def f3(X):
    """Given a scalar X, return some value (a real number)."""
    Y = .7*math.log(1-X) + .2*math.log(1 + 10*X) + .1*math.log(1 + 30*X)
    #print("X = {:.4f}, Y = {:.4f}".format(X, Y)) # for tracking
    return Y

@my_time_decorator
def find_maximum(f: 'function', Xguess, increment = .001):
    Y = f(Xguess)
    Xhigher, Xlower = Xguess + increment, Xguess - increment
    pair = (Xhigher, Xlower)

    def advance(Xguess, increment = increment):
        Xhigher, Xlower = Xguess + increment, Xguess - increment
        Yhigher, Ylower = f(Xhigher), f(Xlower)
        Ywinner = max(Yhigher, Ylower)
        #print('YWinner: {:.4f}'.format(Ywinner)) 
        if Ywinner == Yhigher:
            Xwinner = Xhigher
        else:
            Xwinner = Xlower
        #print('XWinner: {:.4f}'.format(Xwinner)) 
        return Xwinner
    new_estimate = advance(Xguess)
    
    iterations = int(1 / increment)
    print('Iterations:', iterations)
    for i in range(iterations*2):
        new_estimate = advance(new_estimate)
        #print(new_estimate)
    return new_estimate

#elagolix = ComplexEvent('CLVS', Distribution_MultiIndex(elagolix_info), dt.date(2018,6,1), 'Elagolix Approval')
event = Stock.elagolix
df = event.event_input_distribution_df
probs = df.loc[:, 'Prob'].tolist()
pct_moves = df.loc[:, 'Pct_Move'].tolist()
max_loss = pct_moves[-1]
#max_loss = -1
#pct_moves = [pct_move/-max_loss for pct_move in pct_moves]

def f4(X, probs=probs, pct_moves=pct_moves):
    a, b, c, d, e = probs
    A, B, C, D, E = pct_moves
    
    #print('Probs:', a, b, c, d, e)
    #print('Pct_Moves:', A, B, C, D, E)
    #print(X) 
    Y = a*math.log(1+A*X) + b*math.log(1+B*X) + c*math.log(1+C*X) + d*math.log(1+D*X) + e*math.log(1+E*X)
    return Y

def f5(X = None, probs=probs, pct_moves=pct_moves):
    if X is None:
        X = sym.symbols('X')
    
    Y = 0
    for a, A in zip(probs, pct_moves):
        expression = a*sym.log(1+A*X)
        Y += expression
    return Y

value = f5(.25)
print(value)

capital_allocation = 100*10**6
portfolio_max_drawdown_percent =.05
portfolio_max_drawdown = portfolio_max_drawdown_percent*capital_allocation

optimal_size = find_maximum(f5, .5, .001)
#capital_deployed = maximum*(1/-max_loss)
capital_deployed = optimal_size
max_drawdown = max_loss*capital_deployed

optimal_size_dollars = optimal_size*portfolio_max_drawdown
optimal_size_percent_of_capital = optimal_size_dollars / capital_allocation
max_drawdown_dollars = max_loss*optimal_size_dollars
max_drawdown_percent_of_capital = max_drawdown_dollars / capital_allocation
print('Optimal Size (% of Risk Dollars): {:.2f}'.format(optimal_size))
print('Capital_Deployed (% of Risk Dollars): {:.2f}'.format(capital_deployed))
print('Max Drawdown (% of Risk Dollars): {:.2f}'.format(max_drawdown))
print('\n-------Sizing ($) for $100mm Portoflio; 5.0% Drawdown Limit-------')
print('Optimal Size ($): ${:,.0f}'.format(optimal_size_dollars))
print('Max Expcted Loss ($): ${:,.0f}'.format(max_drawdown_dollars))
print('% of Capital Deployed: {:.2f}%'.format(optimal_size_percent_of_capital*100))
print('Max Exp. Drawdown (% of Capital): {:.2f}%'.format(max_drawdown_percent_of_capital*100))


if __name__ == '__main__':
    #f3(.25)
    #test_run(f3, 2.0)

    #maximum = find_maximum(f3, .15, .0001)
    #print(maximum)
    pass
