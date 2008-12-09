# -*- coding: utf-8 -*-
import sqlite3
import logging
import Fields, Constraints, Matches

'''Using repr() on a database object returns valid SQL.'''

instance = None

def instance():
    if (instance == None):
        instance = Database()
    return instance

class Table:
    def __init__(self, name):
        self.log = logging.getLogger("Pointything.Database.%s"%name)
        self.db = Database()
        self.name = name
        self._fields = {}
        
    def addField(self, field):
        field.table = self
        self._fields.update({field.name: field})
        return field
        
    def field(self, name):
        return self._fields[name]
    
    def fields(self):
        return self._fields.values()
        
    def __getitem__(self, name):
        return self.field(name)
    
    def select(self, *args, **kwargs):
        return self.db.select(self, *args, **kwargs)
    
    def __repr__(self):
        sql = "create table %s"%self.name
        sql += " ( "+reduce((lambda x,y:repr(x)+", "+repr(y.schema())), self._fields.values())+" )"
        return sql

class Database:
    connection = None
    def __init__(self):
        self.log = logging.getLogger("Pointything.Database")
        self.log.debug("Connecting to database")
        if Database.connection == None:
            Database.connection = sqlite3.connect("/home/trever/Projects/Pointything5/database")
            Database.connection.row_factory = sqlite3.Row
        
    
    def createTable(self, table):
        c = self.db().cursor()
        try:
            c.execute(table.schema())
            self.db().commit()
            self.log.info("Created table %s"%(table.name))
        except sqlite3.OperationlError:
            self.db().rollback()
            return false
        return true
    
    def db(self):
        return Database.connection
    
    def query(self, q, *args):
        self.log.debug("Running query %s (%s)", q, args)
        c = self.db().cursor()
        c.execute(q, args)
        self.db().commit()
        return c
    
    def select(self, table, fields, matches):
        sql = "select %s from %s where %s"%(reduce(lambda x,y:str(x)+", "+str(y), fields), table.name, reduce(lambda x,y:str(x)+" "+str(y), matches))
        c = self.db().cursor()
        c.execute(sql)
        return c