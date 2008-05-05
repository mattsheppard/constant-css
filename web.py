import wsgiref.handlers
import constantcss
import os

from google.appengine.api import users
from google.appengine.ext import webapp

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
    
        if user:
            self.response.headers['Content-Type'] = 'text/plain'
            css_file = os.path.join(os.path.dirname(__file__), 'example.css')
            css = constantcss.CssWithConstants(css_file)
			
            for (key, value) in self.request.GET.items():
                    css.set_override(key, value)
            self.response.out.write( css.final() )
        else:
            self.redirect(users.create_login_url(self.request.uri))

def main():
    application = webapp.WSGIApplication(
                                        [('/', MainPage)],
                                        debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()