import csv
import re
import string
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

            user = {'user': tweet['userid'], 'tweet': sentence, 'words': words, 'weight': sum_weight}
            users.append(user)

    return users
