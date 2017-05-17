import json
import os

import jinja2
import webapp2

from utils.helpers import *
from models import *

base_path = os.path.dirname(os.path.dirname(__file__))
template_dir = os.path.join(base_path, 'resources', 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


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

        self.data = {}

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
