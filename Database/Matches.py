# -*- coding: utf-8 -*-
from Fields import BaseField
class MatchBase:
    def __init__(self, operand, field, value):
        self.field = field
        self.value = value
        self.op = operand
    
    def __str__(self):
        return str(self.field) + self.op + str(self.field.cast(self.value))
    
    def __repr__(self):
        return str(self.field) + self.op + "?"

class Equals(MatchBase):
    RIGHT = 1
    LEFT = 2
    def __init__(self, field, value):
        if isinstance(field, BaseField):
            self.direction = Equals.RIGHT
            self.field = field
            self.value = value
        else:
            self.direction = Equals.LEFT
            self.field = value
            self.value = field
        MatchBase.__init__(self, '==', self.field, self.value)
    
    def __repr__(self):
        if self.direction==Equals.RIGHT:
            return str(self.field) + self.op + "?"
        else:
            return "?" + self.op + str(self.field)
    
    def __str__(self):
        if self.direction==Equals.RIGHT:
            return str(self.field) + self.op + str(self.field.cast(self.value))
        else:
            return str(self.field.cast(self.value)) + self.op + str(self.field)