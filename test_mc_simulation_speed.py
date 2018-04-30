from Event_Module import Earnings
import datetime as dt
from decorators import my_time_decorator

event = Earnings('CRBP', .075, 'Q2_2018')

distribution = event.get_distribution(dt.date(2018, 5, 20))

@my_time_decorator
def get_simulation_results(mc_iterations):
    return distribution.mc_simulation(mc_iterations)

simulation_results = list(get_simulation_results(10**7))
print(type(simulation_results), len(simulation_results))

@my_time_decorator
def list_of_list(my_list):
    return list(my_list)

list_of_list(simulation_results)
