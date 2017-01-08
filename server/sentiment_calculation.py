import re
import re
import string
import csv
import random
import logging
from datetime import datetime
from server.settings import *
from server.model import tweets, sentiment
from google.appengine.ext import ndb


def get_weight_dictionary():
    csv_file = PROJECT_DIR+'/../data/dictionary.csv'

    with open(csv_file, 'rb') as csvfile:
        cursor = csv.reader(csvfile, delimiter=';')
        next(cursor, None)

        data = {}
        for row in cursor:
            data[row[0]] = row[1]

    return data


dictWords = get_weight_dictionary()


def calculate_a_tweet(tweet):
    total_weight = 0
    list_of_words = []

    sentence = tweet.split()
    for word in sentence:
        #check if it is url, ignore if yes.
        h = re.match('(.*)http.*$', word)
        u = re.match('(.*)\.com.*$', word)

        if h is None and u is None:
            #this part is to remove all symbols and turn them into whitespace
            chars_to_remove = ['"', '!', '#', '.', ',', '?', '@', ':', '~', '*', "'", '\/', '(' ,')', '-', '=']
            specials = ''.join(chars_to_remove)
            trans = string.maketrans(specials, ' '*len(specials))
            remove_symbols = word.translate(trans)
            word = remove_symbols.strip()

            #dict = sentiment.Weight.query().filter(sentiment.Weight.word == word)
            weight = dictWords.get(word.lower(), None)

            if weight:
                total_weight = total_weight + int(weight)
                list_of_words.append(word.lower())

    return {'sentiment': total_weight, 'words': list_of_words}

def summarize_sentiment():

    #ndb.delete_multi(sentiment.Sum_Sentiment.query().fetch(keys_only=True))
    #ndb.delete_multi(sentiment.Sum_Word.query().fetch(keys_only=True))

    q_sentiment = tweets.TwitterStatus.query().fetch()
    t = tweets.TwitterStatus
    q_sentiment = tweets.TwitterStatus.query().order(-t.date).fetch(1000)
    counter = 0
    records = []
    word_records = []

    for s in q_sentiment:
        #logging.info(str(s.date.date()) + ' - ' + str(datetime.today().date()))
        type = ''
        if s.sentiment > 0: type = 'positive'
        elif s.sentiment < 0: type = 'negative'
        else: type = 'neutral'

        if len(records) > 0:
            check = True
            for each in records:
                if s.date.date() == each.date and each.type == type:
                    each.sum = each.sum + 1
                    check = False
                    pass

            if check:
                record = sentiment.Sum_Sentiment(date=s.date.date(), type=type, sum=1)
                records.append(record)
        else:
            record = sentiment.Sum_Sentiment(date=s.date.date(), type=type, sum=1)
            records.append(record)

        q_word = s.words
        for w in q_word:
            if len(word_records) > 0:
                check = True
                for each in word_records:
                    if w == each.word and s.date.date() == each.date:
                        each.sum = each.sum + 1
                        check = False

                if check:
                    record = sentiment.Sum_Word(date=s.date.date(), word=w, sum=1)
                    word_records.append(record)
            else:
                record = sentiment.Sum_Word(date=s.date.date(), word=w, sum=1)
                word_records.append(record)
            counter = counter + 1

    ndb.put_multi(records)
    ndb.put_multi(word_records)

    return True

def get_csv_data(file_name):
    csv_file = PROJECT_DIR+'/../data/'+ file_name +'.csv'

    with open(csv_file, 'rb') as csvfile:
        cursor = csv.reader(csvfile, delimiter=';')
        next(cursor, None)
        #limit = 100
        i = 0
        data = []
        for row in cursor:
            #print row
            data.append(row)
            i = i + 1

            #if limit and i == limit:
            #    break
    return data
