# -*- coding: utf-8 -*-
r"""Interface for the user subsystem authorization and management.

Normal extensions shouldn't be concerned with this module.
"""
import Database

class UserTable(Database.Table):
    """Contains users"""
    def __init__(self):
        Database.Table.__init__(self, "users")
        self.addField(Database.Fields.Integer("user_id").addConstraint(Database.Constraints.PrimaryKey()).addConstraint(Database.Constraints.AutoIncrement()))
        self.addField(Database.Fields.Text("login"))
        self.addField(Database.Fields.Text("password"))
        self.insert(login="Trever", password="Hi")

class User:
    """A representation of a Pointything user. Users that exist in the database are considered "valid"."""
    def __init__(self, id):
        tbl = UserTable()
        u = tbl.select(tbl.fields(), (Database.Matches.Equals(tbl["user_id"], id),))
        data = u.fetchone()
        self.data = {}
        for idx, cell in enumerate(u.description):
            self.data[cell[0]] = data[idx]
        self.invalid = (self.data == None)

    def __getitem__(self, item):
        return self.data[item]

    def isValid(self):
        return not self.invalid
    
    @staticmethod
    def login(login, password):
        """Returns a valid user if the credentials are correct, and an invalid one otherwise."""
        tbl = UserTable()
        u = tbl.select((tbl["user_id"],), (Database.Matches.Equals(tbl["login"], login), Database.Matches.Equals(tbl["password"], password)))
        u = u.fetchone()
        if u == None:
            return User(0)
        else:
            return User(u['user_id'])
