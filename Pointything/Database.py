# -*- coding: utf-8 -*-
import sqlite3
import logging

class Database:
    staticDB = None
    def __init__(self):
        self.log = logging.getLogger("Pointything.Database")
        self.log.debug("Connecting to database")
        if Database.staticDB == None:
            Database.staticDB = sqlite3.connect("/home/trever/Projects/Pointything5/database")
            Database.staticDB.row_factory = sqlite3.Row
        
        self.log.debug("Creating tables")
        c = self.db().cursor()
        try:
            c.execute('''create table if not exists users (user_id integer primary key autoincrement, login text, password text)''')
            #c.execute('''insert into users (login, password) values ('trever', '')''')
            self.db().commit()
            self.log.info("Created tables")
        except sqlite3.OperationalError:
            self.log.debug("Tables already exist")
            self.db().rollback()
        
    def db(self):
        return Database.staticDB
    
    def query(self, q, *args):
        self.log.debug("Running query %s (%s)", q, args)
        c = self.db().cursor()
        c.execute(q, args)
        self.db().commit()
        return c
    
    def find(self, table, field, value):
        self.log.debug("Searching for %s==%s in %s", field, value, table)
        c = self.db().cursor()
        c.execute('select * from %s where %s == ?' % (table, field), (value,))
        return c