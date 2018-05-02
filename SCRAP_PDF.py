from Distribution_Module import float_to_volbeta_distribution
from paul_resources import show_mc_distributions_as_line_chart
import numpy as np
from scipy.interpolate import interp1d, UnivariateSpline, InterpolatedUnivariateSpline
import matplotlib.pyplot as plt
from decorators import my_time_decorator
from statistics import mean
import pandas as pd
import datetime as dt
from Option_Module import Option, OptionPriceMC

mc_iterations = 10**1
dist = float_to_volbeta_distribution(.10)
mc_distribution = dist.mc_simulation(mc_iterations)
mc_distribution = np.array(mc_distribution)

#show_mc_distributions_as_line_chart([mc_distribution])

#@my_time_decorator
def get_spline_from_mc_simulation(mc_distribution):
    #min_cutoff = np.percentile(mc_distribution, 0)
    #max_cutoff = np.percentile(mc_distribution, 100)
    #mc_distribution = [i for i in mc_distribution if (i > min_cutoff) and (i < max_cutoff)]
    
    bin_min = np.percentile(mc_distribution, .25)
    bin_max = np.percentile(mc_distribution, 99.75)
    y, binEdges = np.histogram(mc_distribution, bins=np.arange(bin_min, bin_max, .01))
    
    bincenters = .5*(binEdges[1:] + binEdges[:-1])
    
    xnew = np.linspace(bin_min+.01, bin_max-.01, num=10**3, endpoint=True)
    
    #@my_time_decorator
    def get_spline():
        return InterpolatedUnivariateSpline(bincenters, y, k=1)
        return interp1d(bincenters, y, kind='cubic')
    
    spline = get_spline()
    
    return spline

bin_min = np.percentile(mc_distribution, .25)
bin_max = np.percentile(mc_distribution, 99.75)
strikes = pd.Series(np.arange(bin_min, bin_max, .01))

def plot_histogram(strikes):
    plt.plot(strikes, spline(strikes))

@my_time_decorator
def get_call_prices_via_spline(strikes, mc_distribution):
    spline = get_spline_from_mc_simulation(mc_distribution)
    total_area = spline.integral(bin_min, bin_max)

    #@my_time_decorator
    def get_call_price(strike):
        
        #@my_time_decorator
        def get_prob_above_strike(strike):
            return spline.integral(strike, 10) / total_area
        
        #@my_time_decorator
        def get_average_stock_price_above_strike(strike):
            return np.mean(mc_distribution[mc_distribution > strike])
            return mean([i for i in mc_distribution if i > strike])
        
        #@my_time_decorator
        def get_average_call_value_above_strike(strike):
            return average_stock_price_above_strike - strike

        prob_above_strike = get_prob_above_strike(strike)
        average_stock_price_above_strike = get_average_stock_price_above_strike(strike)
        average_call_value_above_strike = get_average_call_value_above_strike(strike)
        
        """ 
        prob_above_strike = spline.integral(strike, 1000) / total_area
        average_stock_price_above_strike = mean([i for i in mc_distribution if i > strike])
        average_call_value_above_strike = average_stock_price_above_strike - strike
        """

        #print('Strike: {:.2f}, Prob Above Strike: {:.2f}'.format(strike, prob_above_strike))
        #print('Strike: {:.2f}, Avg. Stock Price: {:.2f}'.format(strike, average_stock_price_above_strike))
        return prob_above_strike * average_call_value_above_strike
    
    @my_time_decorator 
    def get_call_prices(strikes):
        return  strikes.apply(get_call_price)
    
    return get_call_prices(strikes)

@my_time_decorator
def establish_call_options(expiry, strikes):
    #return [Option('Call', strike, expiry) for strike in strikes]
    Option_Map = lambda strike: Option('Call', strike, expiry)
    return strikes.apply(Option_Map)

@my_time_decorator
def get_call_prices(call_options, mc_distribution):
    #return list(map(lambda option: OptionPriceMC(option, mc_distribution), call_options))
    OptionPriceMC_Map = lambda option: OptionPriceMC(option, mc_distribution)
    return call_options.apply(OptionPriceMC_Map)

# Spline Method
spline = get_spline_from_mc_simulation(mc_distribution)
call_prices_spline = get_call_prices_via_spline(strikes, mc_distribution)

# Standard Method
call_options = establish_call_options(dt.date(2018,6,1), strikes)
call_prices_standard = get_call_prices(call_options, mc_distribution)

#print(len(call_prices_spline), len(call_prices_standard))
#print(type(call_prices_spline), type(call_prices_standard))

# Compare Prices Between Both Methods
#compare_call_prices = pd.concat([strikes, call_prices_spline, call_prices_standard], axis=1)
#print(compare_call_prices)
