import csv
import re
from server.settings import *

def get_test_data():
    file_path = PROJECT_DIR+'/../data/brexit.csv'
    delimiter = str(';')

    csvfile = open(file_path, 'r')
    csv.register_dialect(
        'dataset',
        delimiter = delimiter,)
    reader = csv.DictReader(csvfile, dialect='dataset')

    users = []
    for tweet in reader:
        tweets = []
        h = None
        u = None
        sentence = tweet['tweetext'].split()
        for word in sentence:
            #check if it is url, ignore if yes.
            h = re.match('(.*)http.*$', word)
            u = re.match('(.*)\.com.*$', word)

            if h is None and u is None:
                #remove specified characters
                chars_to_remove = ['"', '!', '#', '.', '?', '@', ':', '\'s', '~']
                subj = word
                word = subj.translate(None, ''.join(chars_to_remove))
                tweets.append(word)
            else:
                pass
        if h is None and u is None:
            user = {'user': tweet['userid'], 'tweet': tweets}
            users.append(user)

    return users
