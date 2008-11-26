# -*- coding: utf-8 -*-
from Pointything.Extensions import *

class HelpExtension(Extension):
    extension_name="help"
    
    @Action
    def help(self, bot, *args):
        return "Ok"