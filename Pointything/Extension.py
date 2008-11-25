# -*- coding: utf-8 -*-
from functools import wraps
from io import Output

class Extension:
    extension_name = ""
    def __init__(self):
        pass
    
    def __getattribute__(self, name):
        for m in self.userMethods():
            if name == m.name:
                return m
        if hasattr(self, name):
            return getattr(self, name)
    
    def userMethods(self):
        ret = []
        for m in dir(self):
            m = getattr(self, m)
            if hasattr(m,'action_name'):
                ret.append(m)
        return ret

def Action(name=None):
    if type(name)==str:
        def wrapper(func):
            def outputWrap(*args, **kwargs):
                return Output(func(*args, **kwargs))
            outputWrap.action_name = name
            return outputWrap
        return wrapper
    else:
        def outputWrap(*args, **kwargs):
            return Output(name(*args, **kwargs))
        outputWrap.action_name=name.__name__
        return outputWrap