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

from models import AbstractModel

class Inbox(AbstractModel):

    TYPE = "inbox"
    ENDPOINT = "api/user/%s/inbox"

    _inbox = []
    _count = None
    _offset = None
    author = None

    def __getitem__(self, key):
        """ Adds Inbox[<inbox>] """
        if isinstance(key, slice):
            return self.__getslice__(key)
        count = 1
        offset = key
        data = self.__request(offset=offset, count=count)
        return self.unserialize(data, obj=self) 

    def __getslice__(self, s):
        """ allows for a limit """
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
            return obj._inbox[::s.step]
        else:
            return obj._inbox

    def __iter__(self):
        """ Produces an iterator """
        if self._inbox:
            return self._inbox.__iter__()
        
        data = self.__request()
        return self.unseralize(data, obj=self).__iter__()

    def __len__(self):
        """ Gives amount of items in the inbox """
        return len(self._inbox)

    def __request(self, offset=None, count=None):
        """ Makes a request """
        param = ""

        if count:
            param += "count=%s" % count

        if offset:
            param = "%s&offset=%s" % (param, offset) if param else "offset=%s" % offset

        endpoint = self.ENDPOINT % self.author.preferredUsername

        if param:
            endpoint = "%s?%s" % (endpoint, param)

        data = self._pump.request(endpoint)

        return data

    @staticmethod
    def unserialize(data, obj=None):
        """ Produces self._index from JSON data """
        if obj is None:
            self = Inbox()
        else:
            self = obj

        if type(data) == list:
            items = data
        elif type(data) == dict:
            items = data["items"]
        else:
            raise Exception("Unknown type: %s ('%s')" % (type(data), data))

        for v in items:
            # do we know about it?
            obj_type = v["object"]["objectType"].capitalize()

            # todo: make less hacky
            try:
                obj = getattr(self._pump, obj_type)
            except AttributeError:
                continue # what is this stange type of which you are?
            
            try:
                self._inbox.append(obj.unserialize(v))
            except TypeError:
                # caused by missing out the self param, will fix tomorrow
                print("[DEBUG] %s failed" % obj_type)
                pass

        return self 
