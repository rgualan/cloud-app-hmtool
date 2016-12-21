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
import jinja2
import webapp2
from server.model import user, testdata, weatherapi, sentiment
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


# [START guestbook]
class Login(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        username = self.request.get('username', user.DEFAULT_USERNAME)

        query_params = {'username': username}
        self.redirect('/login?' + urllib.urlencode(query_params))
# [END guestbook]

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


# [START hmtools]
class Chart(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        template_values = check_login(user, self)
        template = JINJA_ENVIRONMENT.get_template('/client/line_chart.html')
        self.response.write(template.render(template_values))
# [END hmtools]

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

# [START weatherApi]
class Sentiment(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        q = sentiment.get_test_data()

        template_values = check_login(user, self)
        template_values['query'] = q

        template = JINJA_ENVIRONMENT.get_template('/client/sentiment.html')
        self.response.write(template.render(template_values))
# [END weatherApi]

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/data', Hmtools),
    ('/weatherapi', WeatherApi),
    ('/sentiment', Sentiment),
    ('/login', Login),
    ('/chart', Chart),
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
