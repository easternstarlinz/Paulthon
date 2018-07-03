# Standard Packages
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as spo
import math
import sympy as sym

# Paul Utils
from utility.decorators import my_time_decorator

def kelly_criterion(probs, pct_moves, X=None):
    if X is None:
        X = sym.symbols('X')
    
    Y = 0
    for a, A in zip(probs, pct_moves):
        expression = a*sym.log(1+A*X)
        Y += expression
    return Y

@my_time_decorator
def find_maximum(f: 'function', Xguess, increment = .001, print_guesses=False, **kwargs):
    Y = f(X=Xguess, **kwargs)
    Xhigher, Xlower = Xguess + increment, Xguess - increment
    pair = (Xhigher, Xlower)

    def advance(Xguess, increment=increment, **kwargs):
        Xhigher, Xlower = Xguess + increment, Xguess - increment
        Yhigher, Ylower = f(X=Xhigher, **kwargs), f(X=Xlower, **kwargs)
        Ywinner = max(Yhigher, Ylower)
        #print('YWinner: {:.4f}'.format(Ywinner)) 
        if Ywinner == Yhigher:
            Xwinner = Xhigher
        else:
            Xwinner = Xlower
        if print_guesses is True:
            print('XWinner: {:.4f}'.format(Xwinner)) 
        return Xwinner
    new_estimate = advance(Xguess, **kwargs)
    
    iterations = int(1 / increment)*50
    print('Optimizer Iterations:', iterations)
    estimates = [Xguess]
    for i in range(iterations):
        new_estimate = advance(new_estimate, increment=increment, **kwargs)
        estimates.append(new_estimate)
        #print(estimates)
        if i >2:
            #print(new_estimate, estimates[i-1])
            #if new_estimate == estimates[i-2]:
            if math.isclose(new_estimate, estimates[i-1], abs_tol=1e-5):
                return new_estimate
            max_loss = min(kwargs['pct_moves'])
            max_loss_risked = new_estimate*max_loss
            print(new_estimate, max_loss, max_loss_risked)
            #if max_loss_risked > .9:
            #if new_estimate > .9:
            #    return new_estimate
        #print(new_estimate)
    return new_estimate

def find_minimum(function, Xguess):
    """I currently don't use this formula anywhere"""
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
