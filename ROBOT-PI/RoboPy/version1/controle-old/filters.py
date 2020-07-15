import numpy

class Filter(object):
    def __init__(self, maxsize, filtering_function):
        self.values = []
        self.maxsize = maxsize
        self.filtering_function = filtering_function

    def add_value(self, value):
        if(len(self.values) == self.maxize):
            self.values.pop(0)
        self.values.append(value)
        
    def get_value(self):
        if(len(self.values) == self.maxize):
            return self.filtering_function(self.values)
        else:
            return self.values[-1]
        
def MedianFilter(maxsize):
    return Filter(maxsize, numpy.median)
