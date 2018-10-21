import datetime as dt
import pandas as pd
import math
import numpy as np
import random
import copy
import matplotlib.pyplot as plt
from collections import namedtuple
from statistics import mean
from paul_resources import InformationTable, tprint, rprint
from decorators import my_time_decorator
from py_vollib.black_scholes.implied_volatility import black_scholes, implied_volatility

"""ALL OF THE CONTENT HERE HAS BEEN DISTRIBUTED TO OTHER MODULES: Option_Module, Event_Module, Distribution_Module"""

"""
-OptionPriceDist
    -Type: Function
    -Params:
        -Option: 'NamedTuple'
        -Distribution: 'Object'
    -Returns->
        -Content: Option Price 
        -Type: Float
"""


"""
-Option: NamedTuple
    -Params:
        -Option_Type: 'str'
        -Strike: 'float'
        -Expiry: 'Datetime'

-OptionPriceDist: Function
    -Params:
        -Option: 'NamedTuple'
        -Distribution: 'Object'
    -Returns->
        -'Float'
        -Content: Option Price 


#Distribution(distrubtions: 'list of independent distributions')
#Price(Option, Distribution)
"""


"""
Types of Distributions:
    --DataFrame of ('Prob', 'Price)
    --MonteCarlo Distribution
    --DataFrame with Residual Volatilities
"""

