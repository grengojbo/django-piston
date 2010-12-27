#!/usr/bin/env python
# encoding: utf-8
"""
The MIT License

Copyright (c) 2007 Leah Culver

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Example consumer. This is not recommended for production.
Instead, you'll want to create your own subclass of OAuthClient
or find one that works with your web framework.
"""

import httplib
import time
import oauth.oauth as oauth
import os

# settings for the local test consumer
from urllib import urlencode

SERVER = 'localhost'
PORT = 8080

# fake urls for the test server (matches ones in server.py)
#REQUEST_TOKEN_URL = 'https://photos.example.net/request_token'
#ACCESS_TOKEN_URL = 'https://photos.example.net/access_token'
#AUTHORIZATION_URL = 'https://photos.example.net/authorize'
CALLBACK_URL = 'http://printer.example.com/request_token_ready'
#RESOURCE_URL = 'http://photos.example.net/photos'

CONSUMER_SERVER = os.environ.get("CONSUMER_SERVER") or 'localhost'
CONSUMER_PORT = os.environ.get("CONSUMER_PORT") or '8000'
print CONSUMER_SERVER , CONSUMER_PORT

# fake urls for the test server (matches ones in server.py)
REQUEST_TOKEN_URL = 'http://%s:%s/api/oauth/request_token/' % (CONSUMER_SERVER, CONSUMER_PORT)
REQUEST_TOKEN = '/api/oauth/request_token/'
ACCESS_TOKEN = '/api/oauth/access_token/'
ACCESS_TOKEN_URL = 'http://%s:%s/api/oauth/authorize/' % (CONSUMER_SERVER, CONSUMER_PORT)
CALLBACK_URL = '/api/oauth/authorize/'
AUTHORIZATION_URL = 'http://%s:%s/api/oauth/authorize/' % (CONSUMER_SERVER, CONSUMER_PORT)
AUTHORIZATION = '/api/oauth/authorize/'

RESOURCE_URL = 'http://%s:%s/api/posts.json' % (CONSUMER_SERVER, CONSUMER_PORT)
RESOURCE = '/api/posts.json'

# key and secret granted by the service provider for this consumer application - same as the MockOAuthDataStore
CONSUMER_KEY = '8aZSFj3W54h8J8sCpx'
CONSUMER_SECRET = 'T5XkNMkcjffDpC9mNQJbyQnJXGsenYbz'

# example client using httplib with headers
class SimpleOAuthClient(oauth.OAuthClient):

    def __init__(self, server, port=httplib.HTTP_PORT, request_token_url='', access_token_url='', authorization_url=''):
        self.server = 'localhost'
        self.port = 8000
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url
        self.connection = httplib.HTTPConnection("%s:%d" % (self.server, self.port))

    def fetch_request_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        self.connection.request(oauth_request.http_method, REQUEST_TOKEN, headers=oauth_request.to_header())
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())

    def fetch_access_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        self.connection.request(oauth_request.http_method, ACCESS_TOKEN, headers=oauth_request.to_header())
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())

    def authorize_token(self, oauth_request):
        # via url
        # -> typically just some okay response
        self.connection.request(oauth_request.http_method, "{0}?{1}".format(AUTHORIZATION, urlencode(oauth_request.parameters, doseq=True)))
        response = self.connection.getresponse()
        return response.read()

    def access_resource(self, oauth_request):
        # via post body
        # -> some protected resources
        headers = {'Content-Type' :'application/x-www-form-urlencoded'}
        self.connection.request('POST', RESOURCE, body=oauth_request.to_postdata(), headers=headers)
        response = self.connection.getresponse()
        return response.read()

def run_example():

    # setup
    print '** OAuth Python Library Example **'
    client = SimpleOAuthClient(SERVER, PORT, REQUEST_TOKEN_URL, ACCESS_TOKEN_URL, AUTHORIZATION_URL)
    consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
    signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
    pause()

    # get request token
    print '* Obtain a request token ...'
    pause()
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, callback=CALLBACK_URL, http_url=client.request_token_url)
    oauth_request.sign_request(signature_method_plaintext, consumer, None)
    print 'REQUEST (via headers)'
    print 'parameters: %s' % str(oauth_request.parameters)
    pause()
    print oauth_request
    token = client.fetch_request_token(oauth_request)
    print 'GOT'
    print 'key: %s' % str(token.key)
    print 'secret: %s' % str(token.secret)
    print 'callback confirmed? %s' % str(token.callback_confirmed)
    pause()

    print '* Authorize the request token ...'
    pause()
    oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=client.authorization_url)
    print 'REQUEST (via url query string)'
    print 'parameters: %s' % str(oauth_request.parameters)
    pause()
#    print oauth_request.http_method
#    # this will actually occur only on some callback
    response = client.authorize_token(oauth_request)
#    print 'GOT'
#    print response
#    # sad way to get the verifier
#    import urlparse, cgi
#    query = urlparse.urlparse(response)[4]
#    params = cgi.parse_qs(query, keep_blank_values=False)
#    verifier = params['oauth_verifier'][0]
#    print 'verifier: %s' % verifier
#    pause()
#
#    # get access token
#    print '* Obtain an access token ...'
#    pause()
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, verifier=None, http_url=client.access_token_url)
    oauth_request.sign_request(signature_method_plaintext, consumer, token)
    print 'REQUEST (via headers)'
    print 'parameters: %s' % str(oauth_request.parameters)
    pause()
    token = client.fetch_access_token(oauth_request)
    print 'GOT'
    print 'key: %s' % str(token.key)
    print 'secret: %s' % str(token.secret)
    pause()
#
    # access some protected resources
    print '* Access protected resources ...'
    pause()
    parameters = {'title': 'test', 'content': 'original'} # resource specific params
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_method='POST', http_url=RESOURCE, parameters=parameters)
    oauth_request.sign_request(signature_method_hmac_sha1, consumer, token)
    print 'REQUEST (via post body)'
    print 'parameters: %s' % str(oauth_request.parameters)
    pause()
    params = client.access_resource(oauth_request)
    print 'GOT'
    print 'non-oauth parameters: %s' % params
    pause()

def pause():
    print ''
    time.sleep(1)

if __name__ == '__main__':
    run_example()
    print 'Done.'