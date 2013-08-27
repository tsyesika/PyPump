##
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

from pypump.compatability import *
from pypump.exception import PyPumpException 
from pypump.models import AbstractModel

class ItemList(object):
    """ A collections list of items """

    previous_id = None

    def __init__(self, collection, count=None, start=None, stop=None):
        self.collection = collection
        self.start = start
        self.stop = stop
        self.cache = list()
        self.count = count
        self.itercounter = 0
        

    def __iter__(self):
        return self

    def next(self):
        if not self.cache:
            if not self.previous_id:
                response = self.collection._request(count=self.count, offset=self.start)
            elif "next" in self.collection.links:
                url = self.collection.links["next"]["href"]
                response = self.collection._request(count=self.count, next=url)
            else:
                response = None
            self.cache = response["items"] if response else None
        data = self.cache.pop(0) if self.cache else None

        if not data or (self.stop and self.itercounter >= self.stop):
            raise StopIteration

        if not self.collection.objectTypes:
            obj = getattr(self.collection._pump, data["objectType"].capitalize())
        else:
            obj = getattr(self.collection._pump, self.collection.objectTypes)
        obj = obj.unserialize(data)
        self.previous_id = obj.id
        self.itercounter +=1
        return obj

class Collection(AbstractModel):
    displayName = None
    totalItems = None
    objectTypes = None
    url = None
    links = dict()
    _parent = None
    _ENDPOINT = None

    @property
    def ENDPOINT(self):
        if self._ENDPOINT is None:
            raise NotImplemented("Definition of the ENDPOINT must be done by subclass")
        return self._ENDPOINT

    @property
    def items(self):
        return ItemList(self)

    def __init__(self, parent, endpoint=None, totalItems=None):
        self._parent = parent
        self.totalItems = totalItems if totalItems else self.totalItems
        self._pump = self._parent._pump
        if endpoint is not None:
            self._ENDPOINT = endpoint

    def __repr__(self):
        return "<Collection: {type}>".format(
            type = self.TYPE,
        )

    def __str__(self):
        # TODO: Do better
        if self._parent.TYPE == "person":
            return "{type} for {user}@{server}".format(
                type=self.TYPE,
                user=self._parent.username,
                server=self._parent.server
            )
        else:
            return "{name}".format(name=self.displayName if self.displayName else self.TYPE)

    def __iter__(self):
        return ItemList(self)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.__getslice__(key)
        item = ItemList(self, count=1, start=key, stop=1)
        try:
            return item.next()
        except StopIteration:
            raise IndexError

    def __getslice__(self, s, e=None):
        if type(s) is not slice:
            s = slice(s,e)

        return ItemList(self, start=s.start, stop=s.stop)
 
    def _request(self, offset=None, count=None, since=None, before=None, next=None):
        params = dict()

        if count is not None:
            params["count"] = count

        if offset is not None:
            params["offset"] = offset

        if since is not None:
            params["since"] = since
        elif before is not None:
            params["before"] = before

        if next is not None:
            url = next
        else:
            url = self.ENDPOINT

        print("_request: ", url, params)
        data = self._pump.request(url, params=params)
        self.unserialize(data)
        return data

    def unserialize(self, data):
        self.displayName = data["displayName"]
        self.totalItems = data["totalItems"]
        self.objectTypes = data["objectTypes"][0].capitalize() if "objectTypes" in data else None
        self.url = data["url"]
        self.links = data["links"]


class Followers(Collection):
    """ Person's followers """

    @property
    def ENDPOINT(self):
        return "{proto}://{server}/api/user/{username}/followers".format(
            proto=self._parent._pump.protocol,
            server=self._parent.server,
            username=self._parent.username
        )

class Following(Collection):
    """ People followed by Person """

    @property
    def ENDPOINT(self):
        return "{proto}://{server}/api/user/{username}/following".format(
            proto=self._parent._pump.protocol,
            server=self._parent.server,
            username=self._parent.username
        )

class Favorites(Collection):
    """ Person's favorites """

    @property
    def ENDPOINT(self):
        return "{proto}://{server}/api/user/{username}/favorites".format(
            proto=self._parent._pump.protocol,
            server=self._parent.server,
            username=self._parent.username
        )

class Inbox(Collection):
    """ Person's inbox """

    _ENDPOINT = "{proto}://{server}/api/user/{username}/inbox"

    def __init__(self, parent, endpoint=None):
        self._parent = parent
        self._pump = self._parent._pump
        if endpoint is not None:
            self._ENDPOINT = endpoint


    @property
    def ENDPOINT(self):
        return self._ENDPOINT.format(
            proto=self._parent._pump.protocol,
            server=self._parent.server,
            username=self._parent.username
        )

    @property
    def direct(self):
        endpoint = self.ENDPOINT
        if not endpoint.endswith("/"):
            endpoint += "/"
        endpoint += "direct"
        return self.__class__(parent=self._parent, endpoint=endpoint)

    @property
    def major(self):
        endpoint = self.ENDPOINT
        if not endpoint.endswith("/"):
            endpoint += "/"
        endpoint += "major"
        return self.__class__(parent=self._parent, endpoint=endpoint)

    @property
    def minor(self):
        endpoint = self.ENDPOINT
        if not endpoint.endswith("/"):
            endpoint += "/"
        endpoint += "minor"
        return self.__class__(parent=self._parent, endpoint=endpoint)


class Outbox(Collection):
    """ Person's outbox """

    _ENDPOINT = "{proto}://{server}/api/user/{username}/feed"

    def __init__(self, parent, endpoint=None):
        self._parent = parent
        self._pump = self._parent._pump
        if endpoint is not None:
            self._ENDPOINT = endpoint


    @property
    def ENDPOINT(self):
        return self._ENDPOINT.format(
            proto=self._parent._pump.protocol,
            server=self._parent.server,
            username=self._parent.username
        )

    @property
    def major(self):
        endpoint = self.ENDPOINT
        if not endpoint.endswith("/"):
            endpoint += "/"
        endpoint += "major"
        return self.__class__(parent=self._parent, endpoint=endpoint)

    @property
    def minor(self):
        endpoint = self.ENDPOINT
        if not endpoint.endswith("/"):
            endpoint += "/"
        endpoint += "minor"
        return self.__class__(parent=self._parent, endpoint=endpoint)

