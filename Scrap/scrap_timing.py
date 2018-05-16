import datetime as dt

date = dt.datetime(2018, 6, 1)
print(isinstance(date, (dt.date, dt.datetime)))

string = date.strftime('YYYY-MM-DD')
string = date.strftime('yyyy-mm-dd')
string = date.strftime('%Y-%m-%d')
print(string)
print(type(string))
date = dt.datetime.strptime(string,'%Y-%m-%d').date()
print(date, type(date))
