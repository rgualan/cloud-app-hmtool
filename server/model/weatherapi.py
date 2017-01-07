from google.appengine.api import urlfetch

def get_currentweather_bycity(city_name):
    key = 'e167861a60e6d23a436f1216e6b92474'
    baseUrl = 'http://api.openweathermap.org'
    path = '/data/2.5/weather?q=%s' %city_name
    app_id = '&APPID=%s' %key

    r = urlfetch.fetch(baseUrl + path + app_id)
    return r

def get_historicalweather_bycoordinate(coordinate):
    baseUrl = 'https://api.darksky.net/forecast'
    key = '/fcd21d318645bb0fb584ac98dd6a6836'
    path = '/%s,2016-01-01T00:00:00Z?exclude=currently,flags' %coordinate

    r = urlfetch.fetch(baseUrl + key + path)
    return r

def get_current_conditions_bycity(location, condition1):
    baseUrl = 'http://api.wunderground.com'
    key = '/c97f94f569e3a8d4'
    path = '/api%s/%s/q/%s' %(key, condition1, location)
    format = ".json"
    r = urlfetch.fetch(baseUrl + path + format)
    return r

def getWeatherByCityIDs(ids):
    key = 'e167861a60e6d23a436f1216e6b92474'
    base_url = 'http://api.openweathermap.org'
    path = base_url + '/data/2.5/group?'
    params = 'units=metric&APPID=' + key + 'id=' }
    if len(ids) <= 20:
        params += ','.join(ids)
    else:
        params += ','.join(ids[:20])
    response = urlfetch.fetch(base_url + path + params)
    return json.loads(response.text)
