import datetime as dt
import pandas as pd
import math
import numpy as np
import random
import copy
import pylab
from collections import namedtuple
from paul_resources import InformationTable, tprint, rprint, get_histogram_from_array
from utility.decorators import my_time_decorator
from Distribution_Module import Distribution, float_to_event_distribution, float_to_bs_distribution
from Option_Module import Option, OptionPrice, OptionPriceMC, get_implied_volatility
from Event_Module import IdiosyncraticVol, Event, SysEvt_PresElection, TakeoutEvent, Earnings
from functools import reduce


#----------------------------------------------Module Tests---------------------------------------------------#
"""
    -timing_test_for_distribution_addition
    -timing_test_for_mc_simulation_by_iteration_size
    -timing_test_for_distribution_addition_2
    -run_takeout_by_expiry
    -systematic_params_for_all_symbols
"""
@my_time_decorator
def timing_test_for_distribution_addition_2():
    # Define Events
    event1 = TakeoutEvent('CLVS', 1)
    event2 = SysEvt_PresElection('CLVS', .2)
    event3 = Earnings('CLVS', .2, 'Q2_2018')
    event4 = Earnings('CLVS', .005, 'Q3_2018')
    event5 = Earnings('CLVS', .3, 'Q4_2018')

    expiry = dt.date(2018, 5, 1)
    events = [event2, event3]
    added_distribution = event1.get_distribution(expiry)
    for event in events:
        added_distribution += event.get_distribution()
    rprint(added_distribution.mean_move)

timing_test_for_distribution_addition_2()

def timing_test_for_mc_simulation_by_iteration_size():
    event = SystematicEvent('CLVS', .00, 'Ph3_Data')
    distribution = evet.get_distribution()
    pct_moves = distribution.distribution_df.loc[:, 'Pct_Move'].values.tolist()
    weights = distribution.distribution_df.loc[:, 'Prob'].values.tolist()
    
    @my_time_decorator
    def mini_run(k):
        pct_moves = event1.get_distribution().distribution_df.loc[:, 'Pct_Move'].values.tolist()
        weights = evet1.get_distribution().distribution_df.loc[:, 'Prob'].values.tolist()
        results = random.choices(pct_moves, weights=weights, k=k)
        return results1

    results1 = mini_run(10**1)
    results2 = mini_run(10**2)
    results3 = mini_run(10**3)
    results4 = mini_run(10**4)
    results5 = mini_run(10**5)
    results6 = mini_run(10**6)
    results6 = mini_run(10**7)
    #results6 = mini_run(10**8)

@my_time_decorator
def timing_test_for_distribution_addition():
    expiry = dt.date(2018, 5, 1)
    event1 = TakeoutEvent('CLVS', 1)
    event2 = SysEvt_PresElection('CLVS', .02)
    event3 = SystematicEvent('CLVS', .1, 'Ph3_Data')
    event4 = SystematicEvent('CLVS', .05, 'Investor_Day')
    event5 = SystematicEvent('CLVS', .3, 'FDA Approval')

    distribution1 = event1.get_distribution(expiry)
    distribution2 = event2.get_distribution()
    distribution3 = event3.get_distribution()
    distribution4 = event4.get_distribution()
    distribution5 = event5.get_distribution()

    added_distribution = distribution1 + distribution2 + distribution3 + distribution4 + distribution5
    print(added_distribution)
    print(added_distribution.distribution_df)
    rprint(distribution1.mean_move, distribution2.mean_move, distribution3.mean_move, distribution4.mean_move, distribution5.mean_move, added_distribution.mean_move)



@my_time_decorator
def run_takeout_by_expiry():
    event = TakeoutEvent('NBIX', 1)
    option_type = 'Call'
    option_type_2 = 'Put'
    strike = 1.0
    expiries = [dt.date(2018, 4, 20), dt.date(2018, 7, 20), dt.date(2018, 10, 20), dt.date(2019, 1, 20), dt.date(2019, 4, 20)]

    # Preliminary Print Statements
    print("Ann. Takeout Prob: {:.1f}%, Premium: {:.1f}%".format(event.takeout_prob*100, event.takeout_premium*100))

    for expiry in expiries:
        option = Option(option_type, strike, expiry)
        option2 = Option(option_type_2, strike, expiry)

        distribution = event.get_distribution(expiry)

        price = OptionPrice(distribution, option)
        price2 = OptionPrice(distribution, option2)
        
        straddle = price + price2
        print("T.O. by {:%m/%d/%Y}: {:.1f}%".format(expiry, distribution.distribution_df.loc["Takeout", "Prob"]*100), "\n"*0)
        print("Mean Move: {:.1f}%".format(distribution.mean_move*100))
        print("Straddle: {:.1f}%".format(straddle*100), "\n"*1)


def systematic_params_for_all_symbols():
    if __name__ == "__main__":
        #-------------------PresElection Setup-----------------#
        PresElectionParams = pd.read_csv("/home/paul/Environments/finance_env/PresElectionParams.csv")
        PresElectionParams.set_index('Stock', inplace=True)

        # Create PresElection Events Dict
        PresElection_Evts = {}
        for stock, move_input in PresElectionParams.itertuples():
            PresElection_Evts[stock] = SysEvt_PresElection(stock, move_input)

        #-------------------Takeout Setup-----------------#
        TakeoutParams = pd.read_csv("TakeoutParams.csv")
        TakeoutParams.set_index('Stock', inplace=True)

        # Create Takeout Events Dict
        Takeout_Evts = {}
        for stock, bucket in TakeoutParams.itertuples():
            Takeout_Evts[stock] = TakeoutEvent(stock, bucket)

        takeout_dict = {}
        for stock, event in Takeout_Evts.items():
            takeout_dict[stock] = (event.takeout_prob, event.takeout_premium)

        takeout_df = pd.DataFrame(takeout_dict).T.round(3)
        takeout_df.rename(columns = {0: 'Prob', 1: 'Premium'}, inplace=True)
        takeout_df.rename_axis('Stock', inplace=True)
        
        
        evt = SystematicEvent('ZFGN', .20)
        evt2 = Event()
        evt3 = SysEvt_PresElection('GM', .05)
        evt4 = TakeoutEvent('NBIX', 1)
        
        print("\n\n\nAll Events---\n", Event.instances, "\n")
        print("Systematic Event---\n", SystematicEvent.instances, "\n")
        print("Presidential Election---\n", SysEvt_PresElection.instances,"\n")
        print("Takeout Event---\n", TakeoutEvent.instances,"\n")
        print(takeout_df.sort_values('Premium', ascending=False))
