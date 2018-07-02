import pandas as pd
import datetime as dt

# Paul Modules
from Event_Module import IdiosyncraticVol, TakeoutEvent, Earnings, Event, ComplexEvent, SysEvt_PresElection
from Distribution_Module import Distribution, Distribution_MultiIndex


elagolix_info = pd.read_excel('/home/paul/Paulthon/Events/Parameters/CLVS_RiskScenarios2.xlsx',
                                 header = [0],
                                 index_col = [0,1],
                                 sheet_name = 'Sub_States')

analyst_day = Event('NBIX', .075, dt.date(2018, 10, 8), 'Analyst Day')
ingrezza_data = Event('NBIX', Distribution(pd.read_csv('/home/paul/Paulthon/Events/Parameters/CLVS.csv')), 'Q4_2018', 'Ingrezza Data')
elagolix_approval = ComplexEvent('NBIX', Distribution_MultiIndex(elagolix_info), dt.date(2018,6,20), 'Elagolix Approval')
all_other_events = [analyst_day, ingrezza_data, elagolix_approval]
    
