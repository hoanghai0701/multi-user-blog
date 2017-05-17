import hmac
import hashlib
import datetime
from google.appengine.ext import db

secret = 'OMG_I_AM_SO_SECRET'


def hash_str(s):
    return hmac.new(secret, s).hexdigest()


def make_secure_cookie(s):
    s = str(s)
    return '%s|%s' % (s, hash_str(s))


def validate_secure_cookie(h):
    s = h.split('|')[0]
    hashed_s = make_secure_cookie(s)
    if hashed_s == h:
        return s
    else:
        return None


def gen_salt(length=5):
    import random
    import string
    return ''.join(random.choice(string.letters) for i in xrange(length))


def make_secure_password(pw, salt=None):
    if not salt:
        salt = gen_salt()

    return '%s|%s' % (hashlib.sha256(pw + salt).hexdigest(), salt)


def validate_secure_password(pw, h):
    parts = h.split('|')
    salt = parts[len(parts) - 1]
    return make_secure_password(pw, salt) == h


simple_types = [int, long, float, bool, dict, basestring, list, unicode]


def to_json(obj):
    output = {}

    for key, prop in obj.properties().iteritems():
        # Skip hidden properties
        if hasattr(obj, 'hidden') and (key in obj.hidden or key == 'hidden'):
            continue

        value = getattr(obj, key)

        for t in simple_types:
            if isinstance(value, t):
                output[key] = value
                break

        if type(value) is datetime.datetime:
            output[key] = value.strftime("%Y-%m-%d")
        elif isinstance(value, db.Model):
            output[key] = to_json(value)

    output['_id'] = obj.key().id()
    return output

