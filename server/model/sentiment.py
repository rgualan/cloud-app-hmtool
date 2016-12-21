import csv
import re
import random
from server.settings import *

def get_test_data():
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
    for tweet in reader:
        sentence = tweet['tweetext'].split()
        tweets = []
        sum_weight = 0
        for word in sentence:
            #check if it is url, ignore if yes.
            h = re.match('(.*)http.*$', word)
            u = re.match('(.*)\.com.*$', word)

            if h is None and u is None:
                word_weight = 0
                #remove specified characters
                chars_to_remove = ['"', '!', '#', '.', '?', '@', ':', '~', '*', '\'', '(' ,')']
                subj = word
                word = subj.translate(None, ''.join(chars_to_remove))
                for weight in weights:
                    if re.match('.*('+ str(weight['word']) +').*', str(word).lower()):
                        word_weight = int(weight['weight'])
                sum_weight = sum_weight + word_weight
                tweets.append(word)

            else:
                pass
        user = {'user': tweet['userid'], 'tweet': tweets, 'weight': sum_weight}
        users.append(user)

    return users
