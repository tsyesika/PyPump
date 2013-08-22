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

from pypump.models import (AbstractModel, Commentable, Likeable, Shareable, 
                           Deleteable)
from pypump.compatability import *

@implement_to_string
class Comment(AbstractModel, Likeable, Shareable, Deleteable, Commentable):

    VERB = "post"

    @property
    def ENDPOINT(self):
        return "/api/user/{username}/feed".format(
            username=self._pump.nickname
            )

    id = None
    content = ""
    inReplyTo = None
    updated = None
    published = None
    deleted = False
    author = None
    _links = None

    def __init__(self, content, id=None, inReplyTo=None, published=None, updated=None,
                 deleted=False, liked=False, author=None, links=None, *args, **kwargs):

        super(Comment, self).__init__(*args, **kwargs)

        self.id = "" if id is None else id
        self.content = content
        self.inReplyTo = inReplyTo
        self.published = published
        self.updated = updated
        self.deleted = deleted
        self.liked = liked
        self.author = self._pump.Person(self._pump.nickname) if author is None else author
        self._links = dict() if links is None else links

    def __repr__(self):
        return "<{type} by {webfinger}>".format(
            type=self.TYPE,
            webfinger=self.author.webfinger
            )

    def __str__(self):
        return str(repr(self))

    def _post_activity(self, activity):
        """ POSTs activity and updates self with new data in response """
        data = self._pump.request(self.ENDPOINT, method="POST", data=activity)

        if not data:
            return False        

        if "error" in data:
            raise PumpException(data["error"])

        self.unserialize(data["object"], obj=self)

        return True

    def send(self):
        activity = {
            "verb":self.VERB,
            "object":{
                "objectType":self.objectType,
                "content":self.content,
                "inReplyTo":{
                    "id":self.inReplyTo.id,
                    "objectType":self.inReplyTo.objectType,
                },
            },
        }

        return self._post_activity(activity)

    @classmethod
    def unserialize(cls, data, obj=None):
        """ from JSON -> Comment """
        content = data["content"] if "content" in data else ""
        id = data["id"] if "id" in data else ""
        published = parse(data["published"])
        updated = parse(data["updated"]) if "updated" in data else False
        deleted = parse(data["deleted"]) if "deleted" in data else False
        liked = data["liked"] if "liked" in data else False
        author = cls._pump.Person.unserialize(data["author"]) if "author" in data else None

        links = dict()
        for i in ["likes", "replies", "shares"]:
            if data.get(i, None):
                if "pump_io" in data[i]:
                    links[i] = data[i]["pump_io"]["proxyURL"]
                else:
                    links[i] = data[i]["url"]

        if obj is None:
            return cls(
                content=content,
                id=id,
                published=published,
                updated=updated,
                deleted=deleted,
                liked=liked,
                author=author,
                links=links
                )
        
        obj.content = content
        obj.id = id
        obj.published = published
        obj.updated = updated
        obj.deleted = deleted
        obj.liked = liked
        obj.author = author if author else obj.author
        obj._links = links
        return obj
        
