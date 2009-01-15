# -*- coding: utf-8 -*-
r"""An object-oriented database abstraction layer.

The Database module is meant to provide an easy way to essentially
write your database's schema right into your python code. It is best explained with an example:

import Database
class UserTable(Database.Table):
    def __init__(self):
        Database.Table.__init__(self, "users")
        self.addField(Database.Fields.Integer("user_id").addConstraint(Database.Constraints.PrimaryKey()).addConstraint(Database.Constraints.AutoIncrement()))
        self.addField(Database.Fields.Text("login"))
        self.addField(Database.Fields.Text("password"))

print repr(UserTable())

The output of this is valid SQL you can pass right into your favorite
sql engine's query() function.

More advanced SQL is possible as well:

from Database import *

class MarkovWordTable(Table):
    def __init__(self):
        Table.__init__(self, "markov_words")
        self.addField(
            Fields.Integer("wid")
            .addConstraint(Constraints.PrimaryKey())
            .addConstraint(Constraints.AutoIncrement())
            .addConstraint(Constraints.ForeignKey(MarkovLinkTable().field("from"),
                                                   (
                                                        Constraints.ForeignKeyAction("delete", "cascade")
                                                   )
                                                   ))
            .addConstraint(Constraints.ForeignKey(MarkovLinkTable().field("to"),
                                                   (
                                                        Constraints.ForeignKeyAction("delete", "cascade")
                                                   )
                                                   ))
            )
        self.addField(Fields.Text("word"))

This creates a table named "markov_words" with two fields. The integer "wid" field
is a primary key with autoincrement and two foreign keys. The keys exist in the Link table
and are set to cascade on delete.

Querying with a table object is remarkably simple as well:

tbl = UserTable()
u = tbl.select(tbl.fields(), (Database.Matches.Equals(tbl["user_id"], id),))

This essentially evaluates to "SELECT * FROM users WHERE user_id == $id"

"""

import sqlite3
import logging
import Fields, Constraints, Matches

'''Using repr() on a database object returns valid SQL.'''

class Table:
    """Represents a table in a sql database"""
    def __init__(self, name):
        self.log = logging.getLogger("Pointything.Database.%s"%name)
        self.name = name
        self._fields = {}
        self.schemaReady = False
        self.depends = []
        self.db = Database()
        self.db.addTable(self)
        
    def create(self):
        if self.schemaReady:
            return
        else:
            for d in self.depends:
                d.create()
            self.db.createTable(self)
            self.schemaReady = True
    
    def addDependency(self, other):
        self.depends.append(other)
    
    def addField(self, field):
        """Adds a field to the table's schema"""
        field.table = self
        self._fields.update({field.name: field})
        for d in field.foreignTables:
            self.addDependency(d)
        self.schemaReady = False
        return field
        
    def field(self, name):
        """Returns the named field"""
        return self._fields[name]
    
    def fields(self):
        """Returns all registered fields"""
        return self._fields.values()
        
    def __getitem__(self, name):
        """Returns the named field"""
        return self.field(name)
    
    def select(self, *args, **kwargs):
        """See Database.select for usage."""
        return self.db.select(self, *args, **kwargs)
    
    def insert(self, *args, **kwargs):
        """See Database.insert for usage."""
        return self.db.insert(self, *args, **kwargs)
    
    def update(self, *args, **kwargs):
        return self.db.update(self, *args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        """Creates the CREATE TABLE ... sql"""
        sql = "create table if not exists %s"%self.name
        fields = []
        for f in self._fields.values():
            fields.append(repr(f))
        sql += " ( "+(", ".join(fields))+" )"
        return sql

class Database:
    """Represents a database connection"""
    connection = None
    alltables = {}
    def __init__(self):
        self.log = logging.getLogger("Pointything.Database")
        self.log.debug("Connecting to database")
        if Database.connection == None:
            Database.connection = sqlite3.connect("/home/trever/Projects/Pointything5/database")
            Database.connection.row_factory = sqlite3.Row
    
    def tables(self):
        return Database.alltables
    
    def table(self, name):
        return Database.alltables[name]
        
    def addTable(self, table):
        Database.alltables[table.name] = table
    
    def createTable(self, table):
        """Executes the table's CREATE sql"""
        self.log.debug("Creating table: %s"%(repr(table)))
        try:
            self.query(repr(table))
            #self.log.info("Created table %s"%(table.name))
        except sqlite3.OperationalError:
            self.__db().rollback()
            return False
        return True
    
    def __db(self):
        return Database.connection
    
    def query(self, q, *args):
        """Runs a raw query on the database connection. If you have to use this, its a bug."""
        self.log.debug("Running query %s %% %s", q, args)
        c = self.__db().cursor()
        try:
            c.execute(q, args)
        except Exception, msg:
            self.log.error("Exception during SQL: %s", msg)
            raise msg
        return c
    
    def select(self, table, fields, matches):
        """Runs a SELECT <fields> FROM <table> WHERE <matches>"""
        table.create()
        compares = []
        values = []
        for f in matches:
            compares.append(repr(f))
            values.append(str(f.field.cast(f.value)))
        #TODO: ANDs and ORs
        sql = "select %s from %s where %s"%(reduce(lambda x,y:str(x)+", "+str(y), fields), table.name, " AND ".join(compares))
        return self.query(sql, *values)
    
    def insert(self, table, **fields):
        """Runs INSERT INTO <table> <fields> VALUES <values>
        Pass in a set of keyword arguments of field=value."""
        table.create()
        parsedValues = []
        fieldNames = []
        for fieldName,value in fields.iteritems():
            field = table.field(fieldName)
            parsedValues.append(field.cast(value))
            fieldNames.append(fieldName)
        sql = "insert into %s (%s) values (%s)"%(table.name, reduce(lambda x,y:str(x)+", "+str(y), fieldNames), ','.join(['?']*len(parsedValues)))
        return self.query(sql, *parsedValues)
    
    def update(self, table, conditions, **values):
        """Runs UPDATE <table> <values> WHERE <conditions>
        Pass in a set of keyword arguments of field=newValue
        """
        table.create()
        parsedValues = []
        fieldNames = []
        for fieldName,value in values.iteritems():
            field = table.field(fieldName)
            parsedValues.append(field.cast(value))
            fieldNames.append(fieldName+"=?")
        
        compares = []
        values = []
        for f in conditions:
            compares.append(repr(f))
            values.append(str(f.field.cast(f.value)))
        
        sql = "update %s set %s where %s"%(table.name, ", ".join(fieldNames) , " AND ".join(compares))
        queryValues = parsedValues+values
        #sql = "update %s set (%s) where (%s)"%(table.name, reduce(lambda x,y:str(x)+", "+str(y), fieldNames), ','.join(['?']*len(parsedValues)))
        return self.query(sql, *queryValues)