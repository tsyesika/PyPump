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
import urllib.request

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

    consumer = None


    def __init__(self, protocol, server, client_name, application_type):
        self.request = urllib.request.build_opener()

        self.server = server

        if type(protocol) is bool:
            self.protocol = "https" if protocol else "http"
        else:
            self.protocol = protocol

        self.name = client_name = client_name
        self.type = application_type

    def register_client(self):
        """ Sends a client registration request """
        data = [
            "client_name={name}".format(name=self.name),
            "type=client_associate",
            "application_type={type}".format(type=self.type),
        ]

        data = "&".join(data)

        if self.server is None:
            raise OpenIDException("Server must be set")

        endpoint = self.ENDPOINT.format(
                proto=self.protocol,
                server=self.server
                )

        request = urllib.request.Request(endpoint)
        request.data = data.encode()
        request = self.request.open(request)
        
        server_data = request.read().decode("utf-8")
        server_data = json.loads(server_data)

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
