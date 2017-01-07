# twitter_rest_gae.py
# Twitter Rest APIs - Search API
# Save tweets in Google Datastore

import logging
from twitter_rest import TwitterRest
from google.appengine.ext import ndb
import twitter_settings as t_s
from model.tweets import TwitterStatus
from sentiment_calculation import calculate_a_tweet as calc_sent
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
        if self.tweets_count and t_s.tweets_limit == self.tweets_count:
            return False

        if status.coordinates != None:
            geo = status.coordinates['coordinates']
            geo = ndb.GeoPt(geo[1], geo[0])
        else:
            if t_s.tweets_only_geo == True:
                return True
            geo = None
            
        sent_result = calc_sent(status.text.encode('utf-8'))
        twitter_status = TwitterStatus(text = status.text,date = status.created_at,
            userid = status.user.id_str,tweetid = status.id_str,location = geo,
            sentiment = sent_result['sentiment'], words=sent_result['words']
        )
        twitter_status_key = twitter_status.put()
        self.tweets_count += 1
        logging.debug( "Processed Tweet #" + str(self.tweets_count) )
        return True
