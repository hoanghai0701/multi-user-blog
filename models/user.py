import re
from utils.helpers import *


class User(db.Model):
    """
    Represent an user.
    """
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    hidden = ['password']

    @classmethod
    def register(cls, username, password, verify):
        user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        password_re = re.compile(r"^.{3,20}$")
        error = {
            'username': [],
            'password': [],
            'verify': []
        }

        fails = False
        if not user_re.match(username):
            error['username'].append('This username is not valid')
            fails = True
        if cls.all().filter('username = ', username).get():
            error['username'].append('This username is already taken')
            fails = True
        if not password_re.match(password):
            error['password'].append('This password is not valid')
            fails = True
        if verify != password:
            error['verify'].append('Password confirmation does not match')
            fails = True

        user = None
        if not fails:
            user = cls(username=username, password=make_secure_password(password))
            user.put()

        return user, error
