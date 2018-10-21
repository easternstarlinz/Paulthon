import datetime as dt
import pandas as pd
import math
import numpy as np
import random
from collections import namedtuple
from paul_resources import InformationTable, tprint, rprint
from decorators import my_time_decorator
from biotech_class_7 import Option, OptionPrice, Distribution, Event, SystematicEvent, SysEvt_PresElection, TakeoutEvent, graph_MC_distribution
"""--------------------------Calculations----------------------------------------"""
@my_time_decorator
def run4():
    expiry = dt.date(2018, 5, 1)
    mc_iterations = 10**4
    
    # Define Events
    event1 = TakeoutEvent('CLVS', 7)
    event2 = SysEvt_PresElection('CLVS', .00)
    event3 = SystematicEvent('CLVS', .00, 'Ph3_Data')
    event4 = SystematicEvent('CLVS', .00, 'Investor_Day')
    event5 = SystematicEvent('CLVS', .3, 'FDA_Approval')
    event6 = SystematicEvent('CLVS', .00, 'Q1_Earnings')
    event7 = SystematicEvent('CLVS', .00, 'Q2_Earnings')
    
    distribution1 = event1.get_distribution(expiry)
    distribution2 = event2.get_distribution()
    distribution3 = event3.get_distribution()
    distribution4 = event4.get_distribution()
    distribution5 = event5.get_distribution()
    distribution6 = event6.get_distribution()
    distribution7 = event7.get_distribution()
    
    events = [event1, event2, event3, event4, event5, event6, event7]
    mc_simulation_total = np.zeros(mc_iterations)
    for event in events:
        distribution = event.get_distribution(expiry)
        mc_simulation = distribution.mc_simulation(mc_iterations)
        mc_simulation_total += mc_simulation
    
    graph_MC_distribution(mc_simulation_total)

    simulation1 = distribution1.mc_simulation(mc_iterations)
    simulation2 = distribution2.mc_simulation(mc_iterations)
    simulation3 = distribution3.mc_simulation(mc_iterations)
    simulation4 = distribution4.mc_simulation(mc_iterations)
    simulation5 = distribution5.mc_simulation(mc_iterations)
    simulation6 = distribution6.mc_simulation(mc_iterations)
    simulation7 = distribution7.mc_simulation(mc_iterations)
    simulation8 = distribution7.mc_simulation(mc_iterations)

    @my_time_decorator
    def run_simulation():
        simulation_total = simulation1 + simulation2 + simulation3 + simulation4 + simulation5 + simulation6 + simulation7 + simulation8 + simulation8 + simulation8 + simulation8
        return simulation_total
    results = run_simulation()

    graph_MC_distribution(results)

    pct_moves1 = distribution1.distribution_df.loc[:, 'Pct_Move'].values.tolist()
    pct_moves2 = distribution2.distribution_df.loc[:, 'Pct_Move'].values.tolist()

    weights1 = distribution1.distribution_df.loc[:, 'Prob'].values.tolist()
    weights2 = distribution2.distribution_df.loc[:, 'Prob'].values.tolist()
    print(pct_moves1)
    print(pct_moves2)
    
    @my_time_decorator
    def mini_run(k):
        results1 = random.choices(pct_moves1, weights=weights1, k=k)
        return results1

    results1 = mini_run(10**1)
    results2 = mini_run(10**2)
    results3 = mini_run(10**3)
    results4 = mini_run(10**4)
    results5 = mini_run(10**5)
    results6 = mini_run(10**6)
    results6 = mini_run(10**7)
    #results6 = mini_run(10**8)
    print(results1)

run4()

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

@my_time_decorator
def run2():
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
def run3():
    # Define Events
    event1 = TakeoutEvent('CLVS', 1)
    event2 = SysEvt_PresElection('CLVS', .02)
    event3 = SystematicEvent('CLVS', .1, 'Ph3_Data')
    event4 = SystematicEvent('CLVS', .05, 'Investor_Day')
    event5 = SystematicEvent('CLVS', .3, 'FDA_Approval')
    event6 = SystematicEvent('CLVS', .05, 'Q1_Earnings')
    event7 = SystematicEvent('CLVS', .05, 'Q2_Earnings')

    expiry = dt.date(2018, 5, 1)
    events = [event2, event3, event4]
    added_distribution = event1.get_distribution(expiry)
    for event in events:
        added_distribution += event.get_distribution()
    rprint(added_distribution.mean_move)


def run():
    if __name__ == "__main__":
        #-------------------PresElection Setup-----------------#
        PresElectionParams = pd.read_csv("/Users/paulwainer/Environments/finance_env/PresElectionParams.csv")
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
