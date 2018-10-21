get_sp500_prices.py: Fetches closing prices for a list of symbols using Yahoo Data Reader.

Module: Stock_Module
Description: This is the highest-level module and contains the Stock class
Methods:
    Risk Metrics:
    - best_index (index with the highest R-squared, taken from a pre-made table)
    - beta_to_best_index
    - beta_to_SPY
    - get_beta_to_index (takes the index of interest as a paramters and performs beta_value calculations)
    
    Stock Events:
    - idio_vol
    - earnings_events
    - takeout_event
    - other_events
    - events_cache (work-in-progress)
    - events (list of all events particular to the Stock instance)
    - sorted_events (events sorted based on center date)
    - get_event_timeline (image showing timeline of events)

    Volatility Calculations:
    - expiries (exchange-listed expiries)
    - strikes (specification of strikes; in final product, strikes will vary by expiry)
    - get_term_structure
    - get_call_prices
    - get_vol_surface
    - get_option_sheet
    - get_vol_surface_spline
    - get_implied_vol
    - get_option_price

Module: CreateMC (future name: mc_distribution_functionality?)
    """This module contains functionality to create the MC Distribution for a given expiry based on the events"""
    - filter_events_before_expiry
    - sum_mc_distributions (multiplicative combination of individual distributions)
    - get_total_mc_distribution_from_events 

M


Package: Utility
Module: Decorators
Functions:
    - my_time_decorator
    - empty_decorator

Module: General
Functions:
    - tprint
    - rprint
    - setup_standard_logger
    - merge_dfs_horizontally

Module: Graphing
Functions:
    - get_histogram_from_array


Package: Data
Module: Finance
Data:
    -InformationTable



Module: biotech_class_run
    Functions
    -get_option_sheet_from_mc_distribution
    -get_vol_surface
    -get_vol_surface_from_event_grouping
    -get_vol_surface_spline

    Data
    -EarningsDist
    -IdiosyncraticVolDist
    -Information Table

