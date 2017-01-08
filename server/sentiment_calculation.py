import re
import string
from datetime import datetime
from server.model import tweets, sentiment
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
            remove_symbols = word.translate(trans)
            word = remove_symbols.strip()

            dict = sentiment.Weight.query().filter(sentiment.Weight.word == word)
            one = dict.fetch(1)
            if one:
                total_weight = total_weight + one[0].weight
                list_of_words.append(word)
        else:
            pass

    return {'sentiment': total_weight, 'words': list_of_words}

def calculate_sentiment():
    data = tweets.TwitterStatus.query().fetch(1)
    q_word = sentiment.Word.query().fetch(1)

    test_counter = 0
    if (q == None or len(q) == 0) and (q_word == None or len(q_word) == 0):
        print 'Inserting sentiment data...'
        records = []
        for r in data:
            #print r
            total_weight = 0
            if len(r) >= 7:
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

                        dict = sentiment.Weight.query().filter(sentiment.Weight.word == word)
                        one = dict.fetch(1)
                        if one:
                            print 'same word...' + str(one[0].word)
                            total_weight = total_weight + one[0].weight
                            #cw_record = Word(word_date=rdate.date(), word_text=word)
                            #cw_record.put()
                    else:
                        pass

                record = sentiment.Sentiment(date=rdate, tweetid=r[6], text=r[7], sum_weight=total_weight)
                records.append(record)
                test_counter = test_counter + 1
            else:
                pass
        ndb.put_multi(records)
    else:
        q = sentiment.Sentiment.query().fetch(10)
        #q.order(+sentiment.Sentiment.date)wei
        records = q

        #---DELETE THIS WHEN LIVE--
        #ndb.delete_multi(Sentiment.query().fetch(keys_only=True))
        #ndb.delete_multi(Word.query().fetch(keys_only=True))

        print "Available sentiment data (sample):"
        print len(records)
        #for r in records:
        #    print r

    return True

def delete_summarize():
    ndb.delete_multi(sentiment.Sum_Sentiment.query().fetch(keys_only=True))
    ndb.delete_multi(sentiment.Sum_Word.query().fetch(keys_only=True))

def summarize_sentiment():

    ndb.delete_multi(sentiment.Sum_Sentiment.query().fetch(keys_only=True))
    ndb.delete_multi(sentiment.Sum_Word.query().fetch(keys_only=True))

    q_sentiment = tweets.TwitterStatus.query().fetch(99)
    counter = 0
    records = []
    word_records = []

    for s in q_sentiment:
        type = ''
        if s.sentiment > 0: type = 'positive'
        elif s.sentiment < 0: type = 'negative'
        else: type = 'neutral'

        if len(records) > 0:
            check = True
            for each in records:
                if s.date.date() == each.date and each.type == type:
                    each.sum = each.sum + 1
                    #print str(each.date.date()) + '::1'
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
