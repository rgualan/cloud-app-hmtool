import webapp2
import taskqueue

class EnqueueTaskHandler(webapp2.RequestHandler):
    def post(self):
        amount = int(self.request.get('amount'))

        task = taskqueue.add(
            url='/update_counter',
            target='worker',
            params={'amount': amount})

        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
