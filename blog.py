from GAEblog import *

class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class Blog(Handler):
	def render_front(self, error=""):
		posts = db.GqlQuery("select * from Post order by created desc limit 10")
		self.render("blog.html", posts=posts, error=error)
		
	def get(self):
		self.render_front()
			
class NewPost(Handler):
	def render_front(self, subject="", content="", error=""):
		self.render("newpost.html", subject=subject, content=content, error=error)
		
	def get(self):
		self.render_front()
		
	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")
		
		if subject and content:
			p = Post(subject=subject, content=content)
			p_key = p.put()
			
			self.redirect("/blog/%d" %p_key.id())
		else:
			error = "we need both a subject and some content!"
			self.render_front(subject, content, error)
			
class Permalink(Blog):
	def get(self, blog_id):
		s = Post.get_by_id(int(blog_id))
		self.render("blog.html", posts=[s])
		
