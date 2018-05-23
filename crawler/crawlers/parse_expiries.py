with open('expiries.txt', 'r') as f:
    string = f.read()
    expiries = string.strip().split()
    print(expiries)
