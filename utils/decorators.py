from models import *
from handlers.handler import AjaxHandler


def authenticated(func):
    """
    A decorator to redirect user to login page if not authenticated
    :param func: 
    :return: 
    """
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'user'):
            return self.redirect('/login')
        else:
            func(self, *args, **kwargs)

    return wrapper


def post_exists(func):
    """
    A decorator to pre-check if post exists, 
    and store it to handler if exists to avoid redundant request to DB
    :param func: 
    :return: 
    """
    def wrapper(self, *args, **kwargs):
        post_id = int(kwargs['post_id'])
        post = Post.get_by_id(post_id, parent=Post.post_key())

        if not post:
            if isinstance(self, AjaxHandler):
                return self.json({'error': 'Post not found'}, 404)
            else:
                return self.redirect('/')
        else:
            self.data['post'] = post
            func(self, *args, **kwargs)

    return wrapper


def comment_exists(func):
    """
    A decorator to pre-check if comment exists,
    and store it to handler if exists to avoid redundant request to DB
    :param func: 
    :return: 
    """
    def wrapper(self, *args, **kwargs):
        comment_id = int(kwargs['comment_id'])
        comment = Comment.get_by_id(comment_id, parent=Comment.comment_key(Post.post_key()))

        if not comment:
            return self.json({'error': 'Comment not found'})

        # If post_id is present, check if this comment belongs to this post
        if 'post_id' in kwargs:
            if 'post' in self.data:
                post = self.data['post']
            else:
                post = Post.get_by_id(int(kwargs['post_id']), Post.post_key())

            if comment.post.key().id() != post.key().id():
                return self.json({'error': 'This comment does not belong to this post'}, 400)

        self.data['comment'] = comment
        func(self, *args, **kwargs)

    return wrapper


def comment_permission(func):
    """
    A decorator to check if logged in user owns this comment
    :param func: 
    :return: 
    """
    def wrapper(self, *args, **kwargs):
        if 'comment' in self.data:
            comment = self.data['comment']
        else:
            comment_id = int(kwargs['comment_id'])
            comment = Comment.get_by_id(comment_id, parent=Comment.comment_key(Post.post_key()))

        if comment.user.key().id() != self.user.key().id():
            return self.json({'error': 'You are not permitted to this comment'}, 403)

        func(self, *args, **kwargs)

    return wrapper


def post_permission(func):
    """
    A decorator to check if logged in user has permission to modify or delete post
    :param func: 
    :return: 
    """
    def wrapper(self, *args, **kwargs):
        if 'post' in self.data:
            post = self.data['post']
        else:
            post_id = int(kwargs['post_id'])
            post = Post.get_by_id(post_id, parent=Post.post_key())

        if post.user.key().id() != self.user.key().id():
            return self.redirect('/')
        else:
            func(self, *args, **kwargs)

    return wrapper
