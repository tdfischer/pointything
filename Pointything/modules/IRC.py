# -*- coding: utf-8 -*-
import irclib
irclib.DEBUG = 1
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
    
    def parse(self, bot, stream):
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
            self.bot.readBanter(event.arguments()[0])
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
