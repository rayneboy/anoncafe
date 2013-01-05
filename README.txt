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

# Based on <code.google.com/p/mirrorrr/> by Brett Slatkin <bslatkin@gmail.com>
# and from <http://code.google.com/p/bs2grproxy/> Russell <yufeiwu@gmail.com>
# By Kevin H <rayneboy1@gmail.com>

Short Description: Simple GAE proxy written in python
Long Description:

	workflow:
		- app.yaml associates the locations used by the application's files
		- main.py runs the main application
		- config.py sets the application's configuration variables
		- controllers.py wires each web page with its corresponding handler
	
	filesystem:
		- static: files that have no dynamic content (ie css and js files)
		- template: html templates used to render content
		- lib: user and 3rd party libraries
	
	Here are some links to get you started:
	
		About GAE
			- http://www.vogella.com/articles/GoogleAppEngine/article.html
			- http://www.terminally-incoherent.com/blog/2009/02/23/your-homepage-on-google-appengine/
	
		Similar projects
			- http://code.google.com/p/mirrorrr/source/browse/#svn%2Ftrunk
			- http://code.google.com/p/bs2grproxy/
	
		Proxy server basics
			- http://tomayko.com/writings/things-caches-do
			- http://www.mnot.net/cache_docs/#DEFINITION
	
		Easy layouts with Twitter Bootstrap
			- https://wrapbootstrap.com/
		
		Webscraping/Data Processing
			- http://blog.ianbicking.org/2008/03/30/python-html-parser-performance/
			
All contributors and contributions welcome!