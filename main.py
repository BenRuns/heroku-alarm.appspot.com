#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.api import users

class Website(ndb.Model): 
	heroku_name = ndb.StringProperty(required = True)
	created = ndb.DateTimeProperty(auto_now_add = True)


class MainHandler(webapp2.RequestHandler):

    def get(self):
    	count = str(Website.query().count(limit=None))
        self.response.write('''
	     <form method="post">

	     Enter your heroku app name to have it pinged every thirty minutes
	     <p>http://
		<input type ="text" name="heroku" >. herokuapp.com</p>
		
		<input type="submit">
	     </form><p>

        	''' + count + ' websites have signed up with this site </p>')

    def post(self):
    	
    	url = self.request.get("heroku") 
    	e = Website(heroku_name = url)
    	e.put()
    	self.response.write("thank you")


class CronHandler(webapp2.RequestHandler):
    def get(self):

    	websites = Website.query()
    		
    	for website in websites:
    		url = 'http://' + website.heroku_name  + '.herokuapp.com'
    		try:
	          urlfetch.fetch(url=url,
	         	method=urlfetch.GET,
	         	follow_redirects=False)
	        except:
	        	#do nothing
	        	print "meh it didn't work"

class AdminHandler(webapp2.RequestHandler):
    def get(self):
    	if users.is_current_user_admin():
	    	websites = Website.query()
	    	for website in websites:
	    		self.response.write("<br><p> " + website.heroku_name + """
	    			</p><form method="post" action='/myadmin/_delete/""" + str(website.key.id()) + """'>

	    			<button type='submit'>delete</button></form><br>""" )
		else:
			self.response.write('not here go away')

class DeleteHandler(webapp2.RequestHandler):
    def post(self, url_id):
		if users.is_current_user_admin():
			heroku = Website.get_by_id( int(url_id) )
			heroku.key.delete()
			self.redirect("/myadmin" )
		else:
			self.response.write('not here go away')

			



app = webapp2.WSGIApplication([
	('/ping/herokus', CronHandler),
	('/myadmin/_delete/(\d+)', DeleteHandler),
	('/myadmin', AdminHandler),
    ('/', MainHandler),

], debug=True)
