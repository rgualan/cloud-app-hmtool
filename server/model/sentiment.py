# sentiment.py
# Database Model for Sentiment Calculation

from google.appengine.ext import ndb

class Weight(ndb.Model):
    word = ndb.StringProperty(indexed=True)
    weight = ndb.IntegerProperty(indexed=False)

class Sentiment(ndb.Model):
    date = ndb.DateTimeProperty(indexed=True)
    tweetid = ndb.StringProperty(indexed=False)
    text = ndb.StringProperty(indexed=True)
    sum_weight = ndb.IntegerProperty(indexed=False)

class Word(ndb.Model):
    word_date = ndb.DateProperty(indexed=True)
    word_text = ndb.StringProperty(indexed=True)
    word_sum_weight = ndb.IntegerProperty(indexed=False)

class Sum_Sentiment(ndb.Model):
    date = ndb.DateProperty(indexed=True)
    type = ndb.StringProperty(indexed=True)
    sum = ndb.IntegerProperty(indexed=False)

class Sum_Word(ndb.Model):
    date = ndb.DateProperty(indexed=True)
    word = ndb.StringProperty(indexed=True)
    sum = ndb.IntegerProperty(indexed=False)
