import webapp2
import cgi
import string
import os
import re
import jinja2


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
								autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
		
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

form="""
<form method="post">
  <h1>Enter some text to ROT13</h1>
    <textarea style="width:400px;" name="text">%(text)s</textarea>
    <input type="submit" />
</form>
"""

def rot13(text):
	if text == "":
		return ""
	if text[0] in string.uppercase:
		return string.uppercase[(string.uppercase.index(text[0]) + 13) % 26] + rot13(text[1:])
	if text[0] in string.lowercase:
	    return string.lowercase[(string.lowercase.index(text[0]) + 13) % 26] + rot13(text[1:])
	return text[0] + rot13(text[1:])



class MainPage(Handler):
  def get(self):
    #self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(form % { 'text' : ""})
  def post(self):
    #self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(form % {'text' : cgi.escape(rot13(self.request.get('text')))})

class Welcome(Handler):
	def get(self):
		welcome = """<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Signup</title>
  </head>

  <body>
    <h2>Welcome, %s!</h2>
  </body>
</html>
"""
		self.response.out.write(welcome % self.request.get('username'))

def GetSignUpValues(req):
	return {
		'Username': req.get('username'),
		'Password': req.get('password'),
		'Password2': req.get('verify'),
		'Email': req.get('email'),
		'Error1': '', 'Error2': '', 'Error3': '', 'Error4': ''
	}

def VerifySignUpValues(req):
	return {
		'Username': re.match(r'^[a-zA-Z0-9_-]{3,20}$', req.get('username')),
		'Password': re.match(r'^.{3,20}$', req.get('password')),
		'Password2': re.match(r'^.{3,20}$', req.get('verify')),
		'Email': re.match(r'^[\S]+@[\S]+\.[\S]+$', req.get('email')),
		'Error1': '', 'Error2': '', 'Error3': '', 'Error4': ''
	}	

class SignUp(Handler):
	def get(self):
		template_values = {
			'Username': '',
			'Password': '',
			'Password2':'',
			'Email': '',
			'Error1': '',
			'Error2': '',
			'Error3': '',
			'Error4': ''
		}
		self.render("signup.html",  **template_values)
	def post(self):
		template_values = GetSignUpValues(self.request)
		tests = VerifySignUpValues(self.request)
		if not template_values['Username'] or tests['Username'] == None:
			template_values['Error1'] = "That's not a valid username."
		if not template_values['Password'] or tests['Password'] == None:
			template_values['Error2'] = "That wasn't a valid password."			
		elif not template_values['Password2'] or template_values['Password'] !=  template_values['Password2']:
			template_values['Error3'] = "Your passwords didn't match."
		if template_values['Email'] and tests['Email'] == None:
			template_values['Error4'] = "That's not a valid email."
		if template_values['Error1'] or template_values['Error2'] or template_values['Error3'] or template_values['Error4']:
			template_values['Password'] = template_values['Password2'] = ''
			self.render('signup.html', **template_values)
		else:
			self.redirect("/welcome?username=" + template_values['Username'])

class Art(db.Model):
	title = db.StringProperty(required = True)
	art = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class Ascii(Handler):
	def render_front(self, title="", art="", error=""):
		arts = db.GqlQuery("select * from Art order by created desc")
		self.render("ascii.html", title=title, art=art, error=error, arts=arts)
		
	def get(self):
		self.render_front()
		
	def post(self):
		title = self.request.get("title")
		art = self.request.get("art")
		
		if title and art:
			a = Art(title=title, art=art)
			a.put()
			
			self.redirect("/ascii")
		else:
			error = "we need both a title and some artwork!"
			self.render_front(title, art, error)
			
from blog import *

app = webapp2.WSGIApplication([('/', MainPage), ('/signup', SignUp), ('/welcome', Welcome), ('/ascii', Ascii), ('/blog', Blog), ('/blog/newpost', NewPost), ('/blog/(\d+)', Permalink)],
                              debug=True)
