import sqlite3
import pandas as pd
import datetime as dt
from datetime import timedelta
from employee import Employee
from Event_Module import Earnings
import random
from paul_resources import HealthcareSymbols

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



stocks = ['AAPL', 'FB', 'AMZN']
stocks = HealthcareSymbols
earnings_evts = create_earnings_events(stocks)

for evt in earnings_evts:
    insert_earnings_event(evt)

earnings_all = get_all_earnings_events()
print(earnings_all)

"""
earns_q2 = Earnings('CLVS', .05, dt.date(2018, 5, 15), 'Q2_2018')
earns_q3 = Earnings('CLVS', .05, dt.date(2018, 8, 15), 'Q3_2018')
earns_q4 = Earnings('CLVS', .05, dt.date(2018, 11, 15), 'Q4_2018')

print(earns_q2.event_name, type(earns_q2.event_name))
print(earns_q2.event_input, type(earns_q2.event_input))
print(earns_q2.event_input_value, type(earns_q2.event_input_value))

insert_earnings_event(earns_q2)
insert_earnings_event(earns_q3)
insert_earnings_event(earns_q3)
"""

"""
earns_evts = []
for earns in earnings_all:
    earns_evt = Earnings(earns[0],
                          earns[1],
                          dt.datetime.strptime(earns[2], '%Y-%m-%d').date(),
                          earns[3])
    for i in earns:
        print(i, type(i))
    earns_evts.append(earns_evt)

print('HELLO JANE', earns_evts)
for earns in earns_evts:
    print(earns.timing_descriptor)
"""

"""
emps = get_emps_by_name('Doe')
print(emps)

update_pay(emp_2, 95000)
remove_emp(emp_1)

emps = get_emps_by_name('Doe')
print(emps)
"""

earnings_table = pd.read_sql_query("SELECT * FROM earnings", conn)
#print('HELLO SAMMY', list(earnings_table.itertuples())[0][1])
print(earnings_table)

conn.close()
