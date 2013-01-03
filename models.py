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

from google.appengine.ext import db

class Link(db.Model):
    """ persistent model object used for link menu """
    
    url = db.LinkProperty()
    entry_time = db.DateTimeProperty(auto_now_add=True)
    added_by = db.StringProperty()
    
class MirrorEntity(object):
    """ serializable model object used for storing into memcache """
    
    def __init__(self, mirror_url, host_name, status, headers, content):
        self.mirror_url = mirror_url
        self.host_name = host_name
        self.status = status
        self.headers = headers
        self.content = content
