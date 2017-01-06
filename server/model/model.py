from google.appengine.ext import ndb

class Station(ndb.Model):
    """Representation of a Remote Sensor Station."""
    identity = ndb.StringProperty(indexed=True)
    description = ndb.StringProperty(indexed=False)
    lat = ndb.FloatProperty(indexed=False)
    lon = ndb.FloatProperty(indexed=False)

class Hmrecord(ndb.Model):
    """A main model for representing an individual Meteorological record."""
    # station = ndb.StructuredProperty(Station)
    station_name = ndb.StringProperty(indexed=True)
    latitude = ndb.FloatProperty(indexed=False)
    longitude = ndb.FloatProperty(indexed=False)
    date = ndb.DateTimeProperty(indexed=True)
    rec_number = ndb.IntegerProperty(indexed=False)
    temperature = ndb.FloatProperty(indexed=False)
    air_humidity = ndb.FloatProperty(indexed=False)
    pressure = ndb.FloatProperty(indexed=False)
    solar_radiation = ndb.FloatProperty(indexed=False)
    soil_temperature = ndb.FloatProperty(indexed=False)
    wind_speed = ndb.FloatProperty(indexed=False)
    wind_direction = ndb.FloatProperty(indexed=False)

class Hmrecord2(ndb.Model):
    """ A model for representing an individual Meteorological record
        for the real time simulations """
    station_name = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(indexed=True)
    value = ndb.FloatProperty(indexed=False)