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
import json

from pypump.models import AbstractModel
from pypump.exception import PyPumpException
from pypump.compatability import *

@implement_to_string
class List(AbstractModel):

    TYPE = "Collection"
    ENDPOINT = "api/user/{username}/lists/{name}"

    id = None
    name = None

    def __init__(self, name, id=None, *args, **kwargs):
        self.name = name
        self.id = self.id if id is None else id

        if self.id is None and self.name:
            user_lists = self.all()
            for user_list in user_lists:
                if user_list.name == self.name:
                    self.id = user_list.id
            
            if self.id is None:
                error = "Can't find list with name {0!r} (Lists found: {1})".format(
                        self.name,
                        ", ".join(user_lists))
                PyPumpException(error)
        
        super(List, self).__init__(*args, **kwargs)

    @classmethod
    def all(cls):
        """ Lists all of the users lists """
        data = cls._pump.request(cls.ENDPOINT.format(
                username=cls._pump.nickname,
                name="person"
                ))
        
        lists = list()
        for item in data["items"]:
            lists.append(cls.unserialize(item))

        return lists

    def serialize(self, as_dict=False):
        """ Serializes data out to server """
        data = {
            "id": self.id,
            "objectType": self.objectType,
        }

        if as_dict:
            return data

        return json.dumps(data)

    @classmethod
    def unserialize(cls, data, obj=None):
        """ Takes data from the server and builds list """
        id = data["id"]
        name = data["displayName"]
        
        if obj is None:
            obj = cls(name=name, id=id)
        else:
            obj.id = id
            obj.name = name

        return obj

class Public(List):
    ENDPOINT = "http://activityschema.org/collection/public"

    def __init__(self, *args, **kwargs):
        self.id = self.ENDPOINT
        super(Public, self).__init__(name=self.TYPE, *args, **kwargs)

class Followers(List):
    ENDPOINT = "api/user/{username}/followers"

    def __init__(self, *args, **kwargs):
        self.ENDPOINT = self._pump.build_url(self.ENDPOINT.format(username=self._pump.nickname))
        self.id = self.ENDPOINT
        super(Followers, self).__init__(name=self.TYPE, *args, **kwargs)

class Following(List):
    ENDPOINT = "api/user/{username}/following"

    def __init__(self, *args, **kwargs):
        self.ENDPOINT = self._pump.build_url(self.ENDPOINT.format(username=self._pump.nickname))
        self.id = self.ENDPOINT
        super(Following, self).__init__(name=self.TYPE, *args, **kwargs)
