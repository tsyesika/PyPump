# -*- coding: utf-8 -*-

##
#   Copyright (C) 2010-2012 Reality <tinmachin3@gmail.com> and Psychedelic Squid <psquid@psquid.net>
#   Copyright (C) 2013 Jessica T. (Tsyesika) <xray7224@googlemail.com>
# 
#   This program is free software: you can redistribute it and/or modify 
#   it under the terms of the GNU General Public License as published by 
#   the Free Software Foundation, either version 3 of the License, or 
#   (at your option) any later version. 
# 
#   This program is distributed in the hope that it will be useful, 
#   but WITHOUT ANY WARRANTY; without even the implied warranty of 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
#   GNU General Public License for more details. 
# 
#   You should have received a copy of the GNU General Public License 
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
##

import urllib.request
import json

import requests
from requests_oauthlib import OAuth1
import openid
import loader

from exceptions import PyPumpException

class PyPump(object):

    PARAM_VERIFER = "oauth_verifier"
    PARAM_TOKEN = "oauth_token"
    PARAM_TOKEN_SECRET = "oauth_token_secret"

    URL_CLIENT_REGISTRATION = "/api/client/register"

    loader = None

    def __init__(self, server, key=None, secret=None, 
                client_name="", client_type="native", token=None, 
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
            self.proto = "https"
        else:
            self.proto = "http"
        
        self.loader = loader.Loader(self)

        # first, if we need to register our client
        if not (key or secret):
            oid = openid.OpenID(
                    protocol=secure,
                    server=server,
                    client_name=client_name,
                    application_type=client_type
                    )
            self.consumer = oid.register_client()
        else:
            self.consumer = openid.Consumer()
            self.consumer.key = key
            self.consumer.secret = secret

        if not (token and token_secret):
            # we need to make a new oauth request
            self.oauth_request() # this does NOT return access tokens but None
        else:
            self.token = token
            self.token_secret = token_secret

        self.client = OAuth1(
                client_key=self.consumer.key,
                client_secret=self.consumer.secret,
                resource_owner_key=self.token,
                resource_owner_secret=self.token_secret
                )        

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
    def request(self, endpoint, method="GET", data="", raw=False, params=None, attempts=10):
        """ This will make a request to <proto>//<self.server>/<endpoint> with oauth headers
        proto = self.proto (https or http)
        method = GET (default), POST or PUT
        attempts = this is how many times it'll try re-attempting
        """

        params = {} if params is None else params

        if not (self.token and self.token_secret):
            # this shouldn't happen but just incase
            raise PyPumpException('Need to initiate oauth')

        if endpoint.startswith("/"):
            endpoint = endpoint[1:] # remove inital / as we add it

        if data and isinstance(data, (dict, list)):
            # we actually need to make it into a json object as that's what pump.io deals with.
            data = json.dumps(data)

        if raw is False:
            endpoint = "{proto}://{server}/{endpoint}".format(
                    proto=self.proto,
                    server=self.server,
                    endpoint=endpoint
                    )
        

        for attempt in range(attempts):
            if method == "POST":
                request = requests.post(endpoint, auth=self.client, params=params, data=data)
            elif method == "GET":
                request = requests.get(endpoint, auth=self.client, params=params)

            if request.status_code == 200:
                # huray!
                return json.loads(request.content.decode("utf-8"))
            elif request.status_code in [400]:
                # can't do much
                raise PyPumpException("Recieved a 400 bad request error. This is likely due to an OAuth failure")

        return '' # failed :(


    ##
    # OAuth specific stuff
    ##
    def oauth_request(self):
        """ Makes a oauth connection """
        # get tokens from server and make a dict of them.
        server_token = self.request_token()
        
        # now we need the user to authorize me to use their pump.io account
        server_token[self.PARAM_VERIFER] = self.get_access(tokens[self.PARAM_TOKEN])
        access = self.request_access(tokens[self.PARAM_TOKEN], tokens[self.PARAM_TOKEN_SECRET], tokens[self.PARAM_VERIFIER]) 
    
    def get_access(self, token):
        """ this asks the user to let us use their account """

        print("To allow us to use your pump.io please follow the instructions at:")
        print("{proto}://{server}/oauth/authorize?oauth_token={token}".format(
                proto=self.proto,
                server=self.server,
                token=token
                ))
        
        code = input("Verifier Code: ").lstrp(" ").rstrip(" ")
        return code

    def request_token(self):
        """ Gets a request token so that we can then ask the user for access to the accoutn """
        client = OAuth1(
                client_key=self.consumer.key,
                client_secret=self.consumer.secret,
                callback_uri="oob"
                )
        
        req = requests.post(
                "{proto}://{server}/oauth/request_token".format(
                        proto=self.proto,
                        server=self.server
                        ),
                auth=client
                )
        
        data = urllib.request.parse_qs(r.content)
        data = {
            "oauth_token": data[self.PARAM_TOKEN][0],
            "oauth_token_secret": data[self.PARAM_TOKEN_SECRET][0]
        }

        return data

    def request_access(self, token, token_secret, code):
        """ This is for when we've got the user's access value and we're asking the server for our access token """
        client = OAuth1(
                client_key=self.consumer.key,
                client_secret=self.consumer.secret,
                resource_owner_key=token,   
                resource_owner_secret=token_secret,
                verifier=code
                )

        req = requests.post("{proto}://{server}/oauth/access_token".format(
                        proto=self.proto,
                        server=self.server,
                        ),
                auth=client)
        
        data = urllib.request.parse_qs(req.content)

        self.token = data[self.PARAM_TOKEN]
        self.token_secret = data[self.PARAM_TOKEN_SECRET]
        
        
