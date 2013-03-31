import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

from django.utils import simplejson

INDEX = """<!DOCTYPE html>
<title>json-head</title>
<h1>json-head</h1>
<p>JSON (and JSON-P) API for running a HEAD request against a URL.
<ul>
    <li><a href="/?url=http://www.google.com/">/?url=http://www.google.com/</a>
    <li><a href="/?url=http://www.yahoo.com/&amp;callback=foo">/?url=http://www.yahoo.com/&amp;callback=foo</a>
</ul>
<p>You may also like <a href="http://json-time.appspot.com/">json-time</a>.
"""

import re
callback_re = re.compile(r'^[a-zA-Z_](\.?[a-zA-Z0-9_]+)+$')
is_valid_callback = callback_re.match

def head_request(url):
    try:
        result = urlfetch.fetch(
            url = url,
            method = urlfetch.HEAD
        )
    except Exception, e:
        return {
            'ok': False,
            'error': str(e),
        }
    return {
        'ok': True,
        'status_code': result.status_code,
        'headers': dict(result.headers),
    }

class MainHandler(webapp.RequestHandler):
    def get(self):
        url = self.request.get('url')
        callback = self.request.get('callback')
        if url:
            self.response.headers['Content-Type'] = 'application/javascript'
            json = simplejson.dumps(head_request(url), indent=4)
            if callback and is_valid_callback(callback):
                self.response.out.write('%s(%s)' % (callback, json))
            else:
                self.response.out.write(json)
        else:
            self.response.out.write(INDEX)

def main():
    application = webapp.WSGIApplication([
        ('/', MainHandler)
    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
