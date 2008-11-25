# -*- coding: utf-8 -*-
import imp
from Extension import *
from io import *
import sys

class ExtensionControl(Extension):
    extension_name = "extensionControl"
    def __init__(self):
        sys.path.append("/home/trever/Projects/Pointything5/Pointything/modules")
    
    @Action
    def loadModule(self, bot, modName):
        (file, path, desc) = imp.find_module(modName)
        if file == None:
            raise ImportError, "Module not found"
        mod = imp.load_module(modName, file, path, desc)
        foundExtensions = []
        for item in dir(mod):
            ext = getattr(mod, item)
            if type(ext) == type(Extension) and issubclass(ext, Extension) and ext != Extension:
                foundExtensions.append(ext.extension_name)
                bot.extendWith(ext())
        return "Loading complete. Found extensions: %s"%(foundExtensions)
    
    @Action
    def loadExtension(self, bot, extName):
        for item in globals():
            if type(item) == type(__builtin__):
                for ext in dir(item):
                    if type(ext) == type(Extension) and issubclass(ext, Extension):
                        bot.extendWith(ext())
        else:
            raise ImportError, "Extension not found in loaded modules."
        return "Found module"
    
    @Action
    def unloadExtension(self, bot, modName):
        pass
        
    @Action
    def listFunctions(self, bot):
        ret = []
        for f in bot.commands.keys():
            ret.append(f)
        return ret
    
    @Action
    def listExtensions(self, bot):
        ret = []
        for m in bot.extensions:
            ret.append(m.extension_name)
        return ret

class Pointything:
    def __init__(self):
        self.commands = {}
        self.extensions = []

    def do(self, command, *args, **kwargs):
        #if len(args)==0:
        #    input = Output()
        #elif type(args[0]) != Output:
        #    input = Output(args[0])
        #else:
        #    input = args[0]
        input = Output()
        for i in args:
            input.append(i)
        command = self.commands[command]
        out = command(self, *input, **kwargs)
        def doWrapper(command, *fargs, **fkwargs):
            for i in fargs:
                out.append(i)
            return self.do(command, *out, **fkwargs)

        out.do = doWrapper
        return out

    def extendWith(self, ext):
        self.unloadExtension(ext)
        self.extensions.append(ext)
        for cmd in ext.userMethods():
            if cmd.action_name in self.commands.keys():
                self.commands[ext.extension_name+"_"+cmd.action_name] = cmd
            else:
                self.commands[cmd.action_name] = cmd
    
    def unloadExtension(self, ext):
        if ext in self.extensions:
            for cmd in ext.userMethods():
                del self.commands[cmd.action_name]
            self.extensions.remove(ext)