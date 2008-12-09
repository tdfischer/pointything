# -*- coding: utf-8 -*-
from Pointything.Extensions import *
from Pointything.Auth import *
import socket
import threading
import traceback
import sys
import atexit

class TelnetListener(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        self.running = False
        self.handler = handler
        self.daemon = True
        self.handler.log.info("Listening on *:16161")
        self.server = socket.socket()
        self.server.bind(("0.0.0.0", 16161))
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
    extension_name="Telnet"
    def __init__(self, bot):
        InputHandler.__init__(self, bot)
        self.clients = []
        self.buffers = {}
        self.listenThread = TelnetListener(self)
        self.listenThread.start()
        
    def unloaded(self):
        self.stopListener();
        for s in self.clients:
            s.close()
    
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
            ret = bot.do(command, input)
            stream.send(str(ret)+"\n")
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            out = traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)
            for line in out:
                stream.send(line)
    
    def streams(self):
        return self.clients