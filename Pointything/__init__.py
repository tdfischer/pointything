# -*- coding: utf-8 -*-
import imp
from Extensions import *
import sys
import select
import logging
import __builtin__
import traceback

class ExtensionControl(Extension):
    '''Extension to control the extensions. Thats deep, man.'''
    extension_name = "extensionControl"
    def __init__(self, bot):
        Extension.__init__(self, bot)
        extPath = "/home/trever/Projects/Pointything5/Pointything/modules"
        self.log.debug("Looking for extensions in %s",extPath)
        sys.path.append(extPath)
    
    @Action
    def loadModule(self, input, modName):
        self.log.info("Loading module %s",modName)
        self.log.debug("Looking for module %s", modName)
        (file, path, desc) = imp.find_module(modName)
        self.log.debug("Found in %s", path)
        mod = imp.load_module(modName, file, path, desc)
        foundExtensions = []
        for item in dir(mod):
            ext = getattr(mod, item)
            if type(ext) == type(Extension) and issubclass(ext, Extension) and ext != Extension and ext != InputHandler:
                self.log.debug("Found extension %s", ext.extension_name)
                foundExtensions.append(ext.extension_name)
                input.bot.extendWith(ext)
        self.log.info("Loaded %s with extensions: %s", modName, foundExtensions)
        return "Loading complete. Found extensions: %s"%(foundExtensions)
    
    @Action
    def details(self, input, extName):
        ext = input.bot.grabExtension(extName)
        details = {}
        details["Name"] = ext.extension_name
        details["Desc"] = ext.__doc__
        details["Class"] = str(ext)
        return details
    
    @Action
    def unload(self, input, extName):
        self.log.info("Unloading extension %s", extName)
        input.bot.unloadExtension(input.bot.grabExtension(extName))
        return "Unloaded extension"
        
    @Action
    def functions(self, input, module=None):
        ret = []
        if module!=None:
            for i in input.bot.extensions[module].userMethods():
                ret.append(i.action_name)
        else:
            ret = input.bot.commands
        return ret
    
    @Action
    def extensions(self, bot):
        ret = []
        for m in input.bot.extensions:
            ret.append(m)
        return ret

class Pointything:
    def __init__(self):
        self.commands = {}
        self.extensions = {}
        self.inputs = []
        self.log = logging.getLogger("Pointything")
        self.extendWith(ExtensionControl)

    def do(self, command, input, user=None):
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

    def run(self):
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
        self.log.debug("Cleaning up modules...")
        extList = self.extensions.copy()
        for m in extList:
            self.unloadExtension(self.extensions[m])

    def extendWith(self, ext):
        log = logging.getLogger("Pointything.extensions")
        log.info("Loading extension %s", ext.extension_name)
        extInstance = ext(self)
        #self.unloadExtension(ext)
        self.extensions[ext.extension_name]=extInstance
        for cmd in extInstance.userMethods():
                self.commands[ext.extension_name+"."+cmd.action_name] = cmd
                self.commands[cmd.action_name] = cmd
        if isinstance(extInstance, InputHandler):
            log.info("Attaching %s as input", ext.extension_name)
            self.inputs.append(extInstance)
    
    def grabExtension(self, extName):
        return self.extensions[extName]
    
    def unloadExtension(self, ext):
        log = logging.getLogger("Pointything.extensions")
        if ext in self.extensions.values():
            log.info("Unloading extension %s", ext.extension_name)
            for cmd in ext.userMethods():
                log.debug("Unregistering commands %s, %s", cmd.action_name, ext.extension_name+"."+cmd.action_name)
                if self.commands[cmd.action_name] == cmd:
                    del self.commands[cmd.action_name]
                del self.commands[ext.extension_name+"."+cmd.action_name]
            del self.extensions[ext.extension_name]
        if ext in self.inputs:
            log.info("Detatching input %s", ext.extension_name)
            self.inputs.remove(ext)
        ext.unloaded()