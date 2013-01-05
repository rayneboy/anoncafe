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

# By Kevin H <rayneboy1@gmail.com>

from config import IGNORE_HOSTS
import logging
import mimetypes
import re
import simplejson as json
import urllib
import urlparse

ABSOLUTE_URL_RE           = '(http(s)?:/{0,2})?[^/\.]+\..*'
PROTOCOL_RELATIVE_URL_RE  = '//[^/]+\..*'
TRAVERSAL_RELATIVE_URL_RE = '.*(\.(\.)?)/.*'
DIRECTORY_RELATIVE_URL_RE = '([^(/|//)]+/)*[^(/|//)]+'
ROOT_RELATIVE_URL_RE      = '/[^/].*'

def is_absolute_url(url):
    host = get_host_from_url(url)
    is_absolute = re.match(ABSOLUTE_URL_RE, host) is not None
    
    return is_absolute

def get_mime_extension(url):
    return mimetypes.guess_type(url)[0]

def get_host_from_url(url):
    """ urlsplit doesn't work unless url is well formed:
        (eg 'scheme://hostname/path/subpath/file#fragment') """
    
    # strip URLs that have a scheme such as a leading 'http(s)://'
    scheme = get_scheme_from_url(url)
    if scheme: url = url[len(scheme):]
    
    # determine the host name of the url, which is left of the path separator
    path_separator = url.find("/")
    
    if path_separator == -1:
        host = url
    else:
        host = url[:path_separator]
    
    return host

def get_path_from_url(url):
    """ urlsplit doesn't work unless url is well formed:
        (eg 'scheme://hostname/path/subpath/file#fragment') """
        
    # strip URLs that have a scheme such as a leading 'http(s)://'
    url_components = urlparse.urlsplit(url)
    scheme = url_components.scheme
    
    if scheme: url = url[len('%s://' % scheme):]
    
    # determine the host name of the url, which is right of the path separator
    path_separator = url.find("/")
    
    if path_separator == -1:
        path = url
    else:
        path = url[path_separator:]
    
    return path

def get_scheme_from_url(url):
    if url.startswith('//'):
        return '//'
    else:
        SCHEME_RE = r'(?P<scheme>([^:/?#]+)?:/{0,2})'
        match = re.match(SCHEME_RE, url)
        
        if match:
            scheme = match.group('scheme')
        else:
            scheme = ''

        return scheme

def join(scheme, base, path):
    scheme = get_scheme_from_url(scheme)
    
    return urlparse.urljoin(scheme + '://' + base.lstrip('/'), path.lstrip('/'))

def popd(path):
    """ return the top directory of the given path """
    last_path_sep = path.rfind('/')
    
    if last_path_sep == -1:
        return path
    else:
        return path[:last_path_sep]

def strip_scheme_from_url(url):
    # strip URLs that have a scheme such as a leading 'http(s)://'
    url_components = urlparse.urlsplit(url)
    netloc = url_components.netloc
    scheme = url_components.scheme
    
    if scheme and netloc:
        url = url[url.find(netloc):]
    
    return url
    
def validate_url(input_url, context={}):

    if not input_url: return None
    
    # decode URL-encoded characters
    input_url = urllib.unquote(input_url)
    
    # check each component of input URL
    url_components = urlparse.urlsplit(input_url)
    
    # check if the scheme is valid
    scheme = url_components.scheme
    
    if scheme:
        # strip URLs that have a scheme such as a leading 'http(s)://'
        if scheme == 'http' or scheme == 'https': 
            input_url = input_url[len('%s://' % scheme): ]
        # scheme is unsupported
        else:
            context['error_msg']= 'URL scheme error "%s"\n' \
								  'Please enter a valid url address' % input_url
            logging.debug(context['error_msg'])
            
            return None
        
    # check if the host is valid
    host = get_host_from_url(input_url)
    
    if not host:
        context['error_msg']= 'URL host  error "%s"\n' \
							  'Please enter a valid url address' % input_url
        logging.debug(context['error_msg'])
            
        return None
    
    for ignore in IGNORE_HOSTS:
        if ignore in host:
            logging.warn('attempt to access invalid url "%s"' % ignore)
            return None
            
    # passes validation
    return input_url

def dict_to_s(d):
    return json.dumps(dict(d), sort_keys=True, indent=4, separators=(',', ': '))