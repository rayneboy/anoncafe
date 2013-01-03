#!/usr/bin/env python
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

from controllers import AdminController, HomeController, ProxyController
from google.appengine.ext import webapp
import os
import sys
import wsgiref.handlers

DEBUG = True

def fix_path():
    """ add path for user libraries under the 'lib' folder """
    sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
    
application = webapp.WSGIApplication([("/", HomeController),
                                      ("/home", HomeController),
                                      ("/admin", AdminController),
                                      ("/([^/]+).*", ProxyController)], debug=DEBUG)

def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()