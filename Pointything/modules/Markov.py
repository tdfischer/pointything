# -*- coding: utf-8 -*-
import random
import re

from Pointything.Extensions import *
from Database import *
class MarkovWordTable(Table):
    def __init__(self):
        Table.__init__(self, "markov_words")
        self.addField(
            Fields.Integer("wid")
            .addConstraint(Constraints.PrimaryKey())
            .addConstraint(Constraints.AutoIncrement())
            .addConstraint(Constraints.ForeignKey(MarkovLinkTable().field("fromWord"),
                                                   (
                                                        Constraints.ForeignKeyAction("delete", "cascade")
                                                   )
                                                   ))
            .addConstraint(Constraints.ForeignKey(MarkovLinkTable().field("toWord"),
                                                   (
                                                        Constraints.ForeignKeyAction("delete", "cascade")
                                                   )
                                                   ))
            )
        self.addField(Fields.Text("word"))

class MarkovLinkTable(Table):
    def __init__(self):
        Table.__init__(self, "markov_links")
        self.addField(Fields.Integer("fromWord").addConstraint(Constraints.Key()))
        self.addField(Fields.Integer("toWord").addConstraint(Constraints.Key()))
        self.addField(Fields.Integer("count"))

class Markov(Extension):
    '''An implementation of a markov chain phrase generator.'''
    def __init__(self, bot):
        Extension.__init__(self, bot)
        self.words = MarkovWordTable()
        self.links = MarkovLinkTable()
    
    def __str__(self):
        return "Markov chain speech generator"
    
    @Action
    def describe(self, input, word):
        '''Attempts to build a sentence given some suggested word'''
        ret = word
        startID = self.getWordByStr(word)
        if startID == None:
            return
        word = self.getNextWord(startID["wid"])
        while word != None:
            word = self.getWordById(word["toWord"])
            self.log.debug("Next word: %s",word["word"])
            ret+=" "+str(word["word"])
            word = self.getNextWord(word["wid"])
        self.log.debug("Built sentence: %s", ret)
        return ret
    
    def getWordByStr(self, word):
        return self.words.select((self.words["wid"], self.words["word"]), (Matches.Equals(self.words["word"], word),)).fetchone()
    
    def getWordById(self, wid):
        return self.words.select((self.words["wid"], self.words["word"],), (Matches.Equals(self.words["wid"], wid), )).fetchone()
    
    def getNextWord(self, word):
        words = self.links.select((self.links["toWord"], self.links["count"], self.links["fromWord"]), (Matches.Equals(self.links["fromWord"], word),)).fetchall()
        return self.getRandom(words)
        
    def getRandom(self, lst):
        if len(lst) == 0:
            return None
        #smaller = self.trimList(self.trimList(lst, 1))
        total = 0
        for i in lst:
            if i["count"]==None:
                left = self.getWordById(i["fromWord"])
                right = self.getWordById(i["toWord"])
                self.log.warn("Found a link with strange count: %s->%s (%s)", left["word"], right["word"], i["count"])
            else:
                total+=i["count"]
        rand = random.randint(0, total)
        for i in lst:
            if i["count"] == None:
                pass
            else:
                rand-=i["count"]
            if rand<=0:
                return i
        return None
    
    def readBanter(self, input, user):
        previd = self.words.select((self.words["wid"],), (Matches.Equals(self.words["word"], None),)).fetchone()
        if previd == None:
            self.words.insert(word=None)
            previd = self.words.select((self.words["wid"],), (Matches.Equals(self.words["word"], None),)).fetchone()
        previd = previd["wid"]
        last = previd
        for w in input.split(' '):
            curid = self.words.select((self.words["wid"],), (Matches.Equals(self.words["word"], w),)).fetchone()
            if curid == None:
                self.words.insert(word=w)
                curid = self.words.select((self.words["wid"],), (Matches.Equals(self.words["word"], w),)).fetchone()["wid"]
            else:
                curid = curid["wid"]
            link = self.links.select((self.links["count"],), (Matches.Equals(self.links["fromWord"], previd), Matches.Equals(self.links["toWord"], curid))).fetchone()
            if link == None:
                self.links.insert(fromWord=previd, toWord=curid, count=1)
            else:
                self.links.update((Matches.Equals(self.links["fromWord"], previd), Matches.Equals(self.links["toWord"], curid)), count=int(link["count"])+1)
        link = self.links.select((self.links["count"],), (Matches.Equals(self.links["fromWord"], previd), Matches.Equals(self.links["toWord"], last))).fetchone()
        if link == None:
            self.links.insert(fromWord=curid, toWord=last, count=1)
        else:
            self.links.update((Matches.Equals(self.links["fromWord"], previd), Matches.Equals(self.links["toWord"], last)), count=int(link["count"])+1)