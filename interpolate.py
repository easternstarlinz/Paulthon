from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, num=25, endpoint=True)
y = np.cos(-x**2/9.0)
f = interp1d(x,y)
f2 = interp1d(x, y, kind='cubic')

xnew = np.linspace(0, 10, num=100, endpoint=True)
plt.plot(x, y, 'o')
plt.plot(xnew, f(xnew), '-')
plt.plot(xnew, f2(xnew), '--')

x2 = np.linspace(0,10, num=100, endpoint=True)
y2 = np.cos(-x2**2/9.0)
plt.plot(x2, y2, 'b')

plt.legend(['Data', 'Linear', 'Cubic', 'Data2'], loc='best')
plt.show()
