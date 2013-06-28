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

import json
import requests
from compatability import *

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

    ENDPOINT = "{proto}://{server}/api/client/register"

    server = None
    protocol = "https" 
    request = None
    type = None
    logo_url = None

    consumer = None


    def __init__(self, protocol, server, client_name, application_type, logo_url=None):
        # we don't want the webfinger just the server
        if "@" in server:
            self.server = server.split("@", 1)[1]
        else:
            self.server = server

        if type(protocol) is bool:
            self.protocol = "https" if protocol else "http"
        else:
            self.protocol = protocol

        self.name = client_name = client_name
        self.type = application_type
        self.logo_url = self.logo_url if logo_url is not None else logo_url

    def register_client(self):
        """ Sends a client registration request """
        data = {
            "type":"client_associate", 
            "application_name":self.name,
            "application_type":self.type,
        }

        if self.logo_url:
            data["logo_url"] = self.logo_url

        data = json.dumps(data)

        if self.server is None:
            raise OpenIDException("Server must be set")

        endpoint = self.ENDPOINT.format(
                proto=self.protocol,
                server=self.server
                )

        request = requests.post(endpoint, headers={'Content-Type': 'application/json'}, data=data)
        try:
            server_data = request.json()
        except ValueError:
            raise OpenIDException(request.content)

        if "error" in server_data:
            raise OpenIDException(server_data["error"])

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
