import datetime as dt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d, UnivariateSpline, InterpolatedUnivariateSpline
import matplotlib.pyplot as plt
from utility.decorators import my_time_decorator
from statistics import mean
from Option_Module import Option, OptionPriceMC
from Distribution_Module import float_to_volbeta_distribution
from paul_resources import show_mc_distributions_as_line_chart

mc_iterations = 10**4
dist = float_to_volbeta_distribution(.10)
dist_df = dist.distribution_df

mc_distribution = dist.mc_simulation(mc_iterations)
mc_distribution = np.array(mc_distribution)


prices = dist_df.loc[:, 'Relative_Price'].values.tolist()
probs = dist_df.loc[:, 'Prob'].values.tolist()
#prices = np.array(prices)
#probs = np.array(probs)

plt.scatter(prices, probs)
#plt.show()

bin_min = np.percentile(mc_distribution, .25)
bin_max = np.percentile(mc_distribution, 99.75)
strikes = pd.Series(np.arange(bin_min, bin_max, .01))

@my_time_decorator
def get_call_price_from_df(strike):
    dist_df = dist.distribution_df
    dist_df = dist_df[dist_df.loc[:, 'Relative_Price'] > strike]
    dist_df['Weighted_Call_Value'] = (dist_df['Relative_Price'] - strike) * dist_df.loc[:, 'Prob']
    return dist_df.loc[:, 'Weighted_Call_Value'].sum()
    return sum([state.Prob*max((state.Relative_Price - strike), 0) for state in dist_df.itertuples()])

call_price = get_call_price_from_df(1.0)

tuples = list(zip(probs, prices))
DistTupes = zip(probs, prices)
#@my_time_decorator
def get_call_price_simple(strike, DistTupes = DistTupes):
    """tup[0] is state Prob, tup[1] is state Price"""
    in_the_money_calls = [tup for tup in DistTupes if tup[1] > strike]
    return sum([tup[0]*(tup[1]-strike) for tup in in_the_money_calls])

@my_time_decorator
def get_call_prices_simple(strikes, DistTupes):
    return strikes.apply(get_call_price_simple)

call_prices = get_call_prices_simple(strikes, DistTupes)

"""        
# Potentially apply this structure? This code is unrelated.
tuples = pd.concat([prob, prices], axis=1).loc[:, [0,1]].apply(tuple, axis=1)
Map = lambda tup: (tup[0], tup[1])
call_IVs = tuples.apply(IV_Map)
"""

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
        
        @my_time_decorator
        def get_average_stock_price_above_strike(strike):
            
            @my_time_decorator
            def my_filter(mc_distribution):
                #return mc_distribution
                return mc_distribution[mc_distribution > strike]
            
            @my_time_decorator
            def take_mean(mc_distribution):
                return np.mean(mc_distribution)
            
            @my_time_decorator
            def take_average(mc_distribution):
                return np.average(mc_distribution)
            
            @my_time_decorator
            def take_sum(mc_distribution):
                return np.sum(mc_distribution)
            
            filtered = my_filter(mc_distribution)
            my_mean = take_mean(mc_distribution)
            my_average = take_average(mc_distribution)
            my_sum = take_sum(mc_distribution)

            return my_mean
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
#call_prices_spline = get_call_prices_via_spline(strikes, mc_distribution)

# Standard Method
call_options = establish_call_options(dt.date(2018,6,1), strikes)
call_prices_standard = get_call_prices(call_options, mc_distribution)

#print(len(call_prices_spline), len(call_prices_standard))
#print(type(call_prices_spline), type(call_prices_standard))

# Compare Prices Between Both Methods
#compare_call_prices = pd.concat([strikes, call_prices_spline, call_prices_standard], axis=1)
#print(compare_call_prices)
