# -*- coding: utf-8 -*-
import Pointything
from Pointything.Extensions import *
import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pthang = Pointything.Pointything()
    pthang.do("loadModule", "Telnet")
    #pthang.extendWith(TelnetInput)
    pthang.run()