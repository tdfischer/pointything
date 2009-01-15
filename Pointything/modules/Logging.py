# -*- coding: utf-8 -*-
from Pointything.Extensions import *
import logging

class LogControl(Extension):
    """Controls Pointything's Logging system"""
    def __str__(self):
        return "Logging Control"
    @Action
    def getLevel(self, input, logger="Pointything"):
        l = logging.getLogger(logger)
        return logging.getLevelName(l.getEffectiveLevel())

    @Action
    def setLevel(self, input, newLevel, logger="Pointything"):
        try:
            newLevel = int(newLevel)
        except ValueError:
            try:
                newLevel = int(getattr(logging, newLevel))
            except ValueError:
                return "Invalid name for a level."
        l = logging.getLogger(logger)
        l.setLevel(newLevel)
        return "New level: %s"%logging.getLevelName(l.getEffectiveLevel())