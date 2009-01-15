# -*- coding: utf-8 -*-
from Pointything.Extensions import *
from Pointything.Auth import *
import socket
import threading
import traceback
import sys
import atexit
import logging

class TelnetLogHandler(logging.Handler):
    def __init__(self, handler):
        logging.Handler.__init__(self)
        self.handler = handler
        
    def emit(self, record):
        for c in self.handler.clients:
            try:
                c.send(self.format(record)+"\n")
            except socket.error:
                pass
            except:
                self.handleError(record)

class TelnetListener(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        self.running = False
        self.handler = handler
        self.daemon = True
        self.server = socket.socket()
        bound = False
        port = 16161
        while not bound:
            try:
              self.server.bind(("0.0.0.0", port))
              bound = True
            except socket.error:
              port+=1
        self.handler.log.info("Listening on *:%s", port)
        self.server.listen(1)
    
    def run(self):
        self.handler.log.debug("Starting listener thread")
        self.running = True
        self.server.settimeout(3)
        while self.running == True:
            try:
                (sock, addr) = self.server.accept()
                self.handler.clients.append(sock)
                self.handler.buffers[sock] = ""
                self.handler.log.info("Accepted client %s",addr)
            except socket.timeout:
                pass
        self.server.close()
    
    def kill(self):
        self.running = False

class TelnetInput(InputHandler):
    def __init__(self, bot):
        InputHandler.__init__(self, bot)
        self.clients = []
        self.buffers = {}
        self.listenThread = None
        self.logHandler = None
    
    def __str__(self):
        return "Telnet Interface"
    
    def init(self):
        self.listenThread = TelnetListener(self)
        self.listenThread.start()
        self.logHandler = TelnetLogHandler(self)
        logging.root.addHandler(self.logHandler)
    
    def unloaded(self):
        self.stopListener();
        listenThread = None
        for s in self.clients:
            s.close()
    
    def reloading(self, old):
        self.listenThread = old.listenThread
        self.clients = old.clients
        self.buffers = old.buffers
        self.logHandler = old.logHandler
    
    def stopListener(self):
        self.log.info("Shutting down listener thread...")
        self.listenThread.kill()
        self.listenThread.join()
    
    def parse(self, bot, stream):
        lineBuffer = self.buffers[stream]
        lineBuffer+=stream.recv(1024)
        line = lineBuffer.partition("\n")[0]
        self.buffers[stream] = lineBuffer.partition("\n")[2]
        if line == "":
            stream.close()
            self.log.info("Client disconnected.")
            self.clients.remove(stream)
            del self.buffers[stream]
            return
        args = line.split(" ")
        command = args[0]
        input = Output(args[1:], User(1))
        try:
            #bot.readBanter(line)
            ret = bot.do(command, input)
            stream.send(str(ret)+"\n")
        except NotImplementedError:
            stream.send("Unknown command: %s\n"%command)
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            out = traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)
            for line in out:
                stream.send(line)
    
    def streams(self):
        return self.clients
