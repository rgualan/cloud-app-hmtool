#!/usr/bin/env python

# [START imports]
import os
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db
import jinja2
import webapp2
from server.model import user, testdata, weatherapi, sentiment, model
from datetime import datetime
import json
from google.appengine.runtime import DeadlineExceededError
from server.twitter_rest_gae import TwitterRestGAE
import logging
# [END imports]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()

        # if the entity is empty, then populate the table with test data
        q = model.Hmrecord.query()
        if q.count() == 0:
            print 'Inserting test data...'
            data = testdata.get_test_data()
            records = []
            for r in data:
                # print r
                rdate = datetime.strptime(r[3], '%Y-%m-%d %H:%M:%S')
                record = model.Hmrecord(station_name=r[0], latitude=float(r[1]), longitude=float(r[2]),
                                  date=rdate,
                                  rec_number=int(r[4]),
                                  temperature=float(r[5]), air_humidity=float(r[6]),
                                  pressure=float(r[7]), solar_radiation=float(r[8]),
                                  soil_temperature=float(r[9]), wind_speed=float(r[10]),
                                  wind_direction=float(r[11]))
                records.append(record)
            # print records[0]
            ndb.put_multi(records)
        else:
            q = model.Hmrecord.query()
            q.order(+model.Hmrecord.date)
            records = q.fetch(10)
            #print "Available data (sample):"
            #for r in records:
            #    print r

        template_values = check_login(user, self)

        template = JINJA_ENVIRONMENT.get_template('/client/index.html')
        self.response.write(template.render(template_values))
# [END main_page]

# [START]
class RealTimeHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/rt.html')
        self.response.write(template.render(template_values))
# [END]

# [START]
class RealTimeLoader(webapp2.RequestHandler):

    def options(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'

    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'

        last_date_str = self.request.get('lastDate', None);

        #print 'Parameter: ',last_date_str
        if not(last_date_str is None or last_date_str == "" ):
            # The client has some data already
            # So, it is asking for new data
            # This code returns the following data window, starting from the
            # last_date parameter
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d %H:%M:%S')
            #print 'Parameter: ',last_date
            q = model.Hmrecord.query(model.Hmrecord.date > last_date).order(+model.Hmrecord.date)
            records = q.fetch(1)
            #print("Queried data ((new)):")
            #for r in records: print r

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
# [END]

# [START]
class SyntheticRealTimeProducer(webapp2.RequestHandler):

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

    def get(self):
        last_date_str = self.request.get('lastDate', None);

        #print 'Parameter: ',last_date_str
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
            # return the most recent data (last window)
            q = model.Hmrecord2.query().order(-model.Hmrecord2.date)
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

# [START Login]
class Login(webapp2.RequestHandler):

    def post(self):
        username = self.request.get('username', user.DEFAULT_USERNAME)

        query_params = {'username': username}
        self.redirect('/login?' + urllib.urlencode(query_params))
# [END Login]

# [START hmtools]
class Hmtools(webapp2.RequestHandler):

    def get(self):
        q = model.Hmrecord.query().order(+model.Hmrecord.date)
        records = q.fetch()

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

# [START aggregator]
class Aggregator(webapp2.RequestHandler):

    def queryData(self, variable):
        q = model.Hmrecord.query().order(+model.Hmrecord.date)
        records = q.fetch()

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
    def queryData(self, variable):
        q = model.Hmrecord.query().order(+model.Hmrecord.date)
        records = q.fetch()

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
    def queryData(self, variable):
        q = model.Hmrecord.query().order(+model.Hmrecord.date)
        records = q.fetch()

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

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/line_chart.html')
        self.response.write(template.render(template_values))
# [END chart]

# [START map]
class Map(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/map.html')
        self.response.write(template.render(template_values))
# [END map]

# [START boxplot]
class Boxplot(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/boxplot.html')
        self.response.write(template.render(template_values))
# [END boxplot]

# [START wordcloud]
class WordCloud(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/cloud.html')
        self.response.write(template.render(template_values))
# [END wordcloud]

# [START weatherApi]
class WeatherApi(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        city_name = 'Southampton'
        coordinate = '42.3601,-71.0589'
        location = 'Allentown'
        feature1 = 'geolookup'
        q = [
            weatherapi.get_currentweather_bycity(city_name).content,
            weatherapi.get_historicalweather_bycoordinate(coordinate).content,
            weatherapi.get_current_conditions_bycity(location, feature1).content]

        template_values = check_login(user, self)
        template_values['query'] = q

        template = JINJA_ENVIRONMENT.get_template('/client/weatherapi.html')
        self.response.write(template.render(template_values))
# [END weatherApi]

# [START Insert Sentiment]
class Insert_Sentiment_Data(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()

        sentiment.calculate_sentiment()

        template_values = check_login(user, self)

        template = JINJA_ENVIRONMENT.get_template('/client/sentiment.html')
        self.response.write(template.render(template_values))
# [END Insert Sentiment]

# [START Insert Weight]
class Insert_Weight_Data(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        q = sentiment.Weight.query().fetch(1)
        if q == None or len(q) == 0:
            print 'Inserting weight data...'
            data = sentiment.get_csv_data('dictionary')
            records = []
            for r in data:
                #print r[1]
                record = sentiment.Weight(word=r[0], weight=int(r[1]))
                records.append(record)
            ndb.put_multi(records)
        else:
            q = sentiment.Weight.query().fetch()
            #q.order(+sentiment.Weight.word)
            records = q

            #---DELETE THIS WHEN LIVE--
            ndb.delete_multi(sentiment.Weight.query().fetch(keys_only=True))

            print "Available weight data (sample):"
            print len(records)
            #for r in records:
            #    print r

        template_values = check_login(user, self)

        template = JINJA_ENVIRONMENT.get_template('/client/sentiment.html')
        self.response.write(template.render(template_values))
# [END Insert Weight]

# [START Summary]
class Summary(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()

        sentiment.summarize_sentiment()

        template_values = check_login(user, self)

        template = JINJA_ENVIRONMENT.get_template('/client/sentiment.html')
        self.response.write(template.render(template_values))
# [END Summary]

# [START Summary]
class Delete_Summary(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()

        sentiment.delete_summarize()

        template_values = check_login(user, self)

        template = JINJA_ENVIRONMENT.get_template('/client/sentiment.html')
        self.response.write(template.render(template_values))
# [END Summary]


# [START Sentiment]
class Sentiment(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)

        template = JINJA_ENVIRONMENT.get_template('/client/sentiment.html')
        self.response.write(template.render(template_values))
# [END Sentiment]

# [START Tweets]
class Tweets(webapp2.RequestHandler):

    def get(self):
        q = sentiment.Sentiment.query()
        records = q.fetch()

        self.response.write(
            json.dumps(
                [{
                    "date": str(r.date),
                    "tweet": r.tweetid,
                    "words": r.text,
                    "weight": r.sum_weight
                    } for r in records])
            )
# [END Tweets]

# [START Words]
class Words(webapp2.RequestHandler):

    def get(self):
        q = sentiment.Sum_Word.query()
        records = q.fetch()

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

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/data', Hmtools),
    ('/aggregate', Aggregator),
    ('/statistics', Statistics),
    ('/runningmean', RunningMean),
    ('/weatherapi', WeatherApi),
    ('/insert_weight_data', Insert_Weight_Data),
    ('/insert_sentiment_data', Insert_Sentiment_Data),
    ('/summary', Summary),
    ('/delete_summary', Delete_Summary),
    ('/sentiment', Sentiment),
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
    ('/tasks/twitter', TwitterRestHandler),
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
