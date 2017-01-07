# tweets.py
# Database Model for new Twitter Statuses

from google.appengine.ext import ndb

class TwitterStatus(ndb.Model):
    text = ndb.TextProperty()
    date = ndb.DateTimeProperty()
    userid = ndb.StringProperty()
    tweetid = ndb.StringProperty()
    location = ndb.GeoPtProperty()
    sentiment = ndb.IntegerProperty()
    words = ndb.StringProperty(repeated=True)
