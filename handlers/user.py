from handler import *


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