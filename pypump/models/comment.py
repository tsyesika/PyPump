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

from dateutil.parser import parse
from pypump.models import (AbstractModel, Commentable, Likeable, Shareable, 
                           Deleteable)

class Comment(AbstractModel, Likeable, Shareable, Deleteable, Commentable):

    @property
    def ENDPOINT(self):
        return "/api/user/{username}/feed".format(
            username=self._pump.client.nickname
            )

    id = None
    content = ""
    inReplyTo = None
    updated = None
    published = None
    deleted = False
    author = None
    _links = None

    def __init__(self, content=None, id=None, inReplyTo=None, published=None, updated=None,
                 deleted=False, liked=False, author=None, links=None, *args, **kwargs):

        super(Comment, self).__init__(*args, **kwargs)

        self.id = "" if id is None else id
        self.content = content
        self.inReplyTo = inReplyTo
        self.published = published
        self.updated = updated
        self.deleted = deleted
        self.liked = liked
        self.author = self._pump.me if author is None else author
        self._links = dict() if links is None else links

    def __repr__(self):
        return "<{type} by {webfinger}>".format(
            type=self.TYPE,
            webfinger=self.author.webfinger
            )

    def send(self):
        activity = {
            "verb":"post",
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

    def unserialize(self, data):
        """ from JSON -> Comment """
        self.content = data["content"] if "content" in data else ""
        self.id = data["id"] if "id" in data else ""
        self.published = parse(data["published"]) if "publised" in data else False
        self.updated = parse(data["updated"]) if "updated" in data else False
        self.deleted = parse(data["deleted"]) if "deleted" in data else False
        self.liked = data["liked"] if "liked" in data else False
        self.author = self._pump.Person().unserialize(data["author"]) if "author" in data else None

        links = dict()
        for i in ["likes", "replies", "shares"]:
            if data.get(i, None):
                if "pump_io" in data[i]:
                    links[i] = data[i]["pump_io"]["proxyURL"]
                else:
                    links[i] = data[i]["url"]

        self._links = links
        return self
        
