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

from pypump.store import JSONStore
from pypump.client import Client
from pypump.exception import PyPumpException

# load models
from pypump.models.note import Note
from pypump.models.comment import Comment
from pypump.models.person import Person
from pypump.models.image import Image
from pypump.models.place import Place

from pypump.models.collection import Collection, Public

_log = logging.getLogger(__name__)


class PyPump(object):
    """Main class to interface with PyPump.

    This class keeps everything together and is responsible for making
    requests to the server on it's own behalf and on the behalf of the
    other clients as well as handling the OAuth requests.

    :param client: an instance of :class:`Client <pypump.Client>`.
    :param verifier_callback: If this is our first time registering the
      client, this function will be called with a single argument, the
      url one can post to for completing verification.
    :param store: this is the :class:`pypump.Store` instance to save
      any data persistantly.
    :param callback: the URI that is used for redirecting a user
      after they authenticate this client... assuming this is
      happening over the web.  If not, the callback is "oob", or "out
      of band".
    :param verify_requests: If this is set to False PyPump won't check SSL/TLS
      certificates.
    :param retries: number of times to retry if a request fails.
    :param timeout: how long to give on a timeout for an http request, in
      seconds.
    """

    PARAM_VERIFER = six.b("oauth_verifier")
    PARAM_TOKEN = six.b("oauth_token")
    PARAM_TOKEN_SECRET = six.b("oauth_token_secret")

    URL_CLIENT_REGISTRATION = "/api/client/register"

    store_class = JSONStore

    def __init__(self,
                 client,
                 verifier_callback,
                 store=None,
                 callback="oob",
                 verify_requests=True,
                 retries=0,
                 timeout=30):

        self._me = None
        self.protocol = "https"

        self.retries = retries
        self.timeout = timeout

        self._server_cache = {}
        self._server_tokens = {}
        self.verify_requests = verify_requests
        self.callback = callback
        self.client = client
        self.verifier_callback = verifier_callback
        self._server_cache[self.client.server] = self.client

        # Setup store object
        if store is None:
            self.store = self.create_store()
        else:
            self.store = store

        # Setup variables for client
        self.client.set_pump(self)
        if "client-key" in self.store:
            self.client.key = self.store["client-key"]

        if "client-secret" in self.store:
            self.client.secret = self.store["client-secret"]

        if "client-expirey" in self.store:
            self.client.expirey = self.store["client-expirey"]

        if not self.client.key:
            self.client.register()
            # Save the info back to the store

            self.store["client-key"] = self.client.key
            self.store["client-secret"] = self.client.secret
            self.store["client-expirey"] = self.client.expirey

        self._populate_models()

        if "oauth-request-token" not in self.store and "oauth-access-token" not in self.store:
            # we Need to make a new oauth request
            self.oauth_request()

    @property
    def me(self):
        """ Returns :class:`Person <pypump.models.person.Person>` instance of
        the logged in user.

        Example:
            >>> pump.me
            <Person: bob@example.org>
        """

        if self._me is not None:
            return self._me

        self._me = self.Person("{username}@{server}".format(
            username=self.client.nickname,
            server=self.client.server,
        ))
        return self._me

    def create_store(self):
        """ Creates store object """
        if self.store_class is not None:
            return self.store_class.load(self.client.webfinger, self)

        raise NotImplementedError("You need to specify PyPump.store_class or override PyPump.create_store method.")

    def _populate_models(self):
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

    def _build_url(self, endpoint):
        """ Returns a fully qualified URL """
        server = None
        if "://" in endpoint:
            # looks like an url, let's break it down
            server, endpoint = self._deconstruct_url(endpoint)

        endpoint = endpoint.lstrip("/")
        url = "{proto}://{server}/{endpoint}".format(
            proto=self.protocol,
            server=self.client.server if server is None else server,
            endpoint=endpoint,
        )
        return url

    def _deconstruct_url(self, url):
        """ Breaks down URL and returns server and endpoint """
        url = url.split("://", 1)[-1]
        server, endpoint = url.split("/", 1)
        return (server, endpoint)

    def _add_client(self, url, key=None, secret=None):
        """ Creates Client object with key and secret for server
        and adds it to _server_cache if it doesnt already exist """

        if "://" in url:
            server, endpoint = self._deconstruct_url(url)
        else:
            server = url

        if server not in self._server_cache:
            if not (key and secret):
                client = Client(
                    webfinger=self.client.webfinger,
                    name=self.client.name,
                    type=self.client.type,
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
                raw=False, params=None, retries=None, client=None,
                headers=None, timeout=None, **kwargs):
        """ Make request to endpoint with OAuth.
        Returns dictionary with response data.

        :param endpoint: endpoint path, or a fully qualified URL if raw=True.
        :param method: GET (default), POST or DELETE.
        :param data: data to send in the request body.
        :param raw: use endpoint as entered without trying to modify it.
        :param params: dictionary of parameters to send in the query string.
        :param retries: number of times to retry if a request fails.
        :param client: OAuth client data, if False do request without OAuth.
        :param headers: dictionary of HTTP headers.
        :param timeout: the timeout for a request, in seconds.

        Example:
            >>> pump.request('https://e14n.com/api/user/evan/profile', raw=True)
            {u'displayName': u'Evan Prodromou',
             u'favorites': {u'totalItems': 7227,
              u'url': u'https://e14n.com/api/user/evan/favorites'},
             u'id': u'acct:evan@e14n.com',
             u'image': {u'height': 96,
              u'url': u'https://e14n.com/uploads/evan/2014/9/24/knyf1g_thumb.jpg',
              u'width': 96},
             u'liked': False,
             u'location': {u'displayName': u'Montreal, Quebec, Canada',
              u'objectType': u'place'},
             u'objectType': u'person',
             u'preferredUsername': u'evan',
             u'published': u'2013-02-20T15:34:52Z',
             u'summary': u'I wanna make it with you. http://payb.tc/evanp',
             u'updated': u'2014-09-24T02:38:32Z',
             u'url': u'https://e14n.com/evan'}
        """

        retries = self.retries if retries is None else retries
        timeout = self.timeout if timeout is None else timeout

        # check client has been setup
        if client is None:
            client = self.setup_oauth_client(endpoint)
        elif client is False:
            client = None

        params = {} if params is None else params

        if data and isinstance(data, dict):
            data = json.dumps(data)

        if not raw:
            url = self._build_url(endpoint)
        else:
            url = endpoint

        headers = headers or {"Content-Type": "application/json"}
        fnc = requests.get
        request = {
            "auth": client,
            "headers": headers,
            "params": params,
            "timeout": timeout,
        }
        request.update(kwargs)

        if method == "POST":
            fnc=requests.post
            request.update({"data": data})

        elif method == "PUT":
            fnc=requests.put
            request.update({"data": data})

        elif method == "GET":
            fnc=requests.get

        elif method == "DELETE":
            fnc=requests.delete,
                
        for attempt in range(1 + retries):
            response = self._requester(
                fnc=fnc,
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
                        raise IndexError  # yesss i know.
                except IndexError:
                    error = "400 - Bad request."
                raise PyPumpException(error)

            if response.ok:
                return response

        error = "Request Failed to {url} (response: {data} | status: {status})"
        error = error.format(
            url=url,
            data=response.content,
            status=response.status_code
        )

        raise PyPumpException(error)

    def _requester(self, fnc, endpoint, raw=False, **kwargs):
        if not raw:
            url = self._build_url(endpoint)
        else:
            url = endpoint

        kwargs["verify"] = self.verify_requests

        try:
            response = fnc(url, **kwargs)
            return response
        except requests.exceptions.ConnectionError:
            if self.protocol == "http" or raw:
                raise  # shoot this seems real.
            else:
                self.set_http()
                url = self._build_url(endpoint)
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

        self.store["oauth-request-token"] = self._server_tokens["token"]
        self.store["oauth-request-secret"] = self._server_tokens["token_secret"]

        # now we need the user to authorize me to use their pump.io account
        result = self.verifier_callback(self.construct_oauth_url())
        if result is not None:
            self.verifier(result)

    def construct_oauth_url(self):
        """ Constructs verifier OAuth URL """
        response = requests.head("http://{0}".format(self.client.server))
        if response.is_redirect:
            server = response.headers['location']
        else:
            server = response.url

        path = "oauth/authorize?oauth_token={token}".format(
            token=self.store["oauth-request-token"]
        )
        return "{server}{path}".format(
            server=server,
            path=path
        )

    def verifier(self, verifier):
        """ Called once verifier has been retrieved. """
        self.request_access(verifier)

    def setup_oauth_client(self, url=None):
        """ Sets up client for requests to pump """
        if url and "://" in url:
            server, endpoint = self._deconstruct_url(url)
        else:
            server = self.client.server

        if server not in self._server_cache:
            self._add_client(server)

        if server == self.client.server:
            self.oauth = OAuth1(
                client_key=self.store["client-key"],
                client_secret=self.store["client-secret"],
                resource_owner_key=self.store["oauth-access-token"],
                resource_owner_secret=self.store["oauth-access-secret"],
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
            callback_uri=self.callback,
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

    def request_access(self, verifier):
        """ Get OAuth access token so we can make requests """
        client = OAuth1(
            client_key=self._server_cache[self.client.server].key,
            client_secret=self._server_cache[self.client.server].secret,
            resource_owner_key=self.store["oauth-request-token"],
            resource_owner_secret=self.store["oauth-request-secret"],
            verifier=verifier,
        )

        request = {"auth": client}
        response = self._requester(
            requests.post,
            "oauth/access_token",
            **request
        )

        data = parse.parse_qs(response.content)

        self.store["oauth-access-token"] = data[self.PARAM_TOKEN][0]
        self.store["oauth-access-secret"] = data[self.PARAM_TOKEN_SECRET][0]
        self._server_tokens = {}  # clean up code.


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
        self.url = self.construct_oauth_url()

    def _callback_verifier(self, url):
        """ This is used to catch the url and store it at `self.url` """
        self.url = url

    @property
    def logged_in(self):
        """ Return boolean if is logged in """
        if "oauth-access-token" not in self.store:
            return False

        # if it redirects to the profile it'll raise an exception as
        # it doesn't sign the redirection request.
        response = self.request("/api/whoami", allow_redirects=False)

        # It should response with a redirect to our profile if it's logged in
        if response.status_code != 302:
            return False

        # the location should be the profile we have
        if response.headers["location"] != self.me.links["self"]:
            return False

        return True
