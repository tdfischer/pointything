# -*- coding: utf-8 -*-
import Pointything
from Pointything import irclib
from Pointything.Extensions import *
import sys

def pthangCompleter(bot):
    def complete(text, state):
        matches = []
        for i in bot.do("functions"):
            if i.startswith(text):
                matches.append(i)
        return matches[state]
    return complete

class ShellInput(InputHandler):
    def parse(self, bot):
        line = sys.stdin.readline()
        if line=="":
            sys.stdin.close()
            bot.unloadExtension(self)
            return
        line = line.strip()
        args = line.split(" ")
        try:
            print bot.do(*args)
        except msg:
            print "Exception: %s"%(msg)
    
    def streams(self):
        if sys.stdin.closed:
            return ()
        return (sys.stdin,)

class IRCInput(InputHandler):
    def __init__(self, bot):
        InputHandler.__init__(self, bot)
        self.bot = bot
        self.ircSockets = []
        self.irc = irclib.IRC(self.addSocket, self.removeSocket)
        self.irc.add_global_handler("privmsg", self.privmsg)
        self.irc.add_global_handler("pubmsg", self.pubmsg)
        slashnet = self.irc.server()
        slashnet.connect("irc.slashnet.org", 6667, "Workbot", ircname="Greased Lightning")
        slashnet.add_global_handler("welcome", self.joinChannel)
    
    def joinChannel(self, server, event):
        server.join("#gmg")
    
    def addSocket(self, sock):
        print "Adding socket"
        self.ircSockets.append(sock)
    
    def removeSocket(self, sock):
        print "Removing socket"
        self.ircSockets.remove(sock)
    
    def parse(self, bot):
        self.irc.process_once()
    
    def pubmsg(self, server, event):
        args = event.arguments()[0].split(' ')
        first = args[0]
        print "First: "+first
        if first == server.get_nickname()+":":
            args = args[1:]
        elif first.startswith("~"):
            args[0] = args[0][1:]
        else:
            return
        try:
            server.privmsg(event.target(),str(self.bot.do(*args)))
        except Exception, msg:
            server.privmsg(irclib.nm_to_n(event.source()),str(msg))
    
    def privmsg(self, server, event):
        args = event.arguments()[0].split(' ')
        try:
            server.privmsg(irclib.nm_to_n(event.source()),str(self.bot.do(*args)))
        except Exception, msg:
            server.privmsg(irclib.nm_to_n(event.source()),str(msg))
    
    def streams(self):
        return self.ircSockets

if __name__ == "__main__":
    irclib.DEBUG = 1
    pthang = Pointything.Pointything()
    pthang.extendWith(ShellInput)
    pthang.run()