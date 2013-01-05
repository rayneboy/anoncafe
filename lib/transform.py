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

from lib import BeautifulSoup, url_tools
from lib.BeautifulSoup import Tag
from lib.url_tools import *
import config
import string
import sys

TRANSFORM_CONTENT_TYPES = frozenset([
  'text/html',
])

HTML_URL_TAGS = frozenset([
  'a',
  'a', 'applet', 'archive', 'area', 'audio',
  'base','blockquote','body', 'button',
  'command',
  'del','dynsrc',
  'embed',
  'form', 'frame',
  'head', 'html',
  'lowsrc',
  'img',
  'iframe', 'input', 'ins',
  'link',
  'object',
  'q',
  'script', 'source',
  'video'
])

HTML_URL_ATTRS = frozenset([
  'action', 'archive',
  'background',
  'classid', 'cite','codebase',
  'formaction', 
  'href',
  'icon',
  'longdesc',
  'src',
  'usemap',
])

def has_common_members(this, that):
    return set(this).intersection(that) != set([])

class ResponseTransformer(object):
        
    def __init__(self, response_url, response):
        
        self.response_url = response_url
        self.status_code = response.status_code
        self.headers = self.transform_headers(response.headers)
        self.content = self.transform_content(response.content)
        
    def transform_headers(self, response_headers):

        new_headers = map(lambda (key, val) : (key.strip().lower(), val), response_headers.iteritems())
        new_headers = filter(lambda (key, val) : key not in config.IGNORE_HEADERS, new_headers)
        new_headers = map(lambda (key, val) : (string.capwords(key, '-'), val), new_headers)
        new_headers = dict(new_headers)

        # check if mime type is consistent
        given_mime_type = new_headers.get('Content-Type', '')
        check_mime_type = url_tools.get_mime_extension(self.response_url)
        if given_mime_type != check_mime_type and check_mime_type is not None:
            logging.warning('resource interpreted as "%s" but transferred with MIME type "%s"' % (check_mime_type, given_mime_type))
            new_headers['Content-Type'] = check_mime_type
            
        # set the cache control
        new_headers['Cache-Control'] = 'max-age=%d' % config.EXPIRATION_RATE_S
        
        return new_headers
    
    def transform_content(self, response_content):

        # check if the page's content type should be transformed
        is_transform_type = lambda types : has_common_members(types, TRANSFORM_CONTENT_TYPES)
        page_content_type = self.headers.get('Content-Type', '').strip().split(';') # for cases like 'text/html; charset=UTF-8'
            
        if not is_transform_type(page_content_type):
            return response_content

        try:
            document = BeautifulSoup.BeautifulSoup(response_content)
        except:
            exception_type = sys.exc_info()[0]
            logging.error('exception in transform content "%s" for "%s"', str(exception_type), self.response_url)
            return response_content

        is_a_link_tag = lambda tag : tag.name in HTML_URL_TAGS
        has_url_attrs = lambda tag : has_common_members(dict(tag.attrs).keys(), HTML_URL_ATTRS)
        
        links = document.findAll(lambda tag: is_a_link_tag(tag) and has_url_attrs(tag))
        
        for link in links:
            for attr, url in link.attrs:
                if attr in HTML_URL_ATTRS:
                    link[attr] = self.fix_url(url)
                    
        plantXSSMole(document)
                    
        return document
                    
    def fix_url(self, url):
        """ URI lore: <http://www.ietf.org/rfc/rfc3986.txt> """
        
        host_name = url_tools.get_host_from_url(self.response_url)      
        url = url.strip()
        
        # check if the scheme is supported
        scheme = url_tools.get_scheme_from_url(self.response_url)
        if not (scheme.startswith('http') or scheme.startswith('https') or scheme.startswith('//')): 
            logging.error('scheme not supported for url "%s" %s' % (url, scheme))
            return url
        
        # check if the 'url' field is a special type
        if url.startswith('#') or url.startswith('javascript'):
            return url
        
        # fix absolute URLs (i.e. href='http://hostname.net/path')
        if re.match(ABSOLUTE_URL_RE, url):
            if urlparse.urlsplit(url).netloc:
                new_url = '/' + url_tools.strip_scheme_from_url(url)
                logging.debug('absolute url transformation "%s" -> "%s"', url, new_url) 
                return new_url 
        
        # fix protocol relative URLs (i.e. src='//hostname.com/path')
        if re.match(PROTOCOL_RELATIVE_URL_RE, url):
            new_url = '/' + url[len('//'):] 
            logging.debug('protocol absolute url transformation "%s"', url, new_url)
            return new_url
                    
        # fix root relative URLs (i.e. src='/subpath_of_host_url/path')
        if re.match(ROOT_RELATIVE_URL_RE, url):
            if url == '/':
                new_url = config.PROXY_SITE + host_name
            else:
                new_url = '/' + host_name + url_tools.get_path_from_url(url)

            logging.debug('root relative transformation "%s"', url, new_url)                
            return new_url
            
        
        # fix directory relative URLs (i.e. src='file_in_the_same_directory/path')
        if re.match(DIRECTORY_RELATIVE_URL_RE, url):
            new_url = config.PROXY_SITE + popd(self.response_url) + '/' + url
            logging.debug('directory relative transformation "%s"', url, new_url) 
            return new_url 
        
        # ignore traversal relative URLs for now (i.e. src='../another_dir_file')
        if re.match(TRAVERSAL_RELATIVE_URL_RE, url):
            pass
        
        return url
                    
def plantXSSMole(document):
    xss = BeautifulSoup.BeautifulSoup(XSS)
    body = document.body
    
    if not body: return
    
    body['onload'] = 'transmitDataToSource()'
    
    mole = xss.iframe
    wire = xss.script
    
    body.insert(len(body.contents), mole)
    body.insert(len(body.contents), wire)
    
XSS = """
            <iframe id="mole" src='' height='0' width='0' frameborder='0'></iframe>

            <script type="text/javascript">
                function transmitDataToSource() {
                    var height = document.body.scrollHeight;

                    // transmit data 'on the wire' to the parent through the 'mole' iframe
                    var wire = document.getElementById('mole');

                    // use a cachebuster to stop browser caching interfering
                    wire.src = '%(script)s?height='+height+'&cacheb='+Math.random();
                }
            </script>
        """ % {'script': config.PROXY_SITE + 'js/xss.html'}