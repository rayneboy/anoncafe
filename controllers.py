# -*- coding: utf-8 -*-

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

from google.appengine.api import users, memcache, urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from lib import url_tools, transform
from models import MirrorEntity
import config
import logging
import sys

HTTP_PREFIX = "http://"
FETCH_ATTEMPTS = 2

class HomeController(webapp.RequestHandler):
    
    context = {}
    
    def get(self):
        self.context['quote'] = {'content': '“Proclaim the truth and do not be silent through fear.”',
                             'source': 'St. Catherine of Siena'
        }
        
        self.response.out.write(template.render('template/home.html', self.context))
    
    def post(self):
        input_url = url_tools.validate_url(self.request.get("url_entry"), self.context);
        
        if input_url:
            # switch to ProxyHandler and send a GET request for input_url
            return self.redirect("/" + input_url)
        else:
            logging.debug("user entered invalid input_url %s" % input_url)
            return self.redirect("/")
            
class ProxyController(webapp.RequestHandler):
    
    record_last_host = config.PROXY_SITE

    def get(self, target_host):
        self.method = 'GET'
        self.mirror_url(self.get_url_from_request())
        
    def post(self, target_host):
        self.method = 'POST'
        self.mirror_url(self.get_url_from_request())
        
    def get_url_from_request(self):
        return self.request.path_qs[1:]
    
    def mirror_url(self, target_url):
        
        target_url = url_tools.validate_url(target_url)
        
        if not target_url:
            logging.debug("user entered invalid input_url %s" % target_url)
            return self.redirect("/")

        mirror_url = HTTP_PREFIX + target_url # the URL the proxy is attempting to mirror
        mirror_content = self.get_mirror_content(mirror_url)
        
        if mirror_content is None:
            return self.error(404)
        
        # TODO: investigate why self.response.headers = mirror_content.headers doesn't work
        # write out the response payload 
        for key in mirror_content.headers.keys():
            self.response.headers[key] = mirror_content.headers[key]
        self.response.out.write(mirror_content.content)
        #self.response.out.write(template.render('template/proxy.html', {'mirror_content': mirror_content.content}))

    def get_mirror_content(self, mirror_url):
        # attempt a cache lookup
        url_content = memcache.get(mirror_url)
        
        # cache hit
        if url_content is not None:
            return url_content
        # cache miss, attempt remote fetch
        else:
            logging.debug("cache miss, fetching '%s'", mirror_url)
            new_content = self.fetch_and_cache(mirror_url)
            return new_content
        
    def fetch_and_cache(self, mirror_url):
        if url_tools.is_absolute_url(mirror_url):
            self.record_last_host = url_tools.get_host_from_url(mirror_url)
        else:
            mirror_url = url_tools.join(HTTP_PREFIX, self.record_last_host, mirror_url)
        
        host_name = url_tools.get_host_from_url(mirror_url)
            
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec8.html 8.1.3 Proxy Servers
        adjusted_headers = dict(self.request.headers)
        adjusted_headers['Connection'] = 'close'
        logging.debug("request headers '%s' of '%s'", url_tools.dict_to_s(adjusted_headers), mirror_url)
                      
        try:
            # fetch the requested url
            for attempt in range(FETCH_ATTEMPTS):
                response = urlfetch.fetch(mirror_url, self.request.body, self.method, adjusted_headers)
                logging.info('url fetch attempt %d for "%s" successful', attempt + 1, mirror_url)
                break
        except urlfetch.Error:
            exception_type = sys.exc_info()[0]
            logging.error('url fetch exception "%s" for "%s"', str(exception_type), mirror_url)
            return None

        transform_response = transform.ResponseTransformer(mirror_url, response)
        
        # cache the transformed entity and return
        mirror_content = MirrorEntity(mirror_url,
                                      host_name,
                                      transform_response.status_code,
                                      transform_response.headers,
                                      transform_response.content)
        memcache.add(mirror_url, mirror_content, config.EXPIRATION_RATE_S)

        return mirror_content

class AdminController(webapp.RequestHandler):
    
    def get(self):
        user = users.get_current_user()

        if user is not None and users.is_current_user_admin():
            
            template_context = {
                 'admin_name': user.nickname(),
                 'logout': users.create_logout_url("/home"),
                 'cache': str(memcache.get_stats()),
                 'logs': ''
            }
            
            self.response.out.write(template.render('template/admin.html', template_context))
            
        else:
            self.redirect(users.create_login_url("/admin"))

    def post(self):
        self.response.headers['content-type'] = 'text/plain'
        self.response.out.write('Flush successful: %s' % memcache.flush_all())
