import csv
import re
import string
from server.settings import *
from google.appengine.ext import ndb

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


def calculate_sentiment():
    file_path = PROJECT_DIR+'/../data/brexit.csv'
    file_weight = PROJECT_DIR+'/../data/dictionary.csv'
    delimiter = str(';')

    csvfile = open(file_path, 'r')
    csv.register_dialect(
        'dataset',
        delimiter = delimiter,)
    reader = csv.DictReader(csvfile, dialect='dataset')

    csvfile_weight = open(file_weight, 'r')
    reader_weights = csv.DictReader(csvfile_weight, dialect='dataset')

    weights = []
    for weight in reader_weights:
        weights.append(weight)

    users = []
    counter = 0
    for tweet in reader:
        counter = counter + 1
        if counter > 99: break
        if counter < 90: pass
        else:
            sentence = tweet['tweetext']
            sum_weight = 0
            words = []

            #this part is to remove all symbols and turn them into whitespace
            chars_to_remove = ['"', '!', '#', '.', ',', '?', '@', ':', '~', '*', "'", '\/', '(' ,')', '-', '=']
            specials = ''.join(chars_to_remove)
            trans = string.maketrans(specials, ' '*len(specials))
            sentence = sentence.translate(trans)

            for weight in weights:
                if re.match('.*( '+ str(weight['word']) +' ).*', str(sentence).lower()):
                    word_weight = int(weight['weight'])
                    words.append(weight['word'] + ':' + weight['weight'])
                    sum_weight = sum_weight + word_weight

            user = {'user': tweet['tweetid'], 'tweet': sentence, 'words': words, 'weight': sum_weight}
            users.append(user)

    return users

class Weight(ndb.Model):
    word = ndb.StringProperty(indexed=True)
    weight = ndb.FloatProperty(indexed=False)

class Sentiment(ndb.Model):
    date = ndb.DateTimeProperty(indexed=True)
    tweetid = ndb.StringProperty(indexed=False)
    text = ndb.StringProperty(indexed=True)
    sum_weight = ndb.IntegerProperty(indexed=False)
