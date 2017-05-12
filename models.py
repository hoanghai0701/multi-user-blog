from google.appengine.ext import db
from helpers import *
import re
    
class User(db.Model):
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


class Post(db.Model):
    title = db.StringProperty(required=True)
    subtitle = db.StringProperty(required=False)
    content = db.TextProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(User, collection_name='posts', required=True)

    @classmethod
    def post_key(cls, name='default'):
        return db.Key.from_path('posts', name)


class Comment(db.Model):
    user = db.ReferenceProperty(User, required=True, collection_name='comments')
    post = db.ReferenceProperty(Post, required=True, collection_name='comments')
    content = db.TextProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def comment_key(cls, post_key, name='default'):
        return db.Key.from_path('comments', name, parent=post_key)
