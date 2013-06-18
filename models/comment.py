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

from models import AbstractModel

class Comment(AbstractModel):

    TYPE = "comment"

    content = ""
    summary = ""
    note = None
    updated = None
    actor = None
    published = None
    likes = []

    def __init__(self, content, summary, actor, note=None,published=None, updated=None, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)

        self.content = content
        self.summary = summary
        self.note = note
        self.actor = actor
        self.author = self.actor

        if published:
            self.published = published 
        else:
            self.published = datetime.now()

        if updated:
            self.updated = updated
        else:
            self.updated = self.published

    def __repr__(self):
        return "<Comment by %s at %s>" % (self.actor, self.published.strftime("%Y/%m/%d"))

    def __str__(self):
        return self.__repr__()

    def like(self):
        """ Will like the comment """
        pass

    def unlike(self):
        """ If comment is liked, it will unlike it """
        pass

    def delete(self):
        """ Will delete the comment if the comment is posted by you """
        pass


    @staticmethod
    def unserialize(data, obj=None):
        """ from JSON -> Comment """
        if "object" in data:
            published = datetime.strptime(data["object"]["published"], Comment.TSFORMAT)
            updated = datetime.strptime(data["object"]["updated"], Comment.TSFORMAT)
            summary = data["content"]
            content = data["object"]["content"]
        else:
            published = datetime.strptime(data["published"], Comment.TSFORMAT)
            updated = datetime.strptime(data["updated"], Comment.TSFORMAT)
            summary = ""
            content = data["content"]

        person = data["actor"] if "actor" in data else data["author"]
        actor = Comment._pump.Person.unserialize(person)
       
        if obj is None:
            return Comment(content=content, summary=summary, actor=actor, published=published, updated=updated)
        
        obj.content = content
        obj.summary = summary
        obj.published = published
        obj.updated = updated
        return obj
        
