import csv
import re
import string
from datetime import datetime
from server.settings import *
from google.appengine.ext import ndb

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
            word = word.translate(trans)
            word = word.strip()

            dict = Weight.query().filter(Weight.word == word)
            one = dict.fetch(1)
            if one:
                total_weight = total_weight + one[0].weight
                cw_record = Word(word_date=rdate.date(), word_text=word)
                cw_record.put()
                list_of_words.append(word)
        else:
            pass

    return {'sentiment': total_weight, 'words': list_of_words}

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
            total_weight = 0
            if len(r) >= 7 and test_counter < 99:
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
                        word = word.strip()

                        dict = Weight.query().filter(Weight.word == word)
                        one = dict.fetch(1)
                        if one:
                            print 'same word...' + str(one[0].word)
                            total_weight = total_weight + one[0].weight
                            #count_word = Word.query().filter(ndb.DateProperty('word_date') == rdate.date(), ndb.GenericProperty('word_text') == word)
                            #count_word = Word.query().filter(Word.word_text == word.lower())
                            #count_word = Word.query()
                            #cw_one = count_word.fetch(1)
                            #if cw_one:
                                #cw_record = Word(word_date=rdate.date(), word_text=word, word_sum_weight=cw_one[0].word_sum_weight + 1.0)
                                #cw_record = Word(word_text=word, word_sum_weight=cw_one[0].word_sum_weight + 1.0)
                            #else:
                                #cw_record = Word(word_date=rdate.date(), word_text=word, word_sum_weight=1.0)
                            cw_record = Word(word_date=rdate.date(), word_text=word)
                            cw_record.put()
                    else:
                        pass

                record = Sentiment(date=rdate, tweetid=r[6], text=r[7], sum_weight=total_weight)
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

def delete_summarize():
    #ndb.delete_multi(Sum_Sentiment.query().fetch(keys_only=True))
    ndb.delete_multi(Sum_Word.query().fetch(keys_only=True))

def summarize_sentiment():

    q_sentiment = Sentiment.query()
    q_word = Word.query()

    counter = 0

    records = []
    for s in q_sentiment:
        if counter < 10:
            if len(records) > 0:
                for each in records:
                    if s.date == each.date and s.sum_weight > 0:
                        each.sum = each.sum + s.sum_weight
                        each.type = 'positive'
                    elif s.date == each.date and s.sum_weight < 0:
                        each.sum = each.sum + s.sum_weight
                        each.type = 'negative'
                    else:
                        each.sum = each.sum + s.sum_weight
                        each.type = 'neutral'
            else:
                if s.date == each.date and s.sum_weight > 0:
                    record = Sum_Sentiment(date=s.date, type='positive', sum=1)
                elif s.date == each.date and s.sum_weight < 0:
                    record = Sum_Sentiment(date=s.date, type='negative', sum=1)
                else:
                    record = Sum_Sentiment(date=s.date, type='neutral', sum=1)
                records.append(record)
            ndb.put_multi(records)
        else:
            break
        counter = counter + 1

    word_records = []
    for w in q_word:
        #if counter < 100:
        if len(word_records) > 0:
            check = True
            for each in word_records:
                print str(counter) + '. word: ' + str(w.word_text) + ' - ' + str(each.word) + ';; date: ' + str(w.word_date) + ' - ' + str(each.date)
                if w.word_text == each.word and w.word_date == each.date:
                    each.sum = each.sum + 1
                    check = False

            if check:
                record = Sum_Word(date=w.word_date, word=w.word_text, sum=1)
                word_records.append(record)
        else:
            record = Sum_Word(date=w.word_date, word=w.word_text, sum=1)
            word_records.append(record)
        #else:
            #break
        counter = counter + 1

    ndb.put_multi(word_records)
    return True

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

