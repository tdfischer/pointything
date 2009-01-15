# -*- coding: utf-8 -*-
import Pointything
from Pointything.Extensions import *
import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("Pointything.Database").setLevel(logging.INFO)
    pthang = Pointything.Pointything()
    pthang.do("loadModule", "Telnet")
    pthang.do("loadModule", "Markov")
    try:
        pthang.run()
    except KeyboardInterrupt:
        pthang.cleanup()