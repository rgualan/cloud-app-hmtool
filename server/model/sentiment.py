import csv
import re
import string
from datetime import datetime
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
    q = Sentiment.query().fetch(1)
    q_word = Word.query().fetch(1)
    test_counter = 0
    if (q == None or len(q) == 0) and (q_word == None or len(q_word) == 0):
        print 'Inserting sentiment data...'
        data = get_csv_data('brexit')
        records = []
        for r in data:
            #print r
            total_weight = 0.0
            if len(r) >= 7 and test_counter < 100:
                rdate = datetime.strptime(r[12], '%d.%m.%y %H:%M')
                sentence = r[7].split()
                for word in sentence:
                    #check if it is url, ignore if yes.
                    h = re.match('(.*)http.*$', word)
                    u = re.match('(.*)\.com.*$', word)

                    if h is None and u is None:
                        #this part is to remove all symbols and turn them into whitespace
                        chars_to_remove = ['"', '!', '#', '.', ',', '?', '@', ':', '~', '*', "'", '\/', '(' ,')', '-', '=']
                        specials = ''.join(chars_to_remove)
                        trans = string.maketrans(specials, ' '*len(specials))
                        word = word.translate(trans)

                        dict = Weight.query().filter(ndb.GenericProperty('word') == word)
                        one = dict.fetch(1)
                        if one:
                            total_weight = total_weight + one[0].weight
                            #count_word = Word.query().filter(ndb.DateProperty('word_date') == rdate.date(), ndb.GenericProperty('word_text') == word)
                            count_word = Word.query().filter(ndb.GenericProperty('word_text') == word.lower())
                            #count_word = Word.query()
                            cw_one = count_word.fetch(1)
                            if cw_one:
                                print str(count_word.fetch(1)[0].word) + ' - ' + word
                                cw_record = Word(word_date=rdate.date(), word_text=word, word_sum_weight=cw_one[0].word_sum_weight + 1.0)
                            else:
                                cw_record = Word(word_date=rdate.date(), word_text=word, word_sum_weight=1.0)
                            cw_record.put()
                    else:
                        pass

                record = Sentiment(date=rdate.date(), tweetid=r[6], text=r[7], sum_weight=total_weight)
                records.append(record)
                test_counter = test_counter + 1
            else:
                pass
        ndb.put_multi(records)
    else:
        q = Sentiment.query().fetch(10)
        #q.order(+sentiment.Sentiment.date)wei
        records = q

        #---DELETE THIS WHEN LIVE--
        ndb.delete_multi(Sentiment.query().fetch(keys_only=True))
        ndb.delete_multi(Word.query().fetch(keys_only=True))

        print "Available sentiment data (sample):"
        print len(records)
        #for r in records:
        #    print r

    return True


class Weight(ndb.Model):
    word = ndb.StringProperty(indexed=False)
    weight = ndb.FloatProperty(indexed=False)

class Sentiment(ndb.Model):
    date = ndb.DateProperty(indexed=False)
    tweetid = ndb.StringProperty(indexed=False)
    text = ndb.StringProperty(indexed=False)
    sum_weight = ndb.FloatProperty(indexed=False)

class Word(ndb.Model):
    word_date = ndb.DateProperty(indexed=False)
    word_text = ndb.StringProperty(indexed=False)
    word_sum_weight = ndb.FloatProperty(indexed=False)
