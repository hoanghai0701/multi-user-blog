from google.appengine.ext import db
from user import User
from post import Post


class Comment(db.Model):
    """
    For comment feature.
    """
    user = db.ReferenceProperty(User, required=True, collection_name='comments')
    post = db.ReferenceProperty(Post, required=True, collection_name='comments')
    content = db.TextProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def comment_key(cls, post_key, name='default'):
        return db.Key.from_path('comments', name, parent=post_key)
