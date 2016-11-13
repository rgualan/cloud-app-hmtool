from google.appengine.api import urlfetch

def get_currentweather_bycity(city_name):
    key = 'e167861a60e6d23a436f1216e6b92474'
    baseUrl = 'http://api.openweathermap.org'
    path = '/data/2.5/weather?q=%s' %city_name
    app_id = '&APPID=%s' %key

    r = urlfetch.fetch(baseUrl + path + app_id)
    return r

def get_historicalweather_bycity(city_name):
    key = 'e167861a60e6d23a436f1216e6b92474'
    baseUrl = 'http://api.openweathermap.org'
    path = '/data/2.5/history/city?q=%s' %city_name
    app_id = '&APPID=%s' %key

    r = urlfetch.fetch(baseUrl + path + app_id)
    return r
