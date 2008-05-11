import wsgiref.handlers
import constantcss
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from webob import Request

class StoredCss(db.Model):
    owner = db.UserProperty()
    name = db.StringProperty()
    content = db.TextProperty()
    last_edited = db.DateTimeProperty(auto_now_add=True)
        
class HomePage(webapp.RequestHandler):
        def get(self):
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, {}))


class ListPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        if users.get_current_user():
          url = users.create_logout_url(self.request.uri)
          url_linktext = 'Logout'
        else:
          url = users.create_login_url(self.request.uri)
          url_linktext = 'Login'
        
        if user:
                csses = db.GqlQuery("SELECT * FROM StoredCss WHERE owner = :1", users.get_current_user())
                template_values = {
                        'csses':csses,
                        'url': url,
                        'url_linktext': url_linktext
                        }
                path = os.path.join(os.path.dirname(__file__), 'css_list.html')
                self.response.out.write(template.render(path, template_values))
        else:
                self.redirect(users.create_login_url(self.request.uri))

class EditCss(webapp.RequestHandler):
	def get(self):
		if self.request.get('key'):
			css = StoredCss.get(self.request.get('key'))
		else:
			css = StoredCss()
			css.content = ""

		already_exists = (css.is_saved())
		template_values = {
		  'css': css,
		  'already_exists': already_exists
		}

		path = os.path.join(os.path.dirname(__file__), 'edit_css.html')
		self.response.out.write(template.render(path, template_values))


class SaveCss(webapp.RequestHandler):
	def post(self):
		if self.request.get('key'):
			css = StoredCss.get(self.request.get('key'))
		else:
			css = StoredCss()

		if users.get_current_user():
			css.owner = users.get_current_user()

                css.name = self.request.get('name')
		css.content = self.request.get('content')

		css.put()
		self.redirect('/list_css')

class DisplayCss(webapp.RequestHandler):
	def get(self):
	        user = users.get_current_user()

                if not users.get_current_user():
                        self.redirect(users.create_login_url(self.request.uri))
                        return
                        
		if self.request.get('key'):
			css = StoredCss.get(self.request.get('key'))
		else:
			self.redirect('/')
			return

                self.response.headers['Content-Type'] = 'text/plain'
                css = constantcss.CssWithConstants(css.content)

                for (key, value) in self.request.GET.items():
                    css.set_override(key, value)

                referrer = Request.blank(self.request.referer)
                for (key, value) in referrer.GET.items():
                    css.set_override(key, value)
                
                self.response.out.write(css.final())


def main():
    application = webapp.WSGIApplication([
                ('/', HomePage),
                ('/list_css', ListPage),
                ('/display_css', DisplayCss),
                ('/add_css', SaveCss),
                ('/edit_css', EditCss)],
                                        debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()