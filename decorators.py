from functools import wraps
import inspect
import time
import cProfile
import pstats
import io

def my_time_decorator(original_function):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = original_function(*args, **kwargs)
        t2 = time.time()
        diff = round(t2 - t1, 4)
        print("{}-> Time (secs): {}".format(original_function.__name__, diff))
        return result
    return wrapper

#Decorator that automatically assigns the parameters in the init function
#def initializer(func):

def empty_decorator(func):
    return func

def profile(fnc):
    """A decorator that uses CProfile to profile a function"""

    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s=io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval
    
    return inner

def initializer(func):
    names, varargs, keywords, defaults = inspect.getargspec(func)
    
    @wraps(func)
    def wrapper(self, *args, **kargs):
        for name, arg in list(zip(names[1:], args)) + list(kargs.items()):
            setattr(self, name, arg)
        
        for name, default in zip(reversed(names), reversed(defaults)):
                if not hasattr(self, name):
                    setattr(self, name, default)
        func(self, *args, **kargs)
        
    return wrapper
