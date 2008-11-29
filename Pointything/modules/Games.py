# -*- coding: utf-8 -*-
from Pointything.Extensions import *
import random

class EightBall(Extension):
    extension_name="8ball"
    
    ANSWERS=[
        "As I see it, yes",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "It is certain",
        "It is decidely so",
        "Most likely",
        "My reply is no",
        "My sources say no",
        "Outlook good",
        "Outlook not so good",
        "Reply hazy, try again",
        "Signs point to yes",
        "Very doubtful",
        "Without a doubt",
        "Yes",
        "Yes - definitely",
        "You may rely on it"
    ]
    @Action("8ball")
    def ball(self, input, *args):
        #i = random.randint(0, len(EightBall.ANSWERS))
        return "%s shook the 8ball and got: %s"%(input.user['login'], random.choice(EightBall.ANSWERS))