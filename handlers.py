import webapp2
import jinja2
import os
from models import *
from helpers import *
import json

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


def authenticated(func):
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'user'):
            return self.redirect('/login')
        else:
            func(self, *args, **kwargs)

    return wrapper


class Handler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(Handler, self).initialize(request, response)
        user_id = self.request.cookies.get('user_id')

        if user_id:
            user_id = validate_secure_cookie(user_id)
            if user_id and user_id.isdigit():
                user = User.get_by_id(int(user_id))
                if user:
                    self.user = user

    def render(self, template, **kwargs):
        t = jinja_env.get_template(template)

        # For authenticated checking
        if hasattr(self, 'user'):
            kwargs['user'] = self.user

        content = t.render(**kwargs)
        self.response.write(content)

    def set_cookie_user_id(self, user):
        self.response.headers.add_header('Set-cookie', 'user_id=%s; Path=/' % make_secure_cookie(user.key().id()))

    def unset_cookie_user_id(self):
        self.response.headers.add_header('Set-cookie', 'user_id=; Path=/')


class AjaxHandler(Handler):
    def initialize(self, request, response):
        super(AjaxHandler, self).initialize(request, response)
        self.response.content_type = 'application/json'

    def json(self, obj, status_code):
        self.response.status = status_code
        self.response.write(json.dumps(obj))


class UserHandler(Handler):
    def store(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        user, error = User.register(username, password, verify)

        if not user:
            self.render('register.html', username=username,
                        password=password,
                        verify=verify,
                        error=error)
        else:
            self.set_cookie_user_id(user)
            self.redirect('/')

    def login(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.all().filter('username = ', username).get()
        if not user:
            return self.render('login.html', username=username,
                               password=password,
                               error='Username or password is not correct, please try again')
        if not validate_secure_password(password, user.password):
            return self.render('login.html', username=username,
                               password=password,
                               error='Username or password is not correct, please try again')

        self.set_cookie_user_id(user)
        self.redirect('/')

    def posts(self, user_id):
        if not user_id.isdigit():
            return self.redirect('/')

        user_id = int(user_id)
        user = User.get_by_id(user_id)

        if not user:
            return self.redirect('/')

        page = self.request.get('page', 0)

        try:
            page = int(page)
        except Exception:
            page = 0

        limit = 5
        posts = user.posts.ancestor(Post.post_key()).order('-created_at').fetch(limit=limit + 1, offset=limit * page)

        if len(posts) == limit + 1:
            no_more = False
            posts = posts[:limit]
        else:
            no_more = True

        self.render('user-post-index.html', posts=posts, page=page, no_more=no_more, owner=user)


class AuthenticationHandler(Handler):
    def register(self):
        self.render('register.html')

    def login(self):
        self.render('login.html')

    def logout(self):
        self.unset_cookie_user_id()
        self.redirect('/')


class PostHandler(Handler):
    @authenticated
    def create(self):
        self.render('post-create.html')

    @authenticated
    def store(self):
        title = self.request.get('title')
        subtitle = self.request.get('subtitle')
        content = self.request.get('content')

        if not (title and content):
            self.render('post-create.html', title=title,
                        subtitle=subtitle,
                        content=content,
                        error='Both title and content are required')
        else:
            post = Post(parent=Post.post_key(), title=title, subtitle=subtitle, content=content, user=self.user)
            post.put()
            self.redirect('/posts/' + str(post.key().id()))

    def show(self, post_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())
        if not post:
            return self.redirect('/')
        else:
            self.render('post-show.html', post=post)

    def index(self):
        page = self.request.get('page', 0)
        try:
            page = int(page)
        except Exception:
            page = 0

        limit = 5
        # Fetch limit + 1 to check if next page exists
        posts = Post.all().order("-created_at").fetch(limit=limit + 1, offset=limit * page)

        if len(posts) == limit + 1:
            no_more = False
            posts = posts[:limit]
        else:
            no_more = True

        self.render('post-index.html', posts=posts, page=page, no_more=no_more)

    @authenticated
    def edit(self, post_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())

        if not post:
            return self.redirect('/')
        else:
            if post.user.key().id() != self.user.key().id():
                return self.redirect('/')
            self.render('post-edit.html', title=post.title,
                        subtitle=post.subtitle,
                        content=post.content,
                        post=post)

    @authenticated
    def update(self, post_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())

        if not post:
            return self.redirect('/')
        else:
            if post.user.key().id() != self.user.key().id():
                return self.redirect('/')
            title = self.request.get('title')
            subtitle = self.request.get('subtitle')
            content = self.request.get('content')

            if not (title and content):
                self.render('post-edit.html', title=title,
                            subtitle=subtitle,
                            content=content,
                            post=post,
                            error="Both title and content are required")
            else:
                post.title = title
                post.subtitle = subtitle
                post.content = content
                post.put()
                self.redirect('/posts/' + str(post.key().id()))

    @authenticated
    def delete(self, post_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())

        if not post:
            return self.redirect('/users/%s/posts' % str(self.user.key().id()))
        else:
            post.delete()
            self.redirect('/users/%s/posts' % str(self.user.key().id()))


# This handler only serves ajax request
class CommentHandler(AjaxHandler):
    def index(self, post_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())
        page = self.request.get('page', 0)
        page = int(page)
        limit = 5

        if not post:
            return self.json({'error': 'Post not found'}, 404)
        else:
            comments = post.comments \
                .ancestor(Comment.comment_key(Post.post_key())) \
                .order("-created_at").fetch(limit=limit, offset=limit * page)

            comments = [to_json(comment) for comment in comments]
            return self.json(comments, 200)

    def store(self, post_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())
        body = self.request.json
        content = body['content']

        if not post:
            return self.json({'error': 'Post not found'}, 404)
        else:
            comment = Comment(user=self.user, post=post, content=content, parent=Comment.comment_key(Post.post_key()))
            comment.put()
            return self.json({'msg': 'Comment successfully', 'data': to_json(comment)}, 200)

    def update(self, post_id, comment_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())
        body = self.request.json
        content = body['content']

        if not post:
            return self.json({'error': 'Post not found'}, 404)
        else:
            comment_id = int(comment_id)
            comment = Comment.get_by_id(comment_id, parent=Comment.comment_key(Post.post_key()))
            if comment.post.key().id() != post.key().id():
                return self.json({'error': 'This comment does not belong to this post'}, 400)
            else:
                comment.content = content
                comment.put()
                return self.json({'msg': 'Comment updated successfully', 'data': to_json(comment)}, 200)
