import logging

_filters = []

def filter(func):
    def newfunc(cal):
        log = logging.getLogger('filter:' + func.__name__)
        return func(cal, log=log)
    _filters.append(newfunc)
    return newfunc
