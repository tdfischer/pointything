#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import re
import os
import sys

class Graph:
    SENTENCE_END = [".", "!", "?"]
    def __init__(self):
        self.nodes = {}
    
    def getWord(self, word):
        end = word[-1]
        word = re.sub('\W', '', word.lower())
        if word == "":
            return None
        if (not (word in self.nodes)):
            #print "New word %s"%word
            self.nodes[word] = Word(word)
        if end in Graph.SENTENCE_END:
            self.nodes[word].addNext(None)
        return self.nodes[word]

class Word:
    def __init__(self, word):
        self.word = word
        self.count = 0
        self.next = {}
        self.prev = {}
        self.score = 0
    
    def addNext(self, other):
        if other in self.next:
            self.next[other]+=1
        else:
            self.next[other] = 1
    
    def addPrev(self, other):
        if other in self.prev:
            self.prev[other]+=1
        else:
            self.prev[other] = 1
    
    def trimList(self, lst, limit=-1):
        if len(lst)==0:
            return lst
        total = 0
        minval = sys.maxint
        maxval = 0
        for i in lst:
            n = lst[i]
            if n>maxval:
                maxval = n
            if n<minval:
                minval = n
            total+=n
        mean = total/len(lst)
        if limit == -1:
            limit = mean/7
        #print "%s Min: %i Max: %i Mean: %i Limit: %i Total: %i Size: %i"%(self, minval, maxval, mean, limit, total, len(lst))
        ret = {}
        for i in lst:
            if lst[i]<=limit:
                continue
            ret[i] = lst[i]
        return ret
    
    def getPrev(self):
        return self.getRandom(self.prev)
    
    def getNext(self):
        return self.getRandom(self.next)
    
    def getRandom(self, lst):
        if len(lst) == 0:
            return None
        smaller = self.trimList(self.trimList(lst, 1))
        total = 0
        for i in smaller:
            total+=smaller[i]
        rand = random.randint(0, total)
        for i in smaller:
            rand-=lst[i]
            if rand<=0:
                if (not (i == None)):
                    i.score = lst[i]
                return i
        return None
    
    def __str__(self):
        return self.word
        #return self.word+("(%s)"%self.score)

def loadFile(f):
    line = f.readline()
    i = 0
    while (line != ""):
        i+=1
        line = line.strip()
        if i % 2000 == 0:
            print "\r%s"%i
        text = prog.search(line)
        if text != None:
            text = text.group(1)
            prev = None
            for word in text.split(' '):
                if word == "":
                    continue
                word = g.getWord(word)
                if word != None:
                    word.addPrev(prev)
                if prev != None:
                    prev.addNext(word)
                prev = word
        line = f.readline()

prog = re.compile("^\[.*?\] \[.*?\] <.*?>(.*)$")
g = Graph()

for log in os.listdir("/home/trever/logs/"):
    print "Loading %s"%log
    f = open("/home/trever/logs/"+log)
    loadFile(f)

print "Ready."
while True:
    word = sys.stdin.readline().strip()
    if word == "":
        continue
    word = g.getWord(word)
    next = word.getNext()
    prev = word.getPrev()
    ret = str(word)
    while prev != None:
        ret=str(prev)+" "+ret
        prev = prev.getPrev()
    while next != None:
        ret=ret+" "+str(next)
        next = next.getNext()
    
    print ret