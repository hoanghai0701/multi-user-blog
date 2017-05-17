from google.appengine.ext import db
from user import User
from post import Post


class Like(db.Model):
    """
    For like feature.
    """
    user = db.ReferenceProperty(User, required=True, collection_name='likes')
    post = db.ReferenceProperty(Post, required=True, collection_name='likes')

    @classmethod
    def like_key(cls, name='default'):
        return db.Key.from_path('likes', name)
