import numpy

class Filter(object):
    def __init__(self, maxsize, filtering_function):
        self.values = []
        self.maxsize = maxsize
        self.filtering_function = filtering_function

    def add_value(self, value):
        if(len(self.values) == self.maxsize):
            self.values.pop(0)
        self.values.append(value)
        
    def get_value(self):
        if(len(self.values) == self.maxsize):
            return self.filtering_function(self.values)
        else:
            return self.values[-1]        

def id_function(l):
    return l[-1]
        
def MedianFilter(maxsize):
    return Filter(maxsize, numpy.median)

def MeanFilter(maxsize):
    return Filter(maxsize, numpy.mean)
