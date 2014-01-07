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
import logging

from pypump.models import AbstractModel
from pypump.models.feed import Feed
from pypump.models.activity import Mapper

_log = logging.getLogger(__name__)

class Collection(AbstractModel):

    _members = None
    _ignore_attr = ["dummyattr", ]
    _mapping = {
        "id": "id",
        "display_name": "displayName",
        "content": "content",
        "author": "author",
        "published": "published",
        "updated": "updated",
        "url": "url"
    }

    def __init__(self, id=None, *args, **kwargs):
        super(Collection, self).__init__(*args, **kwargs)

        self.id = id

    @property
    def members(self):
        self._members = self._members or Feed(self.links["members"], pypump=self._pump)
        return self._members

    @property
    def ENDPOINT(self):
        return self.id

    def add(self, obj):
        """ Adds a member to the collection """
        activity = {
            "verb": "add",
            "object": {
                "objectType": obj.objectType,
                "id": obj.id
            },
            "target":{
                "objectType": "collection",
                "id": self.id
            }
        }

        self._post_activity(activity)

    def remove(self, obj):
        """ Removes a member from the collection """
        activity = {
            "verb": "remove",
            "object": {
                "objectType": obj.objectType,
                "id": obj.id
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
        return self.display_name or self.id

    def __repr__(self):
        return "<{type}: {id}>".format(type=self.TYPE, id=self.id)

    def unserialize(self, data):
        Mapper(pypump=self._pump).parse_map(self, data=data)
        self.add_links(data)
        return self


class Public(object):
    ENDPOINT = "http://activityschema.org/collection/public"

    def __init__(self):
        self.id = self.ENDPOINT
        self.objectType = 'collection'

