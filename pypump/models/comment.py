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
from pypump.models.activity import Mapper

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

    def __init__(self, content=None, id=None, inReplyTo=None, published=None, updated=None,
                 deleted=False, liked=False, author=None, *args, **kwargs):

        super(Comment, self).__init__(*args, **kwargs)

        self.id = "" if id is None else id
        self.content = content
        self.inReplyTo = inReplyTo
        self.published = published
        self.updated = updated
        self.deleted = deleted
        self.liked = liked
        self.author = author

    def __repr__(self):
        return "<{type} by {webfinger}>".format(
            type=self.TYPE,
            webfinger=getattr(self.author,'webfinger', 'unknown')
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
        ignore_attr = ["dummyattr",]
        mapping = {
            "content": "content",
            "id": "id",
            "url": "url",
            "published": "published",
            "updated": "updated",
            "deleted": "deleted",
            "liked" : "liked",
            "author" : "author",
            "in_reply_to" : "inReplyTo"
        }
        Mapper(pypump=self._pump).parse_map(self, mapping=mapping, ignore_attr=ignore_attr, data=data)
        self.add_links(data)
        return self
        
