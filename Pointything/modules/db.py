# -*- coding: utf-8 -*-
from Pointything.Extensions import *
import Database as p_db

class Database(Extension):
    
    @Action
    def tables(self, input, *args):
        db = p_db.Database()
        return "Loaded tables: "+", ".join(db.tables().keys())
