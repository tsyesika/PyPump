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

import six
import requests

_log = logging.getLogger(__name__)

class OpenIDException(Exception):
    pass

class Consumer(object):
    """
        Container for holding the client registration details
    """
    key = None
    secret = None
    expirey = 0 # never

    def __repr__(self):
        return "<Consumer %s>" % self.key

    def __str__(self):
        return self.__repr__()

class OpenID(object):

    ENDPOINT = "api/client/register"

    pypump = None
    server = None
    request = None
    logo_url = None
    contacts = None
    redirect_uri = None
    type = None

    consumer = None


    def __init__(self, server, application_type, client_name=None,
                 contacts=None, redirect_uri=None, logo_url=None):

        # we don't want the webfinger just the server
        if "@" in server:
            self.server = server.split("@", 1)[1]
        else:
            self.server = server

        self.name = client_name
        self.type = application_type
        self.logo_url = logo_url or self.logo_url
        self.contacts = contacts or list()
        self.redirect_uri = redirect_uri or list()

    def register_client(self):
        """ Sends a client registration request """
        data = {
            "type":"client_associate", 
            "application_type":self.type,
        }

        # Add optional params
        if self.name is not None:
            data["application_name"] = self.name

        if self.logo_url is not None:
            data["logo_url"] = self.logo_url

        if self.contacts:
            # space seporated list
            data["contacts"] = " ".join(self.contacts)

        if self.redirect_uri:
            data["redirect_uri"] = " ".join(self.redirect_uri)

        # Convert to JSON  and send
        data = json.dumps(data)

        if self.server is None:
            raise OpenIDException("Server must be set")

        request = {
                "headers": {"Content-Type": "application/json"},
                "data": data
                }

        if self.server == self.pypump.server:
            response = self.pypump._requester(requests.post, self.ENDPOINT, **request)
        else:
            url = "{proto}://{server}/{endpoint}".format(
                proto=self.pypump.protocol,
                server = self.server,
                endpoint = self.ENDPOINT
            )
            response = self.pypump._requester(requests.post, url, **request)
        
        try:
            server_data = response.json()
        except ValueError:
            raise OpenIDException(response.content)

        if "error" in server_data:
            raise OpenIDException(server_data["error"])

        _log.debug("Client registration recieved: {id} {secret} {expire}".format(
                id=server_data["client_id"],
                secret=server_data["client_secret"],
                expire=server_data["expires_at"]
                ))

        consumer = Consumer()
        consumer.key = server_data["client_id"]
        consumer.secret = server_data["client_secret"]
        consumer.expirey = server_data["expires_at"]

        self.consumer = consumer

        return consumer

    def __repr__(self):
        return "<OpenID %s>" % self.server

    def __str__(self):
        return self.__repr__()
