import numpy as np
from pysabr import sabr, black

[k, f, t, v, r, cp] = [.012, .013, 10., .020, .02, 'call']

value = black.lognormal_call(k, f, t, v, r, cp)
print(value)
