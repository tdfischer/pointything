# -*- coding: utf-8 -*-

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