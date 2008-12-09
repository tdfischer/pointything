# -*- coding: utf-8 -*-
class MatchBase:
    def __init__(self, operand, field, value):
        self.field = field
        self.value = value
        self.op = operand
    
    def __str__(self):
        return str(self.field) + self.op + str(self.field.cast(self.value))

class Equals(MatchBase):
    def __init__(self, field, value):
        MatchBase.__init__(self, '==', field, value)