# -*- coding: utf-8 -*-

##
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

from __future__ import absolute_import

import json
import logging

import requests
import six

from six.moves.urllib import parse
from six.moves import input
from requests_oauthlib import OAuth1

import pypump.openid as openid
from pypump.exception import PyPumpException

# load models
from pypump.models.note import Note
from pypump.models.comment import Comment
from pypump.models.person import Person
from pypump.models.image import Image
from pypump.models.location import Location
from pypump.models.activity import Activity
from pypump.models.collection import Collection, Public

_log = logging.getLogger(__name__)

class PyPump(object):
    """
        Main class to interface with PyPump.

        This class keeps everything together and is responsible
        for making requests to the server on it's own behalf and
        on the bahalf of the other clients as well as handling the
        OAuth requests.
    """

    PARAM_VERIFER = six.b("oauth_verifier")
    PARAM_TOKEN = six.b("oauth_token")
    PARAM_TOKEN_SECRET = six.b("oauth_token_secret")

    URL_CLIENT_REGISTRATION = "/api/client/register"

    loader = None
    protocol = "https"
    client = None
    _server_cache = dict()

    def __init__(self, server, key=None, secret=None,
                client_name=None, client_type="native", token=None,
                token_secret=None, verifier_callback=None,
                callback_uri="oob", loglevel="error", debug=False):
        """
            This is the main pump instance, this handles the oauth,
            this also holds the models.

            Don't forget if you want to use https ensure the secure flag is True
        """

        self.debug = debug

        # First, we need to setup the logger
        logginglevel = getattr(logging, loglevel.upper(), None)
        if logginglevel is None:
            raise PyPumpException("Unknown loglevel {0!r}".format(loglevel))
        _log.setLevel(logginglevel)


        openid.OpenID.pypump = self # pypump uses PyPump.requester.
        self.verifier_callback = verifier_callback
        self.client_name = client_name
        self.client_type = client_type
        self.callback_uri = callback_uri

        if "@" in server:
            # it's a web fingerprint!
            self.nickname, self.server = server.split("@")
        else:
            self.server = server
            self.nickname = None

        # Fix #24 by checking
        if (key is None or secret is None) and (token or token_secret):
            error = "Must provide key and secret with token/token_seceret"
            raise Exception(error)

        self.populate_models()

        self._add_consumer(self.server, key, secret)

        if not (token and token_secret):
            # we need to make a new oauth request
            self.oauth_request() # this does NOT return access tokens but None
        else:
            self.token = token
            self.token_secret = token_secret

        if not self.debug:
            self.me = self.Person("{username}@{server}".format(
                username = self.nickname,
                server = self.server)
            )

    def populate_models(self):
        def factory(pypump, model):
            return lambda *args, **kwargs: model(
                pypump=kwargs.pop("pypump", pypump),
                *args,
                **kwargs)

        self.Note = factory(self, Note)
        self.Collection = factory(self, Collection)
        self.Comment = factory(self, Comment)
        self.Image = factory(self, Image)
        self.Person = factory(self, Person)
        self.Location = factory(self, Location)
        self.Public = factory(self, Public)
        self.Activity = factory(self, Activity)

    ##
    # getters to expose some data which might be useful
    ##
    def get_registration(self):
        """ Returns client credentials post-registration """
        return (self._server_cache[self.server].key,
                self._server_cache[self.server].secret,
                self._server_cache[self.server].expirey)

    def get_token(self):
        """ Returns OAuth token and secret post-handshake """
        return (self.token, self.token_secret)

    def set_nickname(self, nickname):
        """ This sets the nickname being used """
        if nickname:
            self.nickname = str(nickname)
        else:
            # they didn't enter a nickname?
            raise Exception("Nickname can't be of length 0")

    ##
    # server
    ##
    def build_url(self, endpoint):
        """ Returns a fully qualified URL """
        server = None
        if "://" in endpoint:
            #looks like an url, let's break it down
            server, endpoint = self.deconstruct_url(endpoint)

        endpoint = endpoint.lstrip("/")
        url = "{proto}://{server}/{endpoint}".format(
                proto=self.protocol,
                server=self.server if server is None else server,
                endpoint=endpoint
                )
        return url

    def deconstruct_url(self, url):
        """ Breaks down URL and returns server and endpoint """
        url = url.split("://", 1)[-1]
        server, endpoint = url.split("/", 1)
        return (server, endpoint)

    def _add_consumer(self, url, key=None, secret=None):
        """ Creates Consumer object with key and secret for server
        and adds it to _server_cache if it doesnt already exist """

        if "://" in url:
            server, endpoint = self.deconstruct_url(url)
        else:
            server = url

        if server not in self._server_cache:
            if not (key and secret):
                oid = openid.OpenID(
                    server=server,
                    client_name=self.client_name,
                    application_type=self.client_type
                )
                consumer = oid.register_client()
            else:
                consumer = openid.Consumer()
                consumer.key = key
                consumer.secret = secret
            self._server_cache[server] = consumer

    def request(self, endpoint, method="GET", data="",
                raw=False, params=None, attempts=3, client=None,
                headers=None):
        """ Make request to endpoint with OAuth
        method = GET (default), POST or PUT
        attempts = this is how many times it'll try re-attempting
        """

        # check client has been setup
        if client is None:
            client = self.setup_oauth_client(endpoint)

        params = {} if params is None else params

        if data and isinstance(data, dict):
            data = json.dumps(data)

        if not raw:
            url = self.build_url(endpoint)
        else:
            url = endpoint

        headers = headers or {"Content-Type": "application/json"}

        lastresponse = ""
        for attempt in range(attempts):
            if method == "POST":
                request = {
                        "auth": client,
                        "headers": headers,
                        "params": params,
                        "data": data,
                        }
                response = self._requester(
                    requests.post,
                    endpoint,
                    raw,
                    **request
                )

            elif method == "GET":
                request = {
                        "params": params,
                        "auth": client,
                        "headers": headers,
                        }

                response = self._requester(
                    requests.get,
                    endpoint,
                    raw,
                    **request
                )

            elif method == "DELETE":
                request = {
                        "params": params,
                        "auth": client,
                        "headers": headers,
                        }

                response = self._requester(
                    requests.delete,
                    endpoint,
                    raw,
                    **request
                )

            self._lastresponse = response # for debug purposes
            if response.status_code == 200:
                # huray!
                return response.json()

            if response.status_code == 400:
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
                    error = "400 - Bad request."
                raise PyPumpException(error)

        error = "Failed to make request to {0}".format(url)
        raise PyPumpException(error)
    def _requester(self, fnc, endpoint, raw=False, **kwargs):
        if not raw:
            url = self.build_url(endpoint)
        else:
            url = endpoint

        try:
            response = fnc(url, **kwargs)
            return response
        except requests.exceptions.ConnectionError:
            if self.protocol == "http" or raw:
                raise # shoot this seems real.
            else:
                self.set_http()
                url = self.build_url(endpoint)
                self.set_https()
                raw = True
                return self._requester(fnc, url, raw, **kwargs)

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
        self.__server_tokens = self.request_token()

        self.token = self.__server_tokens["token"]
        self.token_secret = self.__server_tokens["token_secret"]

        url = self.build_url("oauth/authorize?oauth_token={token}".format(
                protocol=self.protocol,
                server=self.server,
                token=self.token.decode("utf-8")
                ))

        # now we need the user to authorize me to use their pump.io account
        if self.verifier_callback is None:
            verifier = self.get_access(url)
            self.verifier(verifier)
        else:
            self.verifier_callback(url)

    def verifier(self, verifier):
        """ Called once verifier has been retrived """
        self.__server_tokens["verifier"] = verifier
        self.request_access(**self.__server_tokens)

    def setup_oauth_client(self, url=None):
        """ Sets up client for requests to pump """
        if url and "://" in url:
            server, endpoint = self.deconstruct_url(url)
        else:
            server = self.server

        if server not in self._server_cache:
            self._add_consumer(server)

        if server == self.server:
            self.client = OAuth1(
                    client_key=self._server_cache[self.server].key,
                    client_secret=self._server_cache[self.server].secret,
                    resource_owner_key=self.token,
                    resource_owner_secret=self.token_secret
                    )
            return self.client
        else:
            return OAuth1(
                client_key=six.u(self._server_cache[server].key),
                client_secret=six.u(self._server_cache[server].secret),
            )

    def get_access(self, url):
        """ this asks the user to let us use their account """

        six.print_("To authenticate, please open and follow the instructions:")
        six.print_(url)

        code = input("Verifier Code: ").lstrip(" ").rstrip(" ")
        return code

    def request_token(self):
        """ Gets OAuth request token """
        client = OAuth1(
                client_key=self._server_cache[self.server].key,
                client_secret=self._server_cache[self.server].secret,
                callback_uri=self.callback_uri
                )

        request = {"auth": client}
        response = self._requester(
            requests.post,
            "oauth/request_token",
            **request
        )

        data = parse.parse_qs(response.content)
        data = {
            'token': data[self.PARAM_TOKEN][0],
            'token_secret': data[self.PARAM_TOKEN_SECRET][0]
            }

        return data

    def request_access(self, **auth_info):
        """ Get OAuth access token so we can make requests """
        client = OAuth1(
                client_key=self._server_cache[self.server].key,
                client_secret=self._server_cache[self.server].secret,
                resource_owner_key=auth_info['token'],
                resource_owner_secret=auth_info['token_secret'],
                verifier=auth_info['verifier']
                )

        request = {"auth": client}
        response = self._requester(
            requests.post,
            "oauth/access_token",
            **request
        )

        data = parse.parse_qs(response.content)

        self.token = data[self.PARAM_TOKEN][0]
        self.token_secret = data[self.PARAM_TOKEN_SECRET][0]
        self.__server_tokens = None # clean up code.

class WebPump(PyPump):
    """
        This is a PyPump class which is aimed at mainly web developers.
        Allowing you to avoid the callbacks making the oauth portion of
        PyPump instanciation blocking.

        After initialisation you will be able to do `PyPump.verifier_url`
        allowing you to get the url to direct your user to. That method
        will return None if the oauth handshake was successful and no
        verifier callback needs to be done.

        Once you have the verifier instanciate this class again and
        call the verifier method alike what you do using the PyPump class
    """

    url = None

    def __init__(self, *args, **kwargs):
        """
            This is exactly the same as PyPump.__init__ apart from
            verifier_callback is no longer an option for kwargs and
            if specified will be ignored.
        """
        kwargs["verifier_callback"] = self._callback_verifier
        super(WebPump, self).__init__(*args, **kwargs)

    def _callback_verifier(self, url):
        """ This is used to catch the url and store it at `self.url` """
        self.url = url
