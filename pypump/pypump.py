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

import json

import requests
from requests_oauthlib import OAuth1
import openid

from compatability import *
from exception import PyPumpException

# load models
from models.note import Note
from models.comment import Comment
from models.person import Person
from models.image import Image
from models.inbox import Inbox
from models.location import Location

class PyPump(object):

    PARAM_VERIFER = to_bytes("oauth_verifier")
    PARAM_TOKEN = to_bytes("oauth_token")
    PARAM_TOKEN_SECRET = to_bytes("oauth_token_secret")

    URL_CLIENT_REGISTRATION = "/api/client/register"

    loader = None
    protocol = "https"

    def __init__(self, server, key=None, secret=None, 
                client_name="", client_type="native", token=None, 
                token_secret=None):
        """
            This is the main pump instance, this handles the oauth,
            this also holds the models.

            Don't forget if you want to use https ensure the secure flag is True
        """
        openid.OpenID.pypump = self # pypump uses PyPump.requester.

        if "@" in server:
            # it's a web fingerprint!
            self.nickname, self.server = server.split("@")
        else:
            self.server = server
            self.nickname = None # should be set with <instance>.set_nickname(<nickname>)

        # Fix #24 by checking
        if (key is None or secret is None) and (token or token_secret):
            raise Exception("If token and/or token_secret are supplied you must supply key and secret too")

        self.populate_models()

        # first, if we need to register our client
        if not (key or secret):
            oid = openid.OpenID(
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
                client_key=to_unicode(self.consumer.key),
                client_secret=to_unicode(self.consumer.secret),
                resource_owner_key=to_unicode(self.token),
                resource_owner_secret=to_unicode(self.token_secret)
                )        

    def populate_models(self):
        # todo: change me
        self.Note = Note
        self.Note._pump = self

        self.Comment = Comment
        self.Comment._pump = self
        
        self.Inbox = Inbox
        self.Inbox._pump = self

        self.Image = Image
        self.Image._pump = self

        self.Person = Person
        self.Person._pump = self

        self.Location = Location
        self.Location._pump = self

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
    # server 
    ##
    def request(self, endpoint, method="GET", data="", raw=False, params=None, attempts=10):
        """ This will make a request to <self.protocol>://<self.server>/<endpoint> with oauth headers
        method = GET (default), POST or PUT
        attempts = this is how many times it'll try re-attempting
        """

        params = {} if params is None else params

        if endpoint.startswith("/"):
            endpoint = endpoint[1:] # remove inital / as we add it

        if data and isinstance(data, dict):
            # we actually need to make it into a json object as that's what pump.io deals with.
            data = json.dumps(data)

        data = to_unicode(data)

        if raw is False:
            url = "{protocol}://{server}/{endpoint}".format(
                    protocol=self.protocol,
                    server=self.server,
                    endpoint=endpoint
                    )
        else:
            url = endpoint

        for attempt in range(attempts):
            if method == "POST":
                request = {
                        "auth": self.client,
                        "headers": {"Content-Type": "application/json"},
                        "params": params,
                        "data": data,
                        }
                response = self._requester(requests.post, endpoint, raw, **request)
            elif method == "GET":
                request = {
                        "params": params,
                        "auth": self.client,
                        }
  
                response = self._requester(requests.get, endpoint, raw, **request)

            if response.status_code == 200:
                # huray!
                return response.json()
            elif response.status_code in [400]:
                # can't do much
                try:
                    try:
                        data = response.json()
                        error = data["error"]
                    except ValueError:
                        error = response.content
                    
                    if not error:
                        raise IndexError # yesss i know.
                except IndexError:
                    error = "Recieved a 400 bad request error. This is likely due to an OAuth failure"
                raise PyPumpException(error)
        
        # failed, oh no!
        error = "Failed to make request to {0} ({1} {2})".format(url, method, data)
        raise PyPumpException(error)
    def _requester(self, fnc, endpoint, raw=False, **kwargs):
        if not raw:
            url = "{protocol}://{server}/{endpoint}".format(
                    protocol=self.protocol,
                    server=self.server,
                    endpoint=endpoint
                    )
        else:
            url = raw

        try:
            response = fnc(url, **kwargs)
            return response
        except requests.exceptions.ConnectionError:
            if self.protocol == "http":
                raise # shoot this seems real.
            self.set_http()
            return self._requester(fnc, endpoint, raw, **kwargs)

    def set_https(self):
        """ Enforces protocol to be https """
        self.protocol = "https"

    def set_http(self):
        """ Sets protocol to be http """
        self.protocol = "http"

    ##
    # OAuth specific stuff
    ##
    def oauth_request(self):
        """ Makes a oauth connection """
        # get tokens from server and make a dict of them.
        server_token = self.request_token()
        
        # now we need the user to authorize me to use their pump.io account
        server_token['verifier'] = self.get_access(server_token['token'])
        access = self.request_access(**server_token) 
    
    def get_access(self, token):
        """ this asks the user to let us use their account """

        print("To allow us to use your pump.io please follow the instructions at:")
        print("{protocol}://{server}/oauth/authorize?oauth_token={token}".format(
                protocol=self.protocol,
                server=self.server,
                token=token.decode("utf-8")
                ))
        
        code = raw_input("Verifier Code: ").lstrip(" ").rstrip(" ")
        return code

    def request_token(self):
        """ Gets a request token so that we can then ask the user for access to the accoutn """
        client = OAuth1(
                client_key=self.consumer.key,
                client_secret=self.consumer.secret,
                callback_uri="oob"
                )
        
        request = {"auth": client}
        response = self._requester(requests.post, "oauth/request_token", **request)
        data = parse_qs(response.content)
        data = {
            'token': data[self.PARAM_TOKEN][0],
            'token_secret': data[self.PARAM_TOKEN_SECRET][0]
            }

        return data

    def request_access(self, **auth_info):
        """ This is for when we've got the user's access value and we're asking the server for our access token """
        client = OAuth1(
                client_key=self.consumer.key,
                client_secret=self.consumer.secret,
                resource_owner_key=auth_info['token'],
                resource_owner_secret=auth_info['token_secret'],
                verifier=auth_info['verifier']
                )

        request = {"auth": client}
        response = self._requester(requests.post, "oauth/access_token", **request)        
        data = parse_qs(response.content)

        self.token = data[self.PARAM_TOKEN][0]
        self.token_secret = data[self.PARAM_TOKEN_SECRET][0]
        
        
