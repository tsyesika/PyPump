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

from pypump.models import (PumpObject, Commentable, Likeable, Shareable, 
                           Deleteable, Postable, Mapper)

class Comment(PumpObject, Likeable, Shareable, Deleteable, Commentable, Postable):

    object_type = 'comment'
    _ignore_attr = ["summary",]
    _mapping = {}

    id = None
    url = None
    content = None
    published = None
    updated = None
    deleted = None
    liked = None
    author = None
    in_reply_to = None

    def __init__(self, content=None, id=None, in_reply_to=None, published=None, updated=None,
                 deleted=None, liked=None, author=None, url=None, *args, **kwargs):

        super(Comment, self).__init__(*args, **kwargs)

        self.id = id
        self.url = url
        self.content = content
        self.published = published
        self.updated = updated
        self.deleted = deleted
        self.liked = liked
        self.author = author
        self.in_reply_to = in_reply_to

    def __repr__(self):
        return "<{type} by {webfinger}>".format(
            type=self.object_type.capitalize(),
            webfinger=getattr(self.author,'webfinger', 'unknown')
        )

    def __unicode__(self):
        return u"{type} by {webfinger}".format(
            type=self.object_type,
            webfinger=getattr(self.author,'webfinger', 'unknown')
        )

    def serialize(self):
        data = super(Comment, self).serialize()
        data.update({
            "verb":"post",
            "object":{
                "objectType":self.object_type,
                "content":self.content,
                "inReplyTo":{
                    "id":self.in_reply_to.id,
                    "objectType":self.in_reply_to.object_type,
                },
            },
        })

        return data

    def unserialize(self, data):
        """ from JSON -> Comment """
        Mapper(pypump=self._pump).parse_map(self, data=data)
        self.add_links(data)
        return self
        
