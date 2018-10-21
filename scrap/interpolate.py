from scipy.interpolate import interp1d
import numpy as np
from option_model.Distribution_Module import float_to_volbeta_distribution

x = np.linspace(0, 10, num=10000, endpoint=True)
y = np.sin(np.cos(-x**2/9.0)) + x**.3 - np.cos(x*10)**2
f = interp1d(x,y)
f2 = interp1d(x, y, kind='cubic')

xnew = np.linspace(0, 10, num=10000, endpoint=True)
#plt.plot(x, y, '-')
#plt.plot(xnew, f(xnew), '-')
#plt.plot(xnew, f2(xnew), '-')

#x2 = np.linspace(0,10, num=100, endpoint=True)
#y2 = np.cos(-x2**2/9.0)
#plt.plot(x2, y2, 'b')

#plt.legend(['Data', 'Linear', 'Cubic'], loc='best')
#plt.show()

dist = float_to_volbeta_distribution(.05)
dist.get_histogram(10**4)
