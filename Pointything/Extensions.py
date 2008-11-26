# -*- coding: utf-8 -*-
from functools import wraps

class Extension:
    extension_name = ""
    def __init__(self, bot):
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
            @wraps(func)
            def outputWrap(*args, **kwargs):
                return Output(func(*args, **kwargs))
            outputWrap.action_name = name
            return outputWrap
        return wrapper
    else:
        @wraps(name)
        def outputWrap(*args, **kwargs):
            return Output(name(*args, **kwargs))
        outputWrap.action_name=name.__name__
        return outputWrap

class Output(list):
    def __init__(self, init=None, delimiter=" "):
        self.delimiter = delimiter
        list.__init__(self)
        if type(init)==str:
            self.append(init)
        elif init != None:
            if isinstance(init,Output):
                self.delimiter = init.delimiter
                self.do = init.do
            for i in init:
                self.append(i)

    def __str__(self):
        if len(self)>0:
            return str(reduce(lambda x,y:str(x)+self.delimiter+str(y), self))
        return ""
    
    def do(self, command, *args, **kwargs):
        pass

class InputHandler(Extension):
    def parse(self):
        pass

    def streams(self):
        pass