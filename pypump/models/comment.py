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

from datetime import datetime
from dateutil.parser import parse

from pypump.models import AbstractModel
from pypump.compatability import *

@implement_to_string
class Comment(AbstractModel):

    VERB = "post"
    ENDPOINT = "/api/user/{username}/feed"

    id = None
    content = ""
    note = None
    updated = None
    published = None
    deleted = False
    liked = False
    likes = []

    def __init__(self, content, id=None, note=None, published=None, updated=None,
                 deleted=False, liked = False, *args, **kwargs):

        super(Comment, self).__init__(*args, **kwargs)

        self.id = "" if id is None else id
        self.content = content
        self.note = note
        self.published = published
        self.updated = updated
        self.deleted = deleted
        self.liked = liked

    def __repr__(self):
        return self.TYPE

    def __str__(self):
        return str(self.__repr__())

    def like(self, verb="like"):
        """ Will like the comment """
        activity = {
            "verb":verb,
            "object":{
                "id":self.id,
                "objectType":self.objectType,
            },
        
        }

        endpoint = self.ENDPOINT.format(username=self._pump.nickname)
        data = self._pump.request(endpoint, method="POST", data=activity)

        if not data:
            return False        

        if "error" in data:
            raise PumpError(data["error"])

        self.unserialize(data["object"], obj=self)

        return True

    def unlike(self, verb="unlike"):
        """ If comment is liked, it will unlike it """
        activity = {
            "verb":verb,
            "object":{
                "id":self.id,
                "objectType":self.objectType,
            },
        }

        endpoint = self.ENDPOINT.format(username=self._pump.nickname)
        data = self._pump.request(endpoint, method="POST", data=activity)

        if not data:
            return False

        if "error" in data:
            raise PumpError(data["error"])

        self.unserialize(data["object"], obj=self)

        return True

    def delete(self):
        """ Will delete the comment if the comment is posted by you """
        activity = {
            "verb":"delete",
            "object":{
                "id":self.id,
                "objectType":self.objectType,
            },
        }

        endpoint = self.ENDPOINT.format(username=self._pump.nickname)
        data = self._pump.request(endpoint, method="POST", data=activity)

        if not data:
            return False

        if "error" in data:
            raise PumpError(data["error"])

        self.unserialize(data["object"], obj=self)

        return True

    def send(self):
        activity = {
            "verb":self.VERB,
            "object":{
                "objectType":self.objectType,
                "content":self.content,
                "inReplyTo":{
                    "id":self.note.id,
                    "objectType":self.note.objectType,
                },
            },
        }
    
        endpoint = self.ENDPOINT.format(username=self._pump.nickname)
        data = self._pump.request(endpoint, method="POST", data=activity)

        if not data:
            return False

        if "error" in data:
            raise PumpException(data["data"])

        self.unserialize(data["object"], obj=self)

        return True

    @classmethod
    def unserialize(cls, data, obj=None):
        """ from JSON -> Comment """
        content = data["content"] if "content" in data else ""
        id = data["id"] if "id" in data else ""
        published = parse(data["published"])
        updated = parse(data["updated"])
        deleted = parse(data["deleted"]) if "deleted" in data else False
        liked = data["liked"] if "liked" in data else False

        if obj is None:
            return cls(
                content = content,
                id = id,
                published = published,
                updated = updated,
                deleted = deleted,
                liked = liked
                )
        
        obj.content = content
        obj.id = id
        obj.published = published
        obj.updated = updated
        obj.deleted = deleted
        obj.liked = liked
        return obj
        
