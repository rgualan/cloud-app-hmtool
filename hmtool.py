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
from model import testdata
from datetime import datetime
import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


# [START greeting]
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]


# [START timeserie]
class Station(ndb.Model):
    """Sub model for representing a HM station."""
    identity = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)

class Hmrecord(ndb.Model):
    """A main model for representing an individual Meteorological record."""
    # station = ndb.StructuredProperty(Station)
    date = ndb.DateTimeProperty(indexed=True)
    value = ndb.FloatProperty(indexed=False)
    
# [END greeting]


# [START main_page]
class MainPageGuestbook(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('/client/guestbook/index.html')
        self.response.write(template.render(template_values))
# [END main_page]

# [START main_page]
class MainPage(webapp2.RequestHandler):


    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'


        q = Hmrecord.query()
        if q.count() == 0:
            print 'Creating test data...'
            data = testdata.get_test_data()
            records = []
            for r in data:
                rdate = datetime.strptime(r[0], '%Y-%m-%d %H:%M:%S')
                record = Hmrecord(date=rdate, value=r[1])
                records.append(record)
            ndb.put_multi(records)
        else:
            q = Hmrecord.query()
            q.order(+Hmrecord.date)
            records = q.fetch(10)
            for r in records:
                print r

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('/client/index.html')
        self.response.write(template.render(template_values))
# [END main_page]


# [START guestbook]
class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/guestbook?' + urllib.urlencode(query_params))
# [END guestbook]

# [START hmtools]
class Hmtools(webapp2.RequestHandler):

    def get(self):
        q = Hmrecord.query()
        q.order(+Hmrecord.date)
        records = q.fetch(100)
        # return json.dumps([{"date": r.date.strftime('%Y-%m-%d %H:%M:%S'), "temperature": r.value} for r in records])
        # for r in records:
        #    print r.date, r.value, r.date.strftime('%Y-%m-%d %H:%M:%S')
        # return json.dumps([{"date": "test", "temperature": "10"}])
        # return "Hello world"
        # self.response.write('Hello, world!')
        self.response.write(
            json.dumps([{"date": r.date.strftime('%Y-%m-%d %H:%M:%S'), "temperature": r.value} for r in records])
            )

        
# [END hmtools]


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/data', Hmtools),
    ('/guestbook', MainPageGuestbook),
    ('/guestbook/sign', Guestbook),
], debug=True)
# [END app]
