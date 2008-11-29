# -*- coding: utf-8 -*-
from Pointything.Extensions import *
from Pointything.Database import *
from Pointything.Auth import *
import socket
import threading
import traceback
import sys

class TelnetInput(InputHandler):
    extension_name="Telnet"
    def __init__(self, bot):
        InputHandler.__init__(self, bot)
        self.log.info("Listening on *:16161")
        self.server = socket.socket()
        self.server.bind(("0.0.0.0", 16161))
        self.server.listen(1)
        self.clients = []
        self.buffers = {}
        self.listenThread = threading.Thread(target=self.acceptLoop)
        self.log.debug("Starting listener thread")
        self.listenThread.start()
    
    def acceptLoop(self):
        while True:
            (sock, addr) = self.server.accept()
            self.clients.append(sock)
            self.buffers[sock] = ""
            self.log.info("Accepted client %s",addr)
    
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