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

    def add(self):
        """
        {
        "verb": "add",
        "object":{
        "objectType": "person",
        "id": "acct:user@server"
        },
        "target":{
        "objectType": "collection",
        "id": "server/api/collection/uuid"
        }
        }
        """
        pass

    def delete(self):
        """
        {
        "verb": "delete",
        "object":{
        "objectType": "person",
        "id": "acct:user@server"
        },
        "target":{
        "objectType": "collection",
        "id": "server/api/collection/uuid"
        }
        }
        """
        pass

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return "<{type}: {id}>".format(type=self.TYPE, id=self.id)

    @classmethod
    def unserialize(cls, data, obj=False):
        obj = obj or cls(data["id"])
        obj.display_name = data["displayName"]
        obj.links = dict()
        for i in ["members",]:
            if i in data:
                obj.links[i] = data[i]["url"]

        return obj
