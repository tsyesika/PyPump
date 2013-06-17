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

    def __getitem__(self, key):
        """ Adds Inbox[<inbox>] """
        return self._inbox[key]

    def __getslice__(self, start=0, end=None):
        """ allows for a limit """
        if end:
            self._count = end - start
        
        self.offset = start

        self.__request()

    def __len__(self):
        """ Gives amount of items in the inbox """
        return len(self._inbox)

    def __request(self):
        """ Makes a request """
        param = ""

        if self._count:
            param += "count=%s" % self._count

        if self._offset:
            param = "%s+offset=%s" % (param, self._offset) if param else "offset=%s" % self._offset

        endpoint = self.ENDPOINT % self.author.preferredUsername

        if param:
            endpoint = "%s&%s" % param

        data = self._pump.request(endpoint)

        self.unserialize(data)

    @staticmethod
    def unserialize(data):
        """ Produces self._index from JSON data """
        self = Inbox()
        for v in data["items"]:
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
