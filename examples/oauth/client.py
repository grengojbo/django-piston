#!/usr/bin/env python
# encoding: utf-8
import httplib2
import time

__author__ = 'jbo'

import os
import oauth2 as oauth
#from piston import oauth
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
#from django.test.client import Client
from django.utils.http import urlencode
import urllib, base64



CONSUMER_SERVER = os.environ.get("CONSUMER_SERVER") or 'localhost'
CONSUMER_PORT = os.environ.get("CONSUMER_PORT") or '8000'
print CONSUMER_SERVER , CONSUMER_PORT

# fake urls for the test server (matches ones in server.py)
REQUEST_TOKEN_URL = 'http://%s:%s/api/oauth/request_token/' % (CONSUMER_SERVER, CONSUMER_PORT)
ACCESS_TOKEN_URL = 'http://localhost:8000/api/oauth/access_token/'
AUTHORIZE_URL = 'http://%s:%s/api/oauth/authorize/' % (CONSUMER_SERVER, CONSUMER_PORT)

oauth_callback = 'http://%s:%s/api/posts.json' % (CONSUMER_SERVER, CONSUMER_PORT)

CONSUMER_KEY = '8aZSFj3W54h8J8sCpx'
CONSUMER_SECRET = 'T5XkNMkcjffDpC9mNQJbyQnJXGsenYbz'

def main():
    from piston import oauth
    signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
    oaconsumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    request = oauth.OAuthRequest.from_consumer_and_token(oaconsumer, http_url=REQUEST_TOKEN_URL)
    request.sign_request(signature_method, oaconsumer, None)
    print urlencode(request.parameters, doseq=True)

    #response = client.get(REQUEST_TOKEN_URL, request.parameters)
    #oatoken = oauth.OAuthToken.from_string(response.content)
    h = httplib2.Http(".cache")
    resp, content = h.request("{0}?{1}".format(REQUEST_TOKEN_URL, urlencode(request.parameters, doseq=True)), "GET")
    oatoken = oauth.OAuthToken.from_string(content)
    request = oauth.OAuthRequest.from_token_and_callback(token=oatoken,
                callback=oauth_callback,
                http_url=AUTHORIZE_URL)
    request.sign_request(signature_method, oaconsumer, oatoken)
    print resp
    print oatoken.key, oatoken.secret
    data = dict(oauth_token=oatoken.key, title='test', content='xcvzxcv xkcjlkxb lkjxcbkljx cvlbjk')
    resp, content = h.request(oauth_callback, "POST", urlencode(data))
    #print resp

def testMain():
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)

    # Create our client.
    client = oauth.Client(consumer)

    # The OAuth Client request works just like httplib2 for the most part.
    resp, content = client.request(REQUEST_TOKEN_URL, "GET")
    print resp
    print content

def sigMain():
    params = {
    'oauth_version': "1.0",
    'oauth_nonce': oauth.generate_nonce(),
    'oauth_timestamp': int(time.time()),
    'user': 'testuser',
    'content': 'sdfgsdfg fdgdsfg',
    'title': 'test'
}
    token = oauth.Token(key="9eFSHnns6tMHzVqZjz", secret="gAeu3r7sneZkZnAThvCkH9SYTfcdvvPS")
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    # Set our token/key parameters
    params['oauth_token'] = token.key
    params['oauth_consumer_key'] = consumer.key
    # Create our request. Change method, etc. accordingly.
    req = oauth.Request(method="POST", url=oauth_callback, parameters=params)
    #client = oauth.Client()

    # Sign the request.
    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, token)
    #resp, content = client.request(req)
    #print resp
    #print content


    print req

if __name__ == '__main__':
    #main()
    #testMain()
    sigMain()

