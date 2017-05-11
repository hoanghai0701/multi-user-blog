#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

routes = [
    webapp2.Route(r'/', handler='handlers.PostHandler:index', methods=['GET'], name='post-index'),
    webapp2.Route(r'/register', handler='handlers.AuthenticationHandler:register', methods=['GET'], name='register'),
    webapp2.Route(r'/register', handler='handlers.UserHandler:store', methods=['POST']),
    webapp2.Route(r'/login', handler='handlers.AuthenticationHandler:login', methods=['GET'], name='login'),
    webapp2.Route(r'/login', handler='handlers.UserHandler:login', methods=['POST']),
    webapp2.Route(r'/logout', handler='handlers.AuthenticationHandler:logout', methods=['GET'], name='logout'),
    webapp2.Route(r'/posts/create', handler='handlers.PostHandler:create', methods=['GET'], name='post-create'),
    webapp2.Route(r'/posts/create', handler='handlers.PostHandler:store', methods=['POST']),
    webapp2.Route(r'/posts/<post_id:\d+>', handler='handlers.PostHandler:show', methods=['GET']),
    webapp2.Route(r'/users/<user_id:\d+>/posts', handler='handlers.UserHandler:posts', methods=['GET'])
]

app = webapp2.WSGIApplication(routes, debug=True)