from google.appengine.ext import ndb

class Hmrecord2(ndb.Model):
    """A main model for representing an individual Meteorological record."""
    station_name = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(indexed=True)
    value = ndb.FloatProperty(indexed=False)