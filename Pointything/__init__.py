# -*- coding: utf-8 -*-
r"""Pointything, The Famous Whatshisface"""
from Extensions import *
from Extensions import ExtensionControl
import select
import logging
import __builtin__
import traceback
import sys

class Pointything:
    def __init__(self):
        self.commands = {}
        self.extensions = {}
        self.inputs = []
        self.log = logging.getLogger("Pointything")
        self.extendWith(ExtensionControl)

    def do(self, command, input, user=None):
        """'Does' a command. The heart of Pointything."""
        input = Output(input, user, self)
        if command in self.commands:
            command = self.commands[command]
        else:
            raise NotImplementedError, "Could not find command %s"%(command)
        self.log.debug("Executing %s(%s)", command, input)
        out = command(input, *input)
        def doWrapper(command, finput, fuser=None):
            for i in finput:
                out.append(i)
            return self.do(command, out, fuser)

        out.do = doWrapper
        return out

    def readBanter(self, input, user=None):
        for ext in self.extensions.values():
            ext.readBanter(input, user)
    
    def run(self):
        """Begins the main loop"""
        self.log.info("Entering main loop.")
        while True:
            streamToListener = {}
            for i in self.inputs:
                for s in i.streams():
                    streamToListener[s] = i
            if len(streamToListener)==0:
                #self.log.warn("No more streams.")
                pass
            #    return
            else:
                outputs = select.select(streamToListener,[],[])[0]
                self.log.debug("Activity on %s streams",len(outputs))
                for out in outputs:
                    try:
                        streamToListener[out].parse(self, out)
                    except:
                        self.log.error("Exception while parsing input with %s", streamToListener[out].parse)
                        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                        out = traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)
                        for line in out:
                            self.log.error(line.strip())
        self.log.info("Exiting main loop.")
        self.cleanup()
    
    def cleanup(self):
        """Performs some end-of-life maintenence, including unloading modules and closing inputs."""
        self.log.debug("Cleaning up modules...")
        extList = self.extensions.copy()
        for m in extList:
            self.unloadExtension(self.extensions[m])

    def extendWith(self, ext):
        """Loads an instance of ext
        
        ext is _NOT_ an instance of an Extension class. It is the class itself.
        Extensions must be initialized properly by Pointything to work right.
        
        """
        log = logging.getLogger("Pointything.extensions")
        log.debug("Creating new instance of extension %s", ext)
        extInstance = ext(self)
        try:
            old = self.grabExtension(repr(extInstance))
        except:
            old = None
        if old == None:
            log.info("Loading extension %s (%s)", repr(extInstance), extInstance)
            extInstance.init()
        else:
            log.info("Reloading extension %s (%s)", repr(extInstance), extInstance)
            extInstance.reloading(old)
            old.disposed(extInstance)
            del old
        self.extensions[repr(extInstance)]=extInstance
        for cmd in extInstance.userMethods():
                self.commands[repr(extInstance)+"."+cmd.action_name] = cmd
                self.commands[cmd.action_name] = cmd
        if isinstance(extInstance, InputHandler):
            log.info("Attaching %s as input", extInstance)
            self.inputs.append(extInstance)
    
    def grabExtension(self, extName):
        """Returns the extension with the given name"""
        return self.extensions[extName]
    
    def unloadExtension(self, ext):
        """Unloads the extension"""
        log = logging.getLogger("Pointything.extensions")
        if ext in self.extensions.values():
            log.info("Unloading extension %s (%s)", repr(ext), ext)
            for cmd in ext.userMethods():
                log.debug("Unregistering commands %s, %s", cmd.action_name, repr(ext)+"."+cmd.action_name)
                if self.commands[cmd.action_name] == cmd:
                    del self.commands[cmd.action_name]
                del self.commands[repr(ext)+"."+cmd.action_name]
            del self.extensions[repr(ext)]
        if ext in self.inputs:
            log.info("Detatching input %s", ext)
            self.inputs.remove(ext)
        ext.unloaded()