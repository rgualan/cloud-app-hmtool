from google.appengine.ext import ndb
import webapp2

COUNTER_KEY = 'default counter'


class Counter(ndb.Model):
    count = ndb.IntegerProperty(indexed=False)


class UpdateCounterHandler(webapp2.RequestHandler):
    def post(self):
        amount = int(self.request.get('amount'))

        # This task should run at most once per second because of the datastore
        # transaction write throughput.
        @ndb.transactional
        def update_counter():
            counter = Counter.get_or_insert(COUNTER_KEY, count=0)
            counter.count += amount
            counter.put()

        update_counter()


app = webapp2.WSGIApplication([
    ('/update_counter', UpdateCounterHandler)
], debug=True)
