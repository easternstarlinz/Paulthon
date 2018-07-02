import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as spo
import math
import datetime as dt
from statistics import mean
import sympy as sym
from Stock_Module import Stock
from utility.decorators import my_time_decorator
from CreateMC import get_total_mc_distribution_from_events
from Event_Module import IdiosyncraticVol
from Distribution_Module import Distribution, mc_distribution_to_distribution
from Option_Module import get_time_to_expiry

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
def find_maximum(f: 'function', Xguess, increment = .001, print_guesses=False):
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
        if print_guesses is True:
            print('XWinner: {:.4f}'.format(Xwinner)) 
        return Xwinner
    new_estimate = advance(Xguess)
    
    iterations = int(1 / increment)*5
    print('Optimizer Iterations:', iterations)
    estimates = [Xguess]
    for i in range(iterations):
        new_estimate = advance(new_estimate)
        estimates.append(new_estimate)
        #print(estimates)
        if i >2:
            #print(new_estimate, estimates[i-1])
            #if new_estimate == estimates[i-2]:
            if math.isclose(new_estimate, estimates[i-1], abs_tol=1e-5):
                return new_estimate
        #print(new_estimate)
    return new_estimate


# Declare Expiry
expiry = dt.date(2018, 12, 20)

# Declare Events
event = Stock.elagolix
vol = IdiosyncraticVol('NBIX', .30)

# Create distribution_df for the Combined Event
df = event.event_input_distribution_df
mc_dist = get_total_mc_distribution_from_events([event, vol], expiry=expiry)
mc_distribution_to_distribution(mc_dist, bins=10**2+1, to_file=True, file_name='Elagolix_Dist')
combined_dist = Distribution(pd.read_csv('Elagolix_Dist.csv'))
df = combined_dist.distribution_df
#print(df.to_string())

#----------------Print Statements------------------------------------#
print('MC Iterations: {:,.0f}, Mean: {:.2f}'.format(len(mc_dist), np.mean(mc_dist)))
print("Combined Dist. Average Move: {:.2f}".format(combined_dist.average_move))
print("Combined Dist. Mean Sqrt Move: {:.2f}".format(combined_dist.mean_move))


# Source Probs, Pct_Moves, Max_Loss for the Combined Event
probs = df.loc[:, 'Prob'].tolist()
pct_moves = df.loc[:, 'Pct_Move'].tolist()
max_loss = min(pct_moves)


event_pct_moves = event.event_input_distribution_df.loc[:, 'Pct_Move'].tolist()
print(event_pct_moves)
max_loss_event_only = min(event_pct_moves)
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

#-----------------------------Portfolio Parameters-------------------------------#
capital_allocation = 100*10**6
portfolio_max_drawdown_percent =.05
portfolio_max_drawdown = portfolio_max_drawdown_percent*capital_allocation

time_to_expiry = get_time_to_expiry(expiry)
Xguess = min(max(.1, 4-4*5*time_to_expiry), .9)
Xguess =.6
print('Xguess: {:.2f}'.format(Xguess))
optimal_size = find_maximum(f5, Xguess, .01, print_guesses=True)
#capital_deployed = maximum*(1/-max_loss)
capital_deployed = optimal_size
max_drawdown = max_loss*capital_deployed
max_drawdown_event_only = max_loss_event_only*capital_deployed

optimal_size_dollars = optimal_size*portfolio_max_drawdown
optimal_size_percent_of_capital = optimal_size_dollars / capital_allocation
max_drawdown_dollars = max_loss*optimal_size_dollars
max_drawdown_event_only_dollars = max_loss_event_only*optimal_size_dollars
max_drawdown_percent_of_capital = max_drawdown_dollars / capital_allocation
max_drawdown_percent_of_portfolio_max_drawdown = max_drawdown_dollars / portfolio_max_drawdown
max_drawdown_event_only_percent_of_portfolio_max_drawdown = max_drawdown_event_only_dollars / portfolio_max_drawdown
print('Optimal Size (% of Risk Dollars): {:.2f}'.format(optimal_size))
print('Capital_Deployed (% of Risk Dollars): {:.2f}'.format(capital_deployed))
print('Max Drawdown (% of Risk Dollars): {:.2f}'.format(max_drawdown))
print('\n-------Sizing ($) for $100mm Portoflio; 5.0% Drawdown Limit-------')
print('Optimal Size ($): ${:,.0f}'.format(optimal_size_dollars))
print('Max Expcted Loss ($): ${:,.0f}'.format(max_drawdown_dollars))
print('% of Capital Deployed: {:.2f}%'.format(optimal_size_percent_of_capital*100))
print('Max Exp. Drawdown (% of Capital): {:.2f}%'.format(max_drawdown_percent_of_capital*100))
print('Max Exp. Drawdown (% of Portfolio Max Drawdown): {:.2f}%'.format(max_drawdown_percent_of_portfolio_max_drawdown*100))
print('Max Exp. Drawdown - Event Only (% of Portfolio Max Drawdown): {:.2f}%'.format(max_drawdown_event_only_percent_of_portfolio_max_drawdown*100))


if __name__ == '__main__':
    #f3(.25)
    #test_run(f3, 2.0)

    #maximum = find_maximum(f3, .15, .0001)
    #print(maximum)
    pass
