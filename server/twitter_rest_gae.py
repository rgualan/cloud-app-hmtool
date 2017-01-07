# twitter_rest_gae.py
# Twitter Rest APIs - Search API
# Save tweets in Google Datastore

import logging
from twitter_rest import TwitterRest
from google.appengine.ext import ndb
import twitter_settings as t_s
from model.tweets import TwitterStatus
# Configure requests library to use URLFetch
# Tweepy library is using requests
# https://cloud.google.com/appengine/docs/python/issue-requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()

# Extend TwitterRest class
# Save new tweets in Google Datastore
class TwitterRestGAE(TwitterRest):

    tweets_count = 0

    def __init__(self):
        TwitterRest.__init__(self)

    # Save each tweet in Datastore
    def process_status(self,status):
        if t_s.tweets_limit == self.tweets_count:
            return False
        self.tweets_count += 1
        logging.debug( "Processing Tweet #" + str(self.tweets_count) )
        if status.coordinates != None:
            geo = status.coordinates['coordinates']
            geo = ndb.GeoPt(geo[1], geo[0])
        else:
            if t_s.tweets_only_geo == True:
                return True
            geo = None
        twitter_status = TwitterStatus(text = status.text,date = status.created_at,
            userid = status.user.id_str,tweetid = status.id_str,location = geo,
        )
        twitter_status_key = twitter_status.put()
        return True
