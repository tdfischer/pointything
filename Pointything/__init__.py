# -*- coding: utf-8 -*-
import imp
from Extensions import *
import sys
import select
import __builtin__

class ExtensionControl(Extension):
    '''Extension to control the extensions'''
    extension_name = "extensionControl"
    def __init__(self, bot):
        Extension.__init__(self, bot)
        sys.path.append("/home/trever/Projects/Pointything5/Pointything/modules")
    
    @Action
    def loadModule(self, bot, modName):
        (file, path, desc) = imp.find_module(modName)

        mod = imp.load_module(modName, file, path, desc)
        foundExtensions = []
        for item in dir(mod):
            ext = getattr(mod, item)
            if type(ext) == type(Extension) and issubclass(ext, Extension) and ext != Extension and ext != InputHandler:
                foundExtensions.append(ext.extension_name)
                bot.extendWith(ext)
        return "Loading complete. Found extensions: %s"%(foundExtensions)
    
    @Action
    def details(self, bot, extName):
        ext = bot.grabExtension(extName)
        details = {}
        details["Name"] = ext.extension_name
        details["Desc"] = ext.__doc__
        details["Class"] = str(ext)
        return details
    
    @Action
    def unload(self, bot, extName):
        bot.unloadExtension(bot.grabExtension(extName))
        return "Unloaded extension"
        
    @Action
    def functions(self, bot, module=None):
        ret = []
        if module!=None:
            for i in bot.extensions[module].userMethods():
                ret.append(i.action_name)
        else:
            ret = bot.commands
        return ret
    
    @Action
    def extensions(self, bot):
        ret = []
        for m in bot.extensions:
            ret.append(m)
        return ret

class Pointything:
    def __init__(self):
        self.commands = {}
        self.extensions = {}
        self.inputs = []
        
        self.extendWith(ExtensionControl)

    def do(self, command, *args, **kwargs):
        input = Output(args)
        if command in self.commands:
            command = self.commands[command]
        else:
            raise NotImplementedError, "Could not find command %s"%(command)
        out = command(self, *input, **kwargs)
        def doWrapper(command, *fargs, **fkwargs):
            for i in fargs:
                out.append(i)
            return self.do(command, *out, **fkwargs)

        out.do = doWrapper
        return out

    def run(self):
        while True:
            streamToListener = {}
            for i in self.inputs:
                for s in i.streams():
                    streamToListener[s] = i
            if len(streamToListener)==0:
                return
            outputs = select.select(streamToListener,[],[])[0]
            for out in outputs:
                streamToListener[out].parse(self)

    def extendWith(self, ext):
        self.unloadExtension(ext)
        extInstance = ext(self)
        self.extensions[ext.extension_name]=extInstance
        for cmd in extInstance.userMethods():
                self.commands[ext.extension_name+"."+cmd.action_name] = cmd
                self.commands[cmd.action_name] = cmd
        if isinstance(extInstance, InputHandler):
            self.inputs.append(extInstance)
    
    def grabExtension(self, extName):
        return self.extensions[extName]
    
    def unloadExtension(self, ext):
        if ext in self.extensions.values():
            for cmd in ext.userMethods():
                if self.commands[cmd.action_name] == cmd:
                    del self.commands[cmd.action_name]
                del self.commands[ext.extension_name+"."+cmd.action_name]
            del self.extensions[ext.extension_name]
        if ext in self.inputs:
            self.inputs.remove(ext)