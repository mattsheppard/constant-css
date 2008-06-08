import wsgiref.handlers
import constantcss
import sys
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

class AbstractPage(webapp.RequestHandler):
        template_values = {}
        user_is_logged_in = False
        primary_css = None
        primary_css_exists = False
    
        def prepare_request(self):
                user = users.get_current_user()
            
                if user:
                        self.user_is_logged_in = True;
                        self.template_values['login_logout_url'] = users.create_logout_url('/')
                        self.template_values['login_logout_linktext'] = 'Logout'
                else:
                        self.user_is_logged_in = False;
                        self.template_values['login_logout_url'] = users.create_login_url(self.request.uri)
                        self.template_values['login_logout_linktext'] = 'Login'
                        
                self.template_values['user_is_logged_in'] = self.user_is_logged_in
            
                css_key = self.request.get('css_key')
                if css_key:
                        self.primary_css = StoredCss.get(css_key)
                        self.primary_css_exists = True
                else:
                        # Create an empty stub
                        self.primary_css = StoredCss()
                        self.primary_css.content = ""
                        self.primary_css.name = ""
                        self.primary_css_exists = False

        def require_login(self):
                if not self.user_is_logged_in:
                        self.redirect(users.create_login_url(self.request.uri))
                        return False
                return True

        def require_css_owner(self):
                if self.primary_css_exists and (self.primary_css.owner != users.get_current_user()):
                        self.redirect('http://www.constantcss.com/')
                        return False
                return True

class HomePage(AbstractPage):
        def get(self):
                self.redirect('http://www.constantcss.com/')


class ListPage(AbstractPage):
        def get(self):
	        AbstractPage.prepare_request(self)
	        if not self.require_login():
	                return
                
                user = users.get_current_user()
                csses = db.GqlQuery("SELECT * FROM StoredCss WHERE owner = :1", user)
                self.template_values['csses'] = csses
                        
                path = os.path.join(os.path.dirname(__file__), 'css_list.html')
                self.response.out.write(template.render(path, self.template_values))

class EditCss(AbstractPage):
	def get(self):
	        AbstractPage.prepare_request(self)
	        if (not self.require_login()) or (not self.require_css_owner()):
	                return
		
		self.template_values['css'] = self.primary_css
		self.template_values['already_exists'] = self.primary_css_exists
		
		path = os.path.join(os.path.dirname(__file__), 'edit_css.html')
		self.response.out.write(template.render(path, self.template_values))


class SaveCss(AbstractPage):
	def post(self):
	        AbstractPage.prepare_request(self)
	        if (not self.require_login()) or (not self.require_css_owner()):
	                return
	        
		self.primary_css.owner = users.get_current_user()
                self.primary_css.name = self.request.get('name')
		self.primary_css.content = self.request.get('content')
		
		self.primary_css.put()
		self.redirect('/list_css')

class DisplayCss(AbstractPage):
	def get(self):
	        AbstractPage.prepare_request(self)
	        if (not self.require_login()) or (not self.require_css_owner()):
	                return
	        
                self.response.headers['Content-Type'] = 'text/plain'
                css = constantcss.CssWithConstants(self.primary_css.content)
                
                for (key, value) in self.request.GET.items():
                        css.set_override(key, value)
                
                referrer = Request.blank(self.request.referer)
                for (key, value) in referrer.GET.items():
                        css.set_override(key, value)
                
                self.response.out.write(css.final())

def main():
        application = webapp.WSGIApplication(
                [
                        ('/', HomePage),
                        ('/list_css', ListPage),
                        ('/display_css', DisplayCss),
                        ('/add_css', SaveCss),
                        ('/edit_css', EditCss)
                ],
                debug=True)
        wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
        main()