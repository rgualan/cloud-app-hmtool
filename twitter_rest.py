import sys
import tweepy as twp
import twitter_credentials as t_cr
import twitter_settings as t_s

class TwitterRest():
    def __init__(self):
        self.authenticate()

    def authenticate(self):
        self.authenticate_twitter_app()
        if (not self.api):
            print ("Can't Authenticate")
            sys.exit(-1)

    def authenticate_twitter_user(self):
        auth = twp.OAuthHandler(t_cr.consumer_key, t_cr.consumer_secret)
        auth.set_access_token(t_cr.access_token, t_cr.access_token_secret)
        api = twp.API(auth)
        self.api = api

    def authenticate_twitter_app(self):
        auth = twp.AppAuthHandler(t_cr.consumer_key, t_cr.consumer_secret)
        api = twp.API( auth,
                            wait_on_rate_limit=True,
    				        wait_on_rate_limit_notify=True)
        self.api = api

    def get_search_rate_limit(self):
        return self.api.rate_limit_status()['resources']['search']['/search/tweets']

    def get_app_rate_limit(self):
        return self.api.rate_limit_status()['resources']['application']\
        ['/application/rate_limit_status']

    def search_twitter(self):
        self.search_twitter_manual()

    def search_twitter_manual(self):
        last_id = -1
        while True:
            try:
                tweets = self.api.search( q=t_s.query,
                    count=100,
                    lang=t_s.language,
                    max_id=str(last_id - 1))
                if not tweets:
                    break
                for tweet in tweets:
                    self.process_status(tweet)
                last_id = tweets[-1].id
            except twp.TweepError as e:
                break

    def search_twitter_cursor(self):
        tweets_cursor = twp.Cursor( self.api.search,
            q=t_s.query,
            lang=t_s.language,
            count=100)
        for status in tweets_cursor.items():
            self.process_status(status)

    def process_status(self,status):
        pass

if __name__ == '__main__':
    twitter_rest = TwitterRest()
    twitter_rest.search_twitter()
