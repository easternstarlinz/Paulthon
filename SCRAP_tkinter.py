import pandas as pd
import numpy as np

import sys 
from tkinter import * 

dates = pd.date_range('20160101', periods=6)
df = pd.DataFrame(np.random.randn(6,4),index=dates,columns=list('ABCD'))

root = Tk() 

t1 = Text(root) 
t1.pack() 

class PrintToT1(object): 
    def write(self, s):
        t1.insert(END, s) 

sys.stdout = PrintToT1() 

print ('Hello, world!') 
print (df)

mainloop()
