from handler import *


class AuthenticationHandler(Handler):
    def register(self):
        self.render('register.html')

    def login(self):
        self.render('login.html')

    def logout(self):
        self.unset_cookie_user_id()
        self.redirect('/')