from py_vollib.black_scholes.implied_volatility import black_scholes, implied_volatility
from decorators import my_time_decorator

print("No Import Error")

S = 100
K = 100
sigma = .20
r = .01
flag = 'c'
t = .5
@my_time_decorator
def black_scholes_run(iterations):
    for i in range(iterations):
        price = black_scholes(flag, S, K, t, r, sigma)
        iv = implied_volatility(price, S, K, t, r, flag)
    return (price, iv)

result = black_scholes_run(10**5)

print(result)

