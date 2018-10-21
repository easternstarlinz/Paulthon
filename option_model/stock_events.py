import pandas as pd
import datetime as dt

# Paul Modules
from option_model.Event_Module import Event, ComplexEvent
from option_model.Distribution_Module import Distribution, Distribution_MultiIndex


analyst_day = Event('NBIX', .075, dt.date(2018, 12, 1), 'Analyst Day')

ingrezza_info = pd.read_csv('/Users/paulwainer/Paulthon/Events/Parameters/CLVS.csv')
ingrezza_data = Event('NBIX', Distribution(ingrezza_info), 'Q4_2018', 'Ingrezza Data')

elagolix_info = pd.read_excel('/Users/paulwainer/Paulthon/Events/Parameters/CLVS_RiskScenarios2.xlsx',
                                 header = [0],
                                 index_col = [0,1],
                                 sheet_name = 'Sub_States')

elagolix_approval = ComplexEvent('NBIX', Distribution_MultiIndex(
    elagolix_info), dt.date(2018, 11, 15), 'Elagolix Approval')


all_other_events = [analyst_day, ingrezza_data, elagolix_approval]
