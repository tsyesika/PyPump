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
from pypump.models.feed import Feed

@implement_to_string
class Collection(AbstractModel):
    
    def __init__(self, id):
        self.id = id

    @property
    def members(self):
        self._members = Feed(self, self.links["members"])
        return self._members

    @property
    def ENDPOINT(self):
        return self.id

    def add(self, person):
        """ Adds a person to the collection """
        activity = {
            "verb": "add",
            "object": {
                "objectType": "person",
                "id": person.id
            },
            "target":{
                "objectType": "collection",
                "id": self.id
            }
        }

        self._post_activity(activity)

    def remove(self, person):
        """ Removes a person from the collection """
        activity = {
            "verb": "remove",
            "object": {
                "objectType": "person",
                "id": person.id
            },
            "target":{
                "objectType": "collection",
                "id": self.id
            }
        }

        self._post_activity(activity)

    def delete(self):
        """ Deletes the collection """
        self._pump.request(self.id, method="DELETE")

    def __str__(self):
        return str(repr(self))

    def __repr__(self):
        return "<{type}: {id}>".format(type=self.TYPE, id=self.id)

    @classmethod
    def unserialize(cls, data, obj=False):
        obj = obj or cls(data["id"])
        obj.display_name = data["displayName"] if "displayName" in data else None
        obj.content = data["content"] if "content" in data else None
        obj.links = dict()
        for i in ["members",]:
            if i in data:
                obj.links[i] = data[i]["url"]

        return obj


class Public(object):
    ENDPOINT = "http://activityschema.org/collection/public"

    def __init__(self):
        self.id = self.ENDPOINT

