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

from pypump.models import (AbstractModel, Postable, Likeable, Shareable, 
                           Commentable, Deleteable)

class Note(AbstractModel, Postable, Likeable, Shareable, Commentable, Deleteable):
    
    @property
    def ENDPOINT(self):
        return "/api/user/{username}/feed".format(
            username=self._pump.client.nickname
            )


    id = ""
    content = ""
    updated = None # last time this was updated
    published = None # When this was published
    deleted = False # has the note been deleted
    liked = False
    author = None

    def __init__(self, content=None, id=None, published=None, updated=None, 
                 deleted=False, liked=False, author=None, display_name=None, url=None,
                 *args, **kwargs):

        super(Note, self).__init__(*args, **kwargs)

        self.content = content
        self.id = id
        self.published = published
        self.updated = updated
        self.deleted = deleted
        self.liked = liked
        self.author = author
        self.display_name = display_name
        self.url = url

    def serialize(self):
        """ Convers the post to JSON """
        data = super(Note, self).serialize()
        data.update({
            "verb":"post",
            "object":{
                "objectType":self.objectType,
                "content":self.content,
            }
        })
        if self.display_name:
            data["object"]["displayName"] = self.display_name

        return data

    def __repr__(self):
        return "<{type} by {name}>".format(
            type=self.TYPE,
            name=self.author.webfinger
            )
   
    def unserialize(self, data):
        """ Goes from JSON -> Note object """
        self.id = data.get("id", None)
        self.url = data.get("url", None)
        self.display_name = data.get("displayName", "")
        self.content = data.get("content", "")
        self.published = parse(data["published"]) if "published" in data else None
        self.updated = parse(data["updated"]) if "updated" in data else self.published
        self.liked = data["liked"] if "liked" in data else False
        self.deleted = parse(data["deleted"]) if "deleted" in data else False
        self.author = self._pump.Person().unserialize(data["author"]) if "author" in data else None
        self.add_links(data)
        return self
