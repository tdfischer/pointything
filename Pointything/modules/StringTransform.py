# -*- coding: utf-8 -*-
from Pointything.Extensions import *

class StringTransform(Extension):
    
    @Action("concat")
    def concat(self, bot, *args, **kwargs):
        return Output(args,"")

    @Action("reverse")
    def reverse(self, bot, *args, **kwargs):
        if len(args)==1:
            tmp = []
            for i in args[0]:
                tmp.append(i)
            tmp.reverse()
            return Output(tmp, "")
        input = Output()
        for i in args:
            input.append(i)
        input.reverse()
        return input
