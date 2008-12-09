# -*- coding: utf-8 -*-
import Database

class UserTable(Database.Table):
    def __init__(self):
        Database.Table.__init__(self, "users")
        self.addField(Database.Fields.Integer("user_id").addConstraint(Database.Constraints.PrimaryKey()).addConstraint(Database.Constraints.AutoIncrement()))
        self.addField(Database.Fields.Text("login"))
        self.addField(Database.Fields.Text("password"))

class User:
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
        tbl = UserTable()
        u = tbl.select((tbl["user_id"],), (Database.Matches.Equals(tbl["login"], login), Database.Matches.Equals(tbl["password"], password)))
        u = u.fetchone()
        if u == None:
            return User(0)
        else:
            return User(u['user_id'])