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
from requests_oauthlib import OAuth1

from pypump.client import Client
from pypump.exception import PyPumpException

# load models
from pypump.models.note import Note
from pypump.models.comment import Comment
from pypump.models.person import Person
from pypump.models.image import Image
from pypump.models.place import Place
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
    verify_requests = True
    client = None
    _server_cache = None
    _server_tokens = None # this hold OAuth tokens
    _me = None

    def __init__(self, client, verifier_callback, token=None, secret=None,
                 callback="oob", verify=True):
        """
            This is the main pump instance, this handles the oauth,
            this also holds the models.
        """

        self._server_cache = {}
        self._server_tokens = {}
        self.verify_requests = verify
        self.callback = callback
        self.client = client
        self.verifier_callback = verifier_callback
        self._server_cache[self.client.server] = self.client

        self.client.set_pump(self)
        if not self.client.key:
            self.client.register()

        self.populate_models()

        if not (token and secret):
            # we need to make a new oauth request
            self.oauth_request()
        else:
            self.token = token
            self.secret = secret

    @property
    def me(self):
        if self._me is not None:
            return self._me

        self._me = self.Person("{username}@{server}".format(
            username = self.client.nickname,
            server = self.client.server
        ))
        return self._me

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
        self.Place = factory(self, Place)
        self.Public = Public()
        self.Activity = factory(self, Activity)

    ##
    # getters to expose some data which might be useful
    ##
    def get_registration(self):
        """ Returns client credentials post-registration """
        return (self.client.key, self.client.secret, self.client.expirey)

    def get_token(self):
        """ Returns OAuth token and secret post-handshake """
        return (self.token, self.secret)

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
                server=self.client.server if server is None else server,
                endpoint=endpoint
                )
        return url

    def deconstruct_url(self, url):
        """ Breaks down URL and returns server and endpoint """
        url = url.split("://", 1)[-1]
        server, endpoint = url.split("/", 1)
        return (server, endpoint)

    def _add_client(self, url, key=None, secret=None):
        """ Creates Client object with key and secret for server
        and adds it to _server_cache if it doesnt already exist """

        if "://" in url:
            server, endpoint = self.deconstruct_url(url)
        else:
            server = url

        if server not in self._server_cache:
            if not (key and secret):
                client = Client(
                    webfinger=self.client.webfinger,
                    name=self.client.name,
                    type=self.client.type
                )
                client.set_pump(self)
                client.register(server)
            else:
                client = Client(
                        webfinger=self.client.webfinger,
                        key=key,
                        secret=secret,
                        type=self.client.type,
                        name=self.client.name,
                        )
                client.set_pump(self)

            self._server_cache[server] = client

    def request(self, endpoint, method="GET", data="",
                raw=False, params=None, attempts=1, client=None,
                headers=None, timeout=30):
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

        for attempt in range(attempts):
            if method == "POST":
                request = {
                        "auth": client,
                        "headers": headers,
                        "params": params,
                        "data": data,
                        "timeout": timeout,
                        }
                
                response = self._requester(
                    fnc=requests.post,
                    endpoint=endpoint,
                    raw=raw,
                    **request
                )

            elif method == "GET":
                request = {
                        "params": params,
                        "auth": client,
                        "headers": headers,
                        "timeout": timeout,
                        }

                response = self._requester(
                    fnc=requests.get,
                    endpoint=endpoint,
                    raw=raw,
                    **request
                )

            elif method == "DELETE":
                request = {
                        "params": params,
                        "auth": client,
                        "headers": headers,
                        "timeout": timeout,
                        }

                response = self._requester(
                    fnc=requests.delete,
                    endpoint=endpoint,
                    raw=raw,
                    **request
                )

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


        error = "Request Failed to {url} (response: {data} | status: {status})"
        error = error.format(
                url=url,
                data=response.content,
                status=response.status_code
                )

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
        self._server_tokens = self.request_token()

        self.token = self._server_tokens["token"]
        self.secret = self._server_tokens["token_secret"]

        url = self.build_url("oauth/authorize?oauth_token={token}".format(
                protocol=self.protocol,
                server=self.client.server,
                token=self.token.decode("utf-8")
                ))

        # now we need the user to authorize me to use their pump.io account
        result = self.verifier_callback(url)
        if result is not None:
            self.verifier(result)

    def verifier(self, verifier):
        """ Called once verifier has been retrived """
        self._server_tokens["verifier"] = verifier
        self.request_access(**self._server_tokens)

    def setup_oauth_client(self, url=None):
        """ Sets up client for requests to pump """
        if url and "://" in url:
            server, endpoint = self.deconstruct_url(url)
        else:
            server = self.client.server

        if server not in self._server_cache:
            self._add_client(server)

        if server == self.client.server:
            self.oauth = OAuth1(
                    client_key=self._server_cache[self.client.server].key,
                    client_secret=self._server_cache[self.client.server].secret,
                    resource_owner_key=self.token,
                    resource_owner_secret=self.secret
                    )
            return self.oauth
        else:
            return OAuth1(
                client_key=self._server_cache[server].key,
                client_secret=self._server_cache[server].secret,
            )

    def request_token(self):
        """ Gets OAuth request token """
        client = OAuth1(
                client_key=self._server_cache[self.client.server].key,
                client_secret=self._server_cache[self.client.server].secret,
                callback_uri=self.callback
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
                client_key=self._server_cache[self.client.server].key,
                client_secret=self._server_cache[self.client.server].secret,
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
        self.secret = data[self.PARAM_TOKEN_SECRET][0]
        self._server_tokens = {} # clean up code.

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
