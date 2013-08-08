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
    summary = ""
    note = None
    updated = None
    actor = None
    published = None
    likes = []

    def __init__(self, content, cid=None, summary=None, note=None, 
                 published=None, updated=None, actor=None, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)

        self.id = "" if cid is None else cid
        self.content = content
        self.summary = summary
        self.note = note
        self.actor = actor

        if published:
            self.published = published 
        else:
            self.published = datetime.now()

        if updated:
            self.updated = updated
        else:
            self.updated = self.published

    def __repr__(self):
        return "<{type} by {name} at {date}>".format(
                    type=self.TYPE,
                    name=self.actor,
                    date=self.published.strftime("%Y/%m/%d")
                    )

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

        if not data:
            return False

        if "error" in data:
            raise PumpError(data["error"])

        return True

    def delete(self):
        """ Will delete the comment if the comment is posted by you """
        activity = {
            "verb":"delete",
            "objecty":{
                "id":self.id,
                "objectType":self.objectType,
            },
        }

        if not data:
            return False

        if "error" in data:
            raise PumpError(data["error"])

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

        self.unserialize(data, obj=self)

        return True

    @classmethod
    def unserialize(cls, data, obj=None):
        """ from JSON -> Comment """
        if "object" in data:
            published = parse(data["object"]["published"])
            updated = parse(data["object"]["updated"])
            summary = data["content"]
            content = data["object"]["content"]
        else:
            published = parse(data["published"])
            updated = parse(data["updated"])
            summary = ""
            content = data["content"]

        person = data["actor"] if "actor" in data else data["author"]
        actor = Comment._pump.Person.unserialize(person)
       
        if obj is None:
            cid = data["id"] if "id" in data else ""
            return cls(
                content=content,
                cid=cid,
                actor=actor,
                summary=summary,
                published=published,
                updated=updated
                )
        
        obj.id = data["id"] if "id" in data else ""
        obj.actor = actor
        obj.content = content
        obj.summary = summary
        obj.published = published
        obj.updated = updated
        return obj
        
