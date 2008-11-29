# -*- coding: utf-8 -*-
from Pointything.Database import *

class User:
    def __init__(self, id):
        db = Database();
        u = db.find("users", "user_id", id)
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
        db = Database();
        u = db.query("select user_id from users where login = ? and password = ?", (login, password))
        u = u.fetchone()
        if u == None:
            return User(0)
        else:
            return User(u['user_id'])