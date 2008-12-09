# -*- coding: utf-8 -*-
class BaseField:
    def __init__(self, type, name):
        self.name = name
        self.constraints = []
        self.type = type
        self.table = None
    
    def addConstraint(self, type):
        self.constraints.append(type)
        return self
    
    def __repr__(self):
        return "%s %s %s"%(self.name, self.type, reduce((lambda x,y:repr(x)+" "+repr(y)),self.constraints, ""))
    
    def __str__(self):
        return self.name
        
    def cast(self, data):
        pass

class Text(BaseField):
    def __init__(self, name):
        BaseField.__init__(self, 'text', name)
    def cast(self, data):
        return int(data)

class Integer(BaseField):
    def __init__(self, name):
        BaseField.__init__(self, 'integer', name)
    def cast(self, data):
        return int(data)