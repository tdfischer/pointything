# -*- coding: utf-8 -*-
from Pointything.Extensions import *

class Tests(Extension):
    @Action
    def banter(self, input, *args):
        '''Runs input through Pointything.readBanter'''
        input.bot.readBanter(str(input))
        
    @Action
    def eval(self, input, *args):
        '''Passes python code through eval()'''
        return eval(str(input))
        
    @Action
    def compile(self, input, *args):
        '''Passes python code through compile(), then eval()'''
        return eval(compile(str(input),'<string>','exec'))
    
    def __str__(self):
        return "Various Pointything Tests"