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

PROXY_SITE = 'http://localhost:8080/'#'anoncafe.appspot.com/'
EXPIRATION_RATE_S = 3600

IGNORE_HEADERS = frozenset([
  'set-cookie',
  'expires',
  'cache-control',
  'connection',
  'keep-alive',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailers',
  'transfer-encoding',
  'upgrade',
])

IGNORE_HOSTS = frozenset([
  'anoncafe.appspot.com',
  'favicon.ico'
])