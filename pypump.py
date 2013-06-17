# -*- coding: utf-8 -*-
##
# Copyright (C) 2010-2012 Reality <tinmachin3@gmail.com> and Psychedelic Squid <psquid@psquid.net>
# Copyright (C) 2013 Jessica T. (Tsyesika) <xray7224@googlemail.com>
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##

import urllib.request
import urllib.error
import urllib.parse
import json

import oauth.oauth as oauth
import loader

from exceptions import PyPumpException

class PyPump(object):

    PARAM_TOKEN = "oauth_token"
    PARAM_TOKEN_SECRET = "oauth_token_secret"

    URL_CLIENT_REGISTRATION = "/api/client/register"

    loader = None

    def __init__(self, server, key=None, secret=None, 
                client_name="", client_type="web", token=None, 
                token_secret=None, save_token=None, secure = False):
        """ This will initate the pump.io library 
        == required ==
        server = this is the server you're going to connect to (microca.st, pumpity.net, etc...)
        
        == optional ==
        key = This is your client key
        secret = this is the client secret
        client_name = this is the name of the client
        client_type = the type of your client (defaults to 'web')
        token = This is the token if you've already authenticated by oauth before (default None)
        token_secret = this is your token secret if you've already athenticated before (default None)
        save_token = this is a callback (func/method) which is called to save token and token_secret when they've been got (default None)
        secure = Use https or not
        """

        if "@" in server:
            # it's a web fingerprint!
            self.nickname, self.server = server.split("@")
        else:
            self.server = server
            self.nickname = None # should be set with <instance>.set_nickname(<nickname>)

        if secure:
            self.proto = "https://"
        else:
            self.proto = "http://"
        
        self.loader = loader.Loader(self)

        # oauthy stuff
        if not (key and secret):
            # okay we should assume then we're dynamically registrering a client
            self.consumer = oauth.OAuthConsumer(
                client_name=client_name, 
                client_type=client_type,
                server="{proto}{server}{endpoint}".format(proto=self.proto, server=self.server, endpoint=self.URL_CLIENT_REGISTRATION)
            )
        else:
            self.consumer = oauth.OAuthConsumer(key, secret)

        
        self.pump = urllib.request.build_opener()
        
        if not (token and token_secret):
            # we need to make a new oauth request
            self.oauth_request() # this does NOT return access tokens but None
        else:
            self.token = token
            self.token_secret = token_secret
        
        self.oauth_token = oauth.OAuthToken(self.token, self.token_secret)


    ##
    # getters to expose some data which might be useful
    ##
    def get_registration(self):
        """ This is if key and secret weren't specified at instansiation so we registered them """
        return (self.consumer.key, self.consumer.secret, self.consumer.expirey)

    def get_token(self):
        """ This is for when we don't have a token but we've registered one (by asking the user) """
        return (self.token, self.token_secret)

    def set_nickname(self, nickname):
        """ This sets the nickname being used """
        if nickname:
            self.nickname = str(nickname) # everything in python can be converted to a string right?
        else:
            # they didn't enter a nickname?
            raise Exception("Nickname can't be of length 0")

    ## 
    # server request stuff
    ##
    def request(self, endpoint, method="GET", data="", attempts=10):
        """ This will make a request to <proto>//<self.server>/<endpoint> with oauth headers
        proto = self.proto (https or http)
        method = GET (default), POST or PUT
        attempts = this is how many times it'll try re-attempting
        """
        if not (self.token and self.token_secret):
            # this shouldn't happen but just incase
            raise PyPumpException('Need to initiate oauth')

        if "/" == endpoint[0]:
            endpoint = endpoint[1:] # remove inital / as we add it

        if data:
            # we actually need to make it into a json object as that's what pump.io deals with.
            data = json.dumps(data)

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.oauth_token, 
                                                                   http_method=method, http_url="%s%s/%s" % (
                                                                            self.proto, self.server, endpoint)
                                                                    )

        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, self.oauth_token)
        attempts_done = 0

        while attempts_done < attempts:
            try:
                if "GET" == method:
                    request = urllib.request.Request("%s%s/%s" % (self.proto, self.server, endpoint), 
                                                                 headers=oauth_request.to_header('OAuth'))
                else:
                    request = urllib.request.Request("%s%s/%s" % (self.proto, self.server, endpoint), 
                                                                 headers=oauth_request.to_header('OAuth'))

                    request.add_header("Content-Type", "application/json")
                    request.data = data.encode()
                return json.loads(self.pump.open(request).read().decode("utf-8"))
            except Exception:
                attempts_done += 1

        return '' # failed :(


    ##
    # OAuth specific stuff
    ##
    def oauth_request(self):
        """ Makes a oauth connection """
        # get tokens from server and make a dict of them.
        tokens = {}
        server_token = self.request_token()
        for elem in server_token.split("&"):
            key, value = elem.split("=")
            tokens[key] = value

        # now we need the user to authorize me to use their pump.io account
        code = self.get_access(tokens[self.PARAM_TOKEN])
        access = self.request_access(tokens[self.PARAM_TOKEN], tokens[self.PARAM_TOKEN_SECRET], code) 
        access = access.split("&")
        for item in access:
            # don't change the order >.< as they both start with oauth_token
            if item.startswith("oauth_token_secret"):
                self.token_secret = item[19:] # len("oauth_token_secret=") == 19
            elif item.startswith("oauth_token"):
                self.token = item[12:] # len("oauth_token") == 12

    def get_access(self, token):
        """ this asks the user to let us use their account """

        print("To allow us to use your pump.io please follow the instructions at:")
        print("%s%s/oauth/authorize?oauth_token=%s" % (self.proto, self.server, token))
        code = input("It'll give you a verifier code, please enter it: ")
        code = code.replace(" ", "") # lets make sure they didn't put any spaces in it.
        return code

    def request_token(self):
        """ Gets a request token so that we can then ask the user for access to the accoutn """
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, 
                                                                   callback="oob", 
                                                                   http_method="POST", 
                                                                   http_url="%s%s/oauth/request_token" % (
                                                                            self.proto, self.server
                                                                            )
                                                                   )

        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, None)

        request = urllib.request.Request("%s%s/oauth/request_token" % (self.proto, self.server), 
                                                                       data=oauth_request.to_postdata().encode(), 
                                                                       headers=oauth_request.to_header('OAuth')
                                        )

        return self.pump.open(request).read().decode("utf-8")

    def request_access(self, token, token_secret, code):
        """ This is for when we've got the user's access value and we're asking the server for our access token """
        request_token = oauth.OAuthToken(token, token_secret)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, 
                                                                   token=request_token, 
                                                                   verifier=code,
                                                                   callback="oob", 
                                                                   http_method="POST", 
                                                                   http_url="%s%s/oauth/access_token" % (
                                                                        self.proto, self.server)
                                                                   )

        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, request_token)
        request = urllib.request.Request("%s%s/oauth/access_token" % (self.proto, self.server), 
                                         data=oauth_request.to_postdata().encode(), 
                                         headers=oauth_request.to_header())

        return self.pump.open(request).read().decode("utf-8")

