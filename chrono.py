import time


def chrono(func):
    """ Displays the time spent in the function """
    def wrapper(*args, **kwargs):
        start = time.time()
        ret = func(*args, **kwargs)
        print("Executed '{}' in {:.2f}s.".format(
            func.__name__, time.time() - start))
        return ret
    return wrapper
