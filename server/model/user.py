from google.appengine.ext import ndb


DEFAULT_USERNAME = 'admin'

def user_key(username=DEFAULT_USERNAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Login', username)
