# -*- coding: utf-8 -*-
r"""Field types
"""
import Constraints

class BaseField:
    def __init__(self, type, name):
        self.name = name
        self.constraints = []
        self.type = type
        self.table = None
        self.foreignTables = []
    
    def addConstraint(self, c):
        """Applies a constraint to the field"""
        if isinstance(c, Constraints.ForeignKey):
                self.foreignTables.append(c.other.table)
        self.constraints.append(c)
        return self
    
    def __repr__(self):
        constraints = ""
        if len(self.constraints)>0:
            constraints = []
            for c in self.constraints:
                constraints.append(repr(c))
        return "%s %s %s"%(self.name, self.type, " ".join(constraints))
    
    def __str__(self):
        return self.name
        
    def cast(self, data):
        """Converts data into the field's native format"""
        pass

class Text(BaseField):
    def __init__(self, name):
        BaseField.__init__(self, 'text', name)
    def cast(self, data):
        if data == None:
            return ""
        return str(data)

class Integer(BaseField):
    def __init__(self, name):
        BaseField.__init__(self, 'integer', name)
    def cast(self, data):
        if data == None:
            return 0
        return int(data)