#!/usr/bin/env python

# [START imports]
import os
import urllib
import logging
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db
import jinja2
import webapp2
from server.model import user, testdata, sentiment, model
from server.model.tweets import TwitterStatus
from server import sentiment_calculation
from datetime import datetime, timedelta
import json
from google.appengine.runtime import DeadlineExceededError
from server.twitter_rest_gae import TwitterRestGAE
import logging
# [END imports]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# If the entity is empty, then populate the table with test data
q = model.Hmrecord.query()
if q.count() == 0:
    logging.info( "Inserting test data..." )
    data = testdata.get_test_data()
    records = []
    for r in data:
        rdate = datetime.strptime(r[3], '%Y-%m-%d %H:%M:%S')
        record = model.Hmrecord(station_name=r[0], latitude=float(r[1]), longitude=float(r[2]),
                          date=rdate,
                          rec_number=int(r[4]),
                          temperature=float(r[5]), air_humidity=float(r[6]),
                          pressure=float(r[7]), solar_radiation=float(r[8]),
                          soil_temperature=float(r[9]), wind_speed=float(r[10]),
                          wind_direction=float(r[11]))
        records.append(record)
    ndb.put_multi(records)

q = model.Hmrecord.query().order(+model.Hmrecord.date)
records = q.fetch()
HDCACHE = records

def queryHistoricalData():
    if len(HDCACHE)>0:
        logging.info("Using cache...")
        return HDCACHE
    else:
        logging.info("Querying database...")
        q = model.Hmrecord.query().order(+model.Hmrecord.date)
        records = q.fetch()
        return records

# [START main_page]
class MainPage(webapp2.RequestHandler):
    """ Loads the index page using templates and checking login"""
    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/index.html')
        self.response.write(template.render(template_values))
# [END main_page]

# [START Login]
class Login(webapp2.RequestHandler):

    def post(self):
        username = self.request.get('username', user.DEFAULT_USERNAME)

        query_params = {'username': username}
        self.redirect('/login?' + urllib.urlencode(query_params))
# [END Login]

# [START hmtools]
class Hmtools(webapp2.RequestHandler):
    """ Returns all the historical data for the test station.
    If the Google Datastore is empty, it loads the Hmrecord entity
    with test data from a CSV file
    """

    def get(self):
        records = queryHistoricalData()
        self.response.write(
            json.dumps(
                [{
                    "station_name" : r.station_name,
                    "latitude" : r.latitude,
                    "longitude" : r.longitude,
                    "date": r.date.strftime('%Y-%m-%d %H:%M:%S'),
                    "rec_number": r.rec_number,
                    "temperature": r.temperature,
                    "air_humidity": r.air_humidity,
                    "pressure": r.pressure,
                    "solar_radiation": r.solar_radiation,
                    "soil_temperature": r.soil_temperature,
                    "wind_speed": r.wind_speed,
                    "wind_direction": r.wind_direction
                    } for r in records])
            )
# [END hmtools]

# [START]
class RealTimeHandler(webapp2.RequestHandler):
    """ Loads the real time interface"""
    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/rt.html')
        self.response.write(template.render(template_values))
# [END]

# [START]
class RealTimeLoader(webapp2.RequestHandler):
    """ Returns a piece of historical data as if it was real-time data
    If the lastDate parameter is empty, then it returns the first chunk of data
    If the lastDate is not empty, it returns one (or more) record whose
    date is bigger that the lastDate parameter
    """

    def get(self):
        last_date_str = self.request.get('lastDate', None);

        if last_date_str is None or last_date_str.strip() == "":
            # For the first query (not last_date parameter)
            # return a small amomunt of the data
            # the erliest data
            #q = model.Hmrecord.query().order(-model.Hmrecord.date)
            q = model.Hmrecord.query().order(+model.Hmrecord.date)
            records = q.fetch(50)
            #records = q.fetch()
            #records = list(reversed(records));
            #print("Queried data ((first time)):")
            #for r in records: print r;

            self.response.write(
                json.dumps(
                    [{
                        "station_name" : r.station_name,
                        "latitude" : r.latitude,
                        "longitude" : r.longitude,
                        "date": r.date.strftime('%Y-%m-%d %H:%M:%S'),
                        "rec_number": r.rec_number,
                        "temperature": r.temperature,
                        "air_humidity": r.air_humidity,
                        "pressure": r.pressure,
                        "solar_radiation": r.solar_radiation,
                        "soil_temperature": r.soil_temperature,
                        "wind_speed": r.wind_speed,
                        "wind_direction": r.wind_direction
                        } for r in records])
                )
        else:
            # The client has some data already
            # So, it is asking for new data
            # This code returns the following data window, starting from the
            # last_date parameter
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d %H:%M:%S')
            #print 'Parameter: ',last_date
            q = model.Hmrecord.query(model.Hmrecord.date > last_date).order(+model.Hmrecord.date)
            records = q.fetch(1)

            self.response.write(
                json.dumps(
                    [{
                        "station_name" : r.station_name,
                        "latitude" : r.latitude,
                        "longitude" : r.longitude,
                        "date": r.date.strftime('%Y-%m-%d %H:%M:%S'),
                        "rec_number": r.rec_number,
                        "temperature": r.temperature,
                        "air_humidity": r.air_humidity,
                        "pressure": r.pressure,
                        "solar_radiation": r.solar_radiation,
                        "soil_temperature": r.soil_temperature,
                        "wind_speed": r.wind_speed,
                        "wind_direction": r.wind_direction
                        } for r in records])
                )

# [END]

# [START]
class SyntheticRealTimeProducer(webapp2.RequestHandler):
    """ Receives new synthetic data and stores it in the Hmrecord2 entity.
    This is part of the real-time producer/consumer simulation
    """

    def post(self):
        # get the data
        station = self.request.get('station')
        date = datetime.strptime(self.request.get('date'), '%Y-%m-%d %H:%M:%S')
        value = float(self.request.get('value'))

        # save the data
        record = model.Hmrecord2(station_name=station, date=date, value=value)
        record.put()

        #self.response.write(template.render(template_values))
# [END]

# [START]
class SyntheticRealTimeConsumer(webapp2.RequestHandler):
    """ Returns the synthetic data stored in the Hmrecord2 entity.
    This is part of the real-time producer/consumer simulation
    """

    def get(self):
        last_date_str = self.request.get('lastDate', None);

        if not(last_date_str is None or last_date_str == "" ):
            # The client has some data already
            # So, it is asking for new data
            # This code returns the following data window, starting from the
            # last_date parameter
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d %H:%M:%S')
            q = model.Hmrecord2.query(model.Hmrecord2.date > last_date).order(-model.Hmrecord2.date)
            records = q.fetch(50)
            records = list(reversed(records));
            #print("Queried data ((new)): ")
            #for r in records: print r

            self.response.write(
                json.dumps(
                    [{
                        "station_name" : r.station_name,
                        "date": r.date.strftime('%Y-%m-%d %H:%M:%S'),
                        "value": r.value
                        } for r in records])
                )
        else:
            # For the first query (not last_date parameter)
            # return the most recent data (last 5 minutes)
            last_date = datetime.now() - timedelta(minutes=5)
            q = model.Hmrecord2.query(model.Hmrecord2.date > last_date).order(-model.Hmrecord2.date)
            records = q.fetch(50)
            #records = q.fetch()
            records = list(reversed(records));
            #print("Queried data ((first time)):")
            #for r in records: print r;

            self.response.write(
                json.dumps(
                    [{
                        "station_name" : r.station_name,
                        "date": r.date.strftime('%Y-%m-%d %H:%M:%S'),
                        "value": r.value
                        } for r in records])
                )
# [END]

# [START aggregator]
class Aggregator(webapp2.RequestHandler):
    """ Calculates aggregation time series for the historical data.
    The aggregated data can have different periodicity (hour, day, month, year)
    and use different statistics methods for the aggregation (mean, median, min, max)
    """

    def queryData(self, variable):
        records = queryHistoricalData()

        # Aggregate data
        result = [];
        for r in records:
            value = 0
            if (variable == "temperature"):
                value = r.temperature
            elif (variable == "air_humidity"):
                value = r.air_humidity
            elif (variable == "pressure"):
                value = r.pressure
            elif (variable == "soil_temperature"):
                value = r.soil_temperature
            elif (variable == "solar_radiation"):
                value = r.solar_radiation
            elif (variable == "wind_direction"):
                value = r.wind_direction
            elif (variable == "wind_speed"):
                value = r.wind_speed

            result.append({"date":r.date, variable:value})

        return result

    def formaterByLevel(self, level):
        levels = {
            "hour": '%Y-%m-%d %H',
            "day": '%Y-%m-%d',
            "month": '%Y-%m',
            "year": '%Y'
        }

        return levels[level]

    def median(self, lst):
        sortedLst = sorted(lst)
        lstLen = len(lst)
        index = (lstLen - 1) // 2

        if (lstLen % 2):
            return sortedLst[index]
        else:
            return (sortedLst[index] + sortedLst[index + 1])/2.0

    def get(self):
        variable = self.request.get("variable")
        level = self.request.get("level")
        how = self.request.get("how")

        records = self.queryData(variable)

        # Aggregate data
        temp_dict = {};
        for r in records:
            upperIndex = r["date"].strftime(self.formaterByLevel(level));

            if upperIndex in temp_dict:
                temp_dict[upperIndex].append(r[variable]);
            else:
                temp_dict[upperIndex] = [r[variable]];

        # Calculate aggregation
        result = []
        for key in temp_dict.keys():
            sumv = 0
            for val in temp_dict[key]:
                sumv = sumv + val
            date = datetime.strptime(key, self.formaterByLevel(level))

            aggregation = sumv
            if how == "mean":
                aggregation = sumv/len(temp_dict[key])
            elif how == "median":
                aggregation = self.median(temp_dict[key])
            elif how == "min":
                aggregation = min(temp_dict[key])
            elif how == "max":
                aggregation = max(temp_dict[key])

            result.append({'date':date.strftime('%Y-%m-%d %H:%M:%S'), variable:aggregation})

        result = sorted(result, key=lambda k: k['date'])
        #print result;

        self.response.write(json.dumps(result))
# [END aggregator]

# [START statistics]
class Statistics(webapp2.RequestHandler):
    """ Calculates basic statistics for the historical data
    """

    def queryData(self, variable):
        records = queryHistoricalData()

        # Aggregate data
        result = [];
        for r in records:
            value = 0
            if (variable == "temperature"):
                value = r.temperature
            elif (variable == "air_humidity"):
                value = r.air_humidity
            elif (variable == "pressure"):
                value = r.pressure
            elif (variable == "soil_temperature"):
                value = r.soil_temperature
            elif (variable == "solar_radiation"):
                value = r.solar_radiation
            elif (variable == "wind_direction"):
                value = r.wind_direction
            elif (variable == "wind_speed"):
                value = r.wind_speed

            result.append({"date":r.date, variable:value})

        return result

    def median(self, lst):
        sortedLst = sorted(lst)
        lstLen = len(lst)
        index = (lstLen - 1) // 2

        if (lstLen % 2):
            return sortedLst[index]
        else:
            return (sortedLst[index] + sortedLst[index + 1])/2.0

    def get(self):
        variable = self.request.get("variable")

        records = self.queryData(variable)
        values = []
        for r in records:
            values.append(r[variable])

        # Calculate statistics
        sumv = 0;
        for val in values:
            sumv = sumv + val

        meanv = sumv / len(values)
        medianv = self.median(values)
        minv = min(values)
        maxv = max(values)

        result = {
            "sum" : sumv,
            "mean" : meanv,
            "median" : medianv,
            "min" : minv,
            "max" : maxv,
        }
        self.response.write(json.dumps(result))
# [END statistics]

# [START RunningMean]
class RunningMean(webapp2.RequestHandler):
    """ Calculates the running mean or moving average for the historical data
    It receives the size of the window as a parameter.
    """

    def queryData(self, variable):
        records = queryHistoricalData()

        # Aggregate data
        result = [];
        for r in records:
            value = 0
            if (variable == "temperature"):
                value = r.temperature
            elif (variable == "air_humidity"):
                value = r.air_humidity
            elif (variable == "pressure"):
                value = r.pressure
            elif (variable == "soil_temperature"):
                value = r.soil_temperature
            elif (variable == "solar_radiation"):
                value = r.solar_radiation
            elif (variable == "wind_direction"):
                value = r.wind_direction
            elif (variable == "wind_speed"):
                value = r.wind_speed

            result.append({"date":r.date, variable:value})

        return result

    def runningMean(self,inputList,variable,N):
        sum = 0
        result = list( {"date":x["date"], variable:0} for x in inputList)

        for i in range( 0, N ):
            sum = sum + inputList[i][variable]
            result[i][variable] = sum / (i+1)

        for i in range( N, len(inputList) ):
            sum = sum - inputList[i-N][variable] + inputList[i][variable]
            result[i][variable] = sum / N

        return result


    def get(self):
        variable = self.request.get("variable")
        steps = int(self.request.get("steps"))

        records = self.queryData(variable)
        result = self.runningMean(records,variable,steps)
        #print result

        self.response.write(
            json.dumps(
                [{
                    "date": r["date"].strftime('%Y-%m-%d %H:%M:%S'),
                    variable: r[variable]
                } for r in result])
            )
# [END RunningMean]

# [START chart]
class Chart(webapp2.RequestHandler):
    """ Loads the line chart interface
    """

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/line_chart.html')
        self.response.write(template.render(template_values))
# [END chart]

# [START map]
class Map(webapp2.RequestHandler):
    """ Loads the map interface
    """

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/map.html')
        self.response.write(template.render(template_values))
# [END map]

# [START boxplot]
class Boxplot(webapp2.RequestHandler):
    """ Loads the boxplot interface
    """

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/boxplot.html')
        self.response.write(template.render(template_values))
# [END boxplot]

# [START wordcloud]
class WordCloud(webapp2.RequestHandler):
    """ Loads the cloud interface
    """

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/cloud.html')
        self.response.write(template.render(template_values))
# [END wordcloud]

# [START Summary]
class Summary(webapp2.RequestHandler):
    """ Call summarize_sentiment() function from sentiment_calculation
    This part is called in cronjob
    """

    def get(self):
        sentiment_calculation.summarize_sentiment()
# [END Summary]

# [START Sentiment]
class Sentiment(webapp2.RequestHandler):
    """ Call summarize_sentiment() function from sentiment_calculation
    This part is called in cronjob
    """

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        #logging.info(str(sentiment.calculate_a_tweet("like no #aslkj )(*&)lksdfg; aaskf http://asldkfj.com")))

        template = JINJA_ENVIRONMENT.get_template('/client/sentiment.html')
        self.response.write(template.render(template_values))
# [END Sentiment]

# [START Tweets]
class Tweets(webapp2.RequestHandler):
    """ Get tweets data from TwitterStatus table
    """

    def get(self):
        q = TwitterStatus.query().order(-TwitterStatus.date)
        records = q.fetch(299)

        self.response.write(
            json.dumps(
                [{
                    "date": str(r.date),
                    "tweet": r.words,
                    "words": r.text,
                    "weight": r.sentiment
                    } for r in records])
            )
# [END Tweets]

# [START Sum_Sentiment]
class Sum_Sentiment(webapp2.RequestHandler):
    """ Get Summary of Sentiment data from Sum_Sentiment table
    """

    def get(self):
        q = sentiment.Sum_Sentiment.query()
        records = q.fetch()

        self.response.write(
            json.dumps(
                [{
                    "date": str(r.date),
                    #"tweet": r.tweetid,
                    "words": r.type,
                    "weight": r.sum
                    } for r in records])
            )
# [END Sum_Sentiment]

# [START Words]
class Words(webapp2.RequestHandler):
    """ Get Summary of Words Count data from Words table
    """

    def get(self):
        q = sentiment.Sum_Word.query().order(-sentiment.Sum_Word.word_date)
        records = q.fetch(299)

        self.response.write(
            json.dumps(
                [{
                    "word_date": str(r.date),
                    "word_text": r.word,
                    "word_sum_weight": r.sum,
                    } for r in records])
            )
# [END Words]

# [START TwitterRestHandler]
class TwitterRestHandler(webapp2.RequestHandler):
    def get(self):
        try:
            twitter_rest = TwitterRestGAE()
            twitter_rest.search_twitter()
        except DeadlineExceededError as e:
            logging.exception('DeadlineExceededError')
# [END TwitterRestHandler]

# [START TweetsHandler]
class TweetsHandler(webapp2.RequestHandler):
    def get(self):
        q = TwitterStatus.query().order(-TwitterStatus.date)
        results = q.fetch(1000)
        self.response.write(
            json.dumps(
                [{
                    "sentiment": t.sentiment,
                    "tweetid": t.tweetid,
                    "location": [t.location.lat, t.location.lon],
                    } for t in results])
            )
# [END TweetsHandler]

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/data', Hmtools),
    ('/aggregate', Aggregator),
    ('/statistics', Statistics),
    ('/runningmean', RunningMean),
    ('/summary', Summary),
    ('/sentiment', Sentiment),
    ('/sum_sentiment', Sum_Sentiment),
    ('/tweets', Tweets),
    ('/words', Words),
    ('/login', Login),
    ('/chart', Chart),
    ('/boxplot', Boxplot),
    ('/cloud', WordCloud),
    ('/map', Map),
    ('/realtime', RealTimeHandler),
    ('/rtdata', RealTimeLoader),
    ('/srtproducer', SyntheticRealTimeProducer),
    ('/srtconsumer', SyntheticRealTimeConsumer),
    ('/tweets-api', TweetsHandler),
    ('/tasks/twitter', TwitterRestHandler),
    ('/tasks/summary', Summary),
], debug=True)
# [END app]

def check_login(user, self):
    template_values = {}
    url = None
    url_linktext = None
    if user:
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    template_values = {
        'user': user,
        'url': url,
        'url_linktext': url_linktext
    }

    return template_values
