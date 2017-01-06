# twitter_rest.py
# Twitter Rest APIs - Search API

import sys
import tweepy as twp
import twitter_credentials as t_cr
import twitter_settings as t_s

# Twitter Rest APIs
# Twitter Search API
class TwitterRest():
    def __init__(self):
        self.authenticate_twitter_app()
        if (not self.api):
            print ("Can't Authenticate")
            sys.exit(-1)

    # Authenticate as Application-only
    # Limits:   450 requests per 15 mins window
    #           Up to 100 tweets per requests
    #           Total: 45,000 tweets per 15 mins
    def authenticate_twitter_app(self):
        auth = twp.AppAuthHandler(t_cr.consumer_key, t_cr.consumer_secret)
        api = twp.API( auth,
                            wait_on_rate_limit=True,
    				        wait_on_rate_limit_notify=True)
        self.api = api

    # Begin tweet collection
    def search_twitter(self):
        last_id = -1
        while True:
            try:
                tweets = self.api.search( q=t_s.query,count=100,lang=t_s.language,max_id=str(last_id - 1))
                if not tweets:
                    break
                for tweet in tweets:
                    self.process_status(tweet)
                last_id = tweets[-1].id
            except twp.TweepError as e:
                break

    def process_status(self,status):
        pass
