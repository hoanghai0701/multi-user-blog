from handler import *
from utils.decorators import *


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

    @post_exists
    def show(self, post_id):
        post = self.data['post']
        like = None
        if hasattr(self, 'user'):
            like = post.likes.ancestor(Like.like_key()).filter('user = ', self.user).get()

        self.render('post-show.html', post=post, like=like)

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

    @post_permission
    @post_exists
    @authenticated
    def edit(self, post_id):
        post = self.data['post']
        self.render('post-edit.html', title=post.title,
                    subtitle=post.subtitle,
                    content=post.content,
                    post=post)

    @post_permission
    @post_exists
    @authenticated
    def update(self, post_id):
        post = self.data['post']

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

    @post_permission
    @post_exists
    @authenticated
    def delete(self, post_id):
        post = self.data['post']
        post.delete()
        self.redirect('/users/%s/posts' % str(self.user.key().id()))
