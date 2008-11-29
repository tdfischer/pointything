# -*- coding: utf-8 -*-
from functools import wraps
import logging

class Extension:
    extension_name = ""
    def __init__(self, bot):
        self.log = logging.getLogger("Pointything.extensions.%s"%(self.__class__.extension_name))
    
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
    def __init__(self, input=None, user=None, bot=None, delimiter=None):
        if delimiter == None:
            self.delimiter = " "
        self.bot = bot
        self.user = user
        list.__init__(self)
        if type(input)==str or type(input) == unicode:
            self.append(input)
        elif input != None:
            if isinstance(input,Output):
                if delimiter == None:
                    self.delimiter = input.delimiter
                self.do = input.do
                if user == None:
                    self.user = input.user
                if bot == None:
                    self.bot = input.bot
            for i in input:
                self.append(i)

    def __str__(self):
        if len(self)>0:
            return str(reduce(lambda x,y:str(x)+self.delimiter+str(y), self))
        return ""
    
    def do(self, command, out, user):
        pass

class InputHandler(Extension):
    def parse(self, bot, stream):
        pass

    def streams(self):
        pass