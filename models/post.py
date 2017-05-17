from google.appengine.ext import db
from user import User


class Post(db.Model):
    """
    Represent a post.
    """
    title = db.StringProperty(required=True)
    subtitle = db.StringProperty(required=False)
    content = db.TextProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(User, collection_name='posts', required=True)
    num_likes = db.IntegerProperty(default=0)

    @classmethod
    def post_key(cls, name='default'):
        return db.Key.from_path('posts', name)