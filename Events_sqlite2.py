import sqlite3
import pandas as pd
import datetime as dt
from datetime import timedelta
from employee import Employee
from Event_Module import Earnings
import random
from paul_resources import HealthcareSymbols, Symbols
from decorators import my_time_decorator

#conn = sqlite3.connect('employee.db')
conn = sqlite3.connect(':memory:')

c = conn.cursor()


c.execute("""CREATE TABLE earnings (
            stock text,
            event_input real,
            timing_descriptor text,
            event_name text
            )""")

def insert_earnings_event(earns):
    with conn:
        c.execute("INSERT INTO earnings VALUES (:stock, :event_input, :timing_descriptor, :event_name)",
                {'stock': earns.stock,
                 'event_input': earns.event_input_value,
                 'timing_descriptor': earns.timing_descriptor.strftime('%Y-%m-%d'),
                 'event_name': earns.event_name})


def get_all_earnings_events():
    c.execute("SELECT * FROM earnings")
    return c.fetchall()


def get_earnings_table():
    return pd.read_sql_query("SELECT * FROM earnings", conn)

def get_earnings_events():
    earns_evts = []
    for earns in get_earnings_table().itertuples():
        earns_evt = Earnings(earns.stock,
                              earns.event_input,
                              dt.datetime.strptime(earns.timing_descriptor, '%Y-%m-%d').date(),
                              earns.event_name)
        earns_evts.append(earns_evt)
    return earns_evts

def get_emps_by_name(lastname):
    c.execute("SELECT * FROM employees WHERE last=:last", {'last': lastname})
    return c.fetchall()

def update_pay(emp, pay):
    with conn:
        c.execute("""UPDATE employees SET pay = :pay
                    WHERE first = :first AND last = :last""",
                    {'first': emp.first, 'last': emp.last, 'pay': pay})
def remove_emp(emp):
    with conn:
        c.execute("DELETE from employees WHERE first = :first AND last = :last",
                    {'first': emp.first, 'last': emp.last})

def create_earnings_events(stocks: 'list of stocks'):
    """Create Earnings Events for a List of Stocks"""
    event_names = ['Q1_2018', 'Q2_2018', 'Q3_2018', 'Q4_2018']
    q1_date_range = list(pd.date_range(dt.date(2018, 1, 1), dt.date(2018, 3, 30)))
    
    earnings_events = []
    for stock in stocks:
        # Set Event Input
        event_input = random.uniform(.03, .07)
        
        # Set Earnings Dates
        q1_date = random.choice(q1_date_range)
        timing_descriptors = [q1_date,
                              q1_date + timedelta(90),
                              q1_date + timedelta(180),
                              q1_date + timedelta(270)]

        # Instantiate Earnings Events and append to main list
        for i in range(4):
            earnings_evt = Earnings(stock,
                                    event_input,
                                    timing_descriptors[i],
                                    event_names[i])
            
            earnings_events.append(earnings_evt)
   
    return earnings_events

@my_time_decorator
def create_earnings_database():
    stocks = ['AAPL', 'FB', 'AMZN']
    stocks = HealthcareSymbols
    stocks = Symbols
    earnings_evts = create_earnings_events(stocks)
    
    return earnings_evts

@my_time_decorator
def get_specific_symbol(symbol, earnings_evts):
    return [evt for evt in earnings_evts if evt.stock == symbol]


#for evt in earnings_evts:
#    insert_earnings_event(evt)

#earnings_evts = get_earnings_events()
#print(earnings_evts)

#earnings_table = get_earnings_table()
#print(earnings_table)

#print(stocks, len(stocks))

events = create_earnings_database()

events_CLVS = get_specific_symbol('CLVS', events)

print(events_CLVS)
"""
emps = get_emps_by_name('Doe')
print(emps)

update_pay(emp_2, 95000)
remove_emp(emp_1)

emps = get_emps_by_name('Doe')
print(emps)
"""
conn.close()
