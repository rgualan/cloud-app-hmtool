#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db
import jinja2
import webapp2
from server.model import user, testdata, weatherapi, sentiment, model2
from datetime import datetime
import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()

        # if the entity is empty, then populate the table with test data
        q = testdata.Hmrecord.query()
        if q.count() == 0:
            print 'Inserting test data...'
            data = testdata.get_test_data()
            records = []
            for r in data:
                # print r
                rdate = datetime.strptime(r[3], '%Y-%m-%d %H:%M:%S')
                record = testdata.Hmrecord(station_name=r[0], latitude=float(r[1]), longitude=float(r[2]),
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
            q = testdata.Hmrecord.query()
            q.order(+testdata.Hmrecord.date)
            records = q.fetch(10)
            print "Available data (sample):"
            for r in records:
                print r

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

        print 'Parameter: ',last_date_str
        if not(last_date_str is None or last_date_str == "" ):
            # The client has some data already
            # So, it is asking for new data 
            # This code returns the following data window, starting from the 
            # last_date parameter
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d %H:%M:%S')
            print 'Parameter: ',last_date
            q = testdata.Hmrecord.query(testdata.Hmrecord.date > last_date).order(+testdata.Hmrecord.date)
            records = q.fetch(2)
            print("Queried data ((new)):")
            for r in records: print r

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
            #q = testdata.Hmrecord.query().order(-testdata.Hmrecord.date)
            q = testdata.Hmrecord.query().order(+testdata.Hmrecord.date)
            records = q.fetch(50)
            #records = q.fetch()
            #records = list(reversed(records));
            print("Queried data ((first time)):")
            for r in records: print r;
  
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
        record = model2.Hmrecord2(station_name=station, date=date, value=value)
        record.put()

        #self.response.write(template.render(template_values))
# [END]

# [START]
class SyntheticRealTimeConsumer(webapp2.RequestHandler):

    def get(self):
        last_date_str = self.request.get('lastDate', None);

        print 'Parameter: ',last_date_str
        if not(last_date_str is None or last_date_str == "" ):
            # The client has some data already
            # So, it is asking for new data 
            # This code returns the following data window, starting from the 
            # last_date parameter
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d %H:%M:%S')
            q = model2.Hmrecord2.query(model2.Hmrecord2.date > last_date).order(-model2.Hmrecord2.date)
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
            q = model2.Hmrecord2.query().order(-model2.Hmrecord2.date)
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
        q = testdata.Hmrecord.query().order(+testdata.Hmrecord.date) 
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
                record = sentiment.Weight(word=r[0], weight=float(r[1]))
                records.append(record)
            ndb.put_multi(records)
        else:
            q = sentiment.Weight.query().fetch(10)
            #q.order(+sentiment.Weight.word)
            records = q

            #---DELETE THIS WHEN LIVE--
            #ndb.delete_multi(sentiment.Weight.query().fetch(keys_only=True))

            print "Available weight data (sample):"
            print len(records)
            #for r in records:
            #    print r

        template_values = check_login(user, self)

        template = JINJA_ENVIRONMENT.get_template('/client/sentiment.html')
        self.response.write(template.render(template_values))
# [END Insert Weight]

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
        q = sentiment.Word.query()
        records = q.fetch()

        self.response.write(
            json.dumps(
                [{
                    "word_date": str(r.word_date),
                    "word_text": r.word_text,
                    "word_sum_weight": r.word_sum_weight,
                    } for r in records])
            )
# [END Words]


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/data', Hmtools),
    ('/weatherapi', WeatherApi),
    ('/insert_weight_data', Insert_Weight_Data),
    ('/insert_sentiment_data', Insert_Sentiment_Data),
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
