import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
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

class Blog(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class HomePage(Handler):
    def get(self):
        self.render("base.html")
        
class HomeHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        
        self.render("home.html", posts = posts)

class MainHandler(Handler):
    def render_front(self, title = "", art = "", error = ""):
        self.render("front.html", title = title, art = art, error = error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("art")

        if title and content:
            a = Blog(title = title, content = content)
            a.put()

            self.redirect("/blog")
        else:
            error = "We need both a title and/or some content!"
            self.render_front(title, content, error)

class AllPosts(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")

        self.render("home.html", posts = posts)

class ViewPostHandler(Handler):
    def get(self, id):
        post = db.GqlQuery("SELECT * FROM Blog WHERE __key__ = KEY('Blog', %s)" % (str(id))).get()
        self.render("blogpost.html", post = post)

app = webapp2.WSGIApplication([
    ("/", HomePage),
    ("/blog", HomeHandler),
    ('/newpost', MainHandler),
    ("/allposts", AllPosts),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
