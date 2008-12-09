# -*- coding: utf-8 -*-
class Constraint:
    def __init__(self, str):
        self.str = str
    
    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.str

class AutoIncrement(Constraint):
    def __init__(self):
        Constraint.__init__(self, "autoincrement")

class Key(Constraint):
    def __init__(self):
        Constraint.__init__(self, "key")

class PrimaryKey(Constraint):
    def __init__(self):
        Constraint.__init__(self, "primary key")

class ForeignKey(Constraint):
    def __init__(self, other, *actions):
        Constraint.__init__(self, "references")
        self.other = other
        self.actions = actions
    
    def __repr__(self):
        return "references %s.%s %s"%(self.other.table.name, self.other.name, reduce((lambda x,y:str(x)+" "+str(y)), self.actions))

class ForeignKeyAction:
    def __init__(self, event, action):
        self.event = event
        self.action = action
    def __str__(self):
        return "on %s %s"%(self.event, self.action)