# -*- coding: utf-8 -*-
r"""Classes for dealing with extensions, Pointything actions, and the passing of data between actions"""
from functools import wraps
import logging
import sys
import imp

__all__ = ["Extension", "Output", "Action", "InputHandler"]

class Extension:
    """The heart of Pointything's extensibility.
    
    Extension classes are meant to be loaded, unloaded, and reloaded on the fly with minimal hassle.
    Normaly, __init__() and __del__() would be used to handle the loading and unloading. However,
    /reloading/ an extension adds another level of complexity. It isn't enough to simply create
    a new instance of an Extension and delete the old, because the state of an extension might want
    to be preserved between reloads. The following set of methods were designed to handle this:
    
    * init - Called when the extension is first seen
    * unloaded - Called when the extension is last seen
    * reloading - Called on the new instance when it is about to replace the old one
    * disposed - Called on the old instance after it has been supplanted by the new instance.
    
    For every Extension, __init__ and __del__ get handled apropriately on a per-instance basis.
    For simple extensions that don't need to keep a state over Pointything's lifetime, that is
    all they need. However, what if you are writing an extension that needs to keep a set of
    memos in memory? Using only __init__, your internal memo variables would be wiped at every
    extension reload. This is where these magic functions come in. To transfer the memo list
    between module reloads, this memo module would need to implement the reloading method:
    
    def reloading(self, old):
        self.memoList = old.memoList
    
    And your old memo list is now stored in the new extension instance.
    
    The init and unloaded methods work in a similar fashion. When an extension is first seen in Python,
    it gets instantiated (which calls __init__), then init is called. Between then and the end of
    the extension's life, reloads may happen (which use reloading/disposed), and finally unloaded is called.
    
    Extensions always get unloaded when the main loop exits, however they may also be unloaded on-demand.
    
    Each Extension contains a set of actions (decorated with Action) that may be called by
    Pointything's users. Simply marking it with @Action tags it for inclusion in the default
    implementation of userMethods.
    
    Actions get added to pointything with two names. The first is the actionName, the second is of the form
    repr(extension)+"."+actionName.
    
    Other extensions may register actions with the same short names, but they may not claim another
    action's full name.
    """
    def __init__(self, bot):
        self.log = logging.getLogger("Pointything.extensions.%s"%repr(self))
    
    def __getattribute__(self, name):
        for m in self.userMethods():
            if name == m.name:
                return m
        if hasattr(self, name):
            return getattr(self, name)
    
    def userMethods(self):
        """Must return a list of available methods"""
        ret = []
        for m in dir(self):
            m = getattr(self, m)
            if hasattr(m,'action_name'):
                ret.append(m)
        return ret
    
    def init(self):
        """Called when the extension is first created"""
    
    def unloaded(self):
        """Called when the extension is unloaded"""
        pass
        
    def reloading(self, oldInstance):
        """Called when the extension has been replaced with a new instance"""
        pass
        
    def disposed(self, newInstance):
        """Called when the old extension has been replaced with the new one."""
        pass
        
    def readBanter(self, input, user):
        """Called to handle text recieved that isn't a command"""
        pass
    
    def __str__(self):
        """Returns the user-friendly name of the extension"""
        return repr(self)
        
    def __repr__(self):
        """Returns the internal representation of the extension. Overriding this is not recommended."""
        return self.__class__.__name__

def Action(name=None):
    """Methods decorated with this become tagged for inclusion in the default implementation of Extension.userMethods() and have their return value automatically wrapped inside an Output object."""
    if type(name)==str:
        def wrapper(func):
            @wraps(func)
            def outputWrap(*args, **kwargs):
                return Output(func(*args, **kwargs))
            outputWrap.action_name = name
            return outputWrap
        return wrapper
    else:
        @wraps(name)
        def outputWrap(*args, **kwargs):
            return Output(name(*args, **kwargs))
        outputWrap.action_name=name.__name__
        return outputWrap

class Output(list):
    """Standardized object for passing data between actions"""
    def __init__(self, input=None, user=None, bot=None, delimiter=None):
        if delimiter == None:
            self.delimiter = " "
        self.bot = bot
        self.user = user
        list.__init__(self)
        if type(input)==str or type(input) == unicode or type(input) == int:
            self.append(input)
        elif input != None:
            if isinstance(input,Output):
                if delimiter == None:
                    self.delimiter = input.delimiter
                self.do = input.do
                if user == None:
                    self.user = input.user
                if bot == None:
                    self.bot = input.bot
            for i in input:
                self.append(i)

    def __str__(self):
        if len(self)>0:
            return str(reduce(lambda x,y:str(x)+self.delimiter+str(y), self))
        return ""
    
    def do(self, command, out, user):
        """For chaining commands"""
        pass

class InputHandler(Extension):
    """Describes an extension that can handle input streams"""
    def parse(self, bot, stream):
        """Called when select() on a stream (from InputHandler.streams) notifies that it has data ready to be read."""
        pass

    def streams(self):
        """Must return a list of file-like objects that eventually make their way to select() in the main event loop"""
        pass
        
class ExtensionControl(Extension):
    '''Extension to control the extensions. Thats deep, man.'''
    def __str__(self):
        return "Extension Management"
    def __init__(self, bot):
        Extension.__init__(self, bot)
        extPath = "/home/trever/Projects/Pointything5/Pointything/modules"
        self.log.debug("Looking for extensions in %s",extPath)
        sys.path.append(extPath)
    
    @Action
    def loadModule(self, input, modName):
        """Load a module"""
        self.log.info("Loading module %s",modName)
        self.log.debug("Looking for module %s", modName)
        (file, path, desc) = imp.find_module(modName)
        self.log.debug("Found in %s", path)
        mod = imp.load_module(modName, file, path, desc)
        foundExtensions = []
        for item in dir(mod):
            ext = getattr(mod, item)
            if type(ext) == type(Extension) and issubclass(ext, Extension) and ext != Extension and ext != InputHandler:
                self.log.debug("Found extension %s", ext)
                foundExtensions.append(ext)
                input.bot.extendWith(ext)
        self.log.info("Loaded %s with extensions: %s", modName, map(lambda x:x.__name__,foundExtensions))
        return "Loading complete. Found extensions: %s"%(foundExtensions)
    
    @Action
    def details(self, input, extName):
        """Give details about a module"""
        ext = input.bot.grabExtension(extName)
        details = {}
        details["Name"] = str(ext)
        details["Desc"] = ext.__doc__
        details["Class"] = repr(ext)
        return details
    
    @Action
    def unload(self, input, extName):
        """Unload a module by name"""
        self.log.info("Unloading extension %s", extName)
        input.bot.unloadExtension(input.bot.grabExtension(extName))
        return "Unloaded extension"
        
    @Action
    def functions(self, input, module=None):
        """Returns a list of all functions declared by all loaded extensions"""
        ret = []
        if module!=None:
            for i in input.bot.extensions[module].userMethods():
                ret.append(i.action_name)
        else:
            ret = input.bot.commands
        return ret
    
    @Action
    def extensions(self, bot):
        """Lists all loaded extensions"""
        ret = []
        for m in input.bot.extensions:
            ret.append(m)
        return ret