import logging
from twitter_rest import TwitterRest
from google.appengine.ext import ndb
# import requests_toolbelt.adapters.appengine
# requests_toolbelt.adapters.appengine.monkeypatch()

class TwitterStatus(ndb.Model):
    text = ndb.TextProperty()
    date = ndb.DateTimeProperty()
    userid = ndb.StringProperty()
    tweetid = ndb.StringProperty()
    location = ndb.GeoPtProperty()

class TwitterRestGAE(TwitterRest):

    tweets_count = 0

    def __init__(self):
        TwitterRest.__init__(self)

    def process_status(self,status):
        self.tweets_count += 1
        logging.debug( "Processing Tweet #" + str(self.tweets_count) )
        if status.coordinates != None:
            geo = status.coordinates['coordinates']
            geo = ndb.GeoPt(geo[1], geo[0])
        else:
            geo = None
        twitter_status = TwitterStatus(
            text = status.text,
            date = status.created_at,
            userid = status.user.id_str,
            tweetid = status.id_str,
            location = geo,
        )
        twitter_status_key = twitter_status.put()
