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

@implement_to_string
class Feed(AbstractModel):

    _feed = None
    _count = None
    _offset = None
    actor = None
    author = actor

    _ENDPOINT = None
    @property
    def ENDPOINT(self):
        if self._ENDPOINT is None:
            raise NotImplemented("Definition of the ENDPOINT must be done by subclass")
        return self._ENDPOINT

    @property
    def major(self):
        endpoint = self.ENDPOINT
        if not endpoint.endswith("/"):
            endpoint += "/"
        endpoint += "major"
        return self.__class__(username=self.actor, endpoint=endpoint)

    @property
    def minor(self):
        endpoint = self.ENDPOINT
        if not endpoint.endswith("/"):
            endpoint += "/"
        endpoint += "minor"
        return self.__class__(username=self.actor, endpoint=endpoint)

    def __init__(self, username=None, endpoint=None):
        if endpoint is not None:
            self._ENDPOINT = endpoint
        
        self._feed = list() if self._feed is None else self._feed
        
        if isinstance(username, self._pump.Person):
            self.actor = username
            return

        if username is None:
            return

        self.actor = self._pump.Person(username)        

    def __getitem__(self, key):
        """ Adds Feed[<feed>] """
        if isinstance(key, slice):
            return self.__getslice__(key)
        count = 1
        offset = key
        data = self.__request(offset=offset, count=count)
        self.unserialize(data, obj=self) 
        return self._feed[0]

    def __getslice__(self, s, e=None):
        """ Grab multiple items from feed """
        if type(s) is not slice:
            s = slice(s,e)

        if s.start and s.stop:
            count = s.stop - s.start
            offset = s.start
        elif s.stop:
            count = s.stop
            offset = None
        elif s.start:
            offset = s.start
            count = None

        data = self.__request(offset=offset, count=count)
        obj = self.unserialize(data, obj=self)

        if s.step:
            return obj._feed[::s.step]
        else:
            return obj._feed

    def __iter__(self):
        """ Produces an iterator """
        if self._feed:
            return self._feed.__iter__()
        
        data = self.__request()
        return self.unserialize(data, obj=self).__iter__()

    def __repr__(self):
        if self.author:
            return "<{actor} {type} of {num} items>".format(
                    actor=self.actor,
                    type=self.TYPE,
                    num=len(self)
                    )
        else:
            return "<{type} of {num} items>".format(type=self.TYPE, num=len(self))

    def __str__(self):
        return str(self.__repr__())

    def __len__(self):
        """ Gives amount of items in the feed """
        return len(self._feed)

    def __request(self, offset=None, count=None):
        """ Makes a request """
        param = {}

        if count:
            param["count"] = count

        if offset:
            param["offset"] = offset

        if self.actor is None:
            # oh dear, we gotta raise an error
            raise PyPumpException("No actor defined on {feed}".format(feed=self))

        data = self._pump.request(self.ENDPOINT, params=param)

        return data

    def clear(self):
        """ Clears an feed """
        self._feed = []

    @classmethod
    def unserialize(cls, data, obj=None, user=None):
        """ Produces self._feed from JSON data """
        if obj is None:
            self = cls()
        else:
            self = obj

        user = self.actor if user is None else user

        self.actor = user

        if type(data) == list:
            items = data
        elif type(data) == dict:
            items = data["items"]
        else:
            raise Exception("Unknown type: {type} ('{data}')".format(
                    type=type(data),
                    data=data
                    ))

        for v in items:
            # do we know about it?
            obj_type = v["object"]["objectType"].capitalize()

            # todo: make less hacky
            try:
                obj = getattr(self._pump, obj_type)
            except AttributeError:
                continue # what is this stange type of which you are?
            
            try:
                real_obj = obj.unserialize(v)
                if real_obj is not None:
                    self._feed.append(real_obj)
            except TypeError:
                # caused by missing out the self param, will fix tomorrow
                pass

        return self 
