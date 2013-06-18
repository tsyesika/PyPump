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
from datetime import datetime

from models import AbstractModel
from models.person import Person
from models.comment import Comment

class Note(AbstractModel):
    
    TYPE = "note"
    VERB = "post"

    content = ""
    actor = None # who posted.
    updated = None # last time this was updated
    published = None # When this was published

    # where to?
    to = []
    cc = []

    _likes = [] # cache of likes
    _comments = [] # cache of comemnts

    _links = {}

    def __init__(self, content, to, actor, published=None, updated=None, links=None, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)

        self._links = links if links else {}

        self.content = content
        self.to = to
        self.actor = actor

        if published:
            self.published = published
        else:
            self.published = datetime.now()

        if updated:
            self.updated = updated
        else:
            self.updated = self.published

    def _get_likes(self):
        """ gets the likes """
        if self._likes:
            return self._likes

        # gotta go get them.
        endpoint = self._links["likes"]
        likes = self._pypump.request(endpoint)
        for k,v in likes["items"].items():
            self._likes.append(Person.unserialize(v))

        return self._likes

    likes = property(fset=_get_likes)

    def _get_comments(self): 
        """ Gets the comments """
        if self._comments:
            return self._comments

        endpoint = self._links["comments"]
        comments = self._pump.request(endpoint)
        for k,v in comments["items"].items():
            self._comment.append(Comment.unserialize(v))

        return self._comments

    comments = property(fset=_get_comments)

    def send(self):
        """ Sends the post to the server """
        # post it!
        self.pump.request(self.ENDPOINT, method="POST", data=self.serialize())
    
    def comment(self, comment):
        """ Posts a comment """
        # get self.id?
        comment.send()

    def delete(self):
        """ Delete's the note """
        pass

    def like(self):
        """ Likes the Note """
        pass    

    def unlike(self):
        """ Unlikes the Note """
        pass

    # synonyms
    def favorite(self, *args, **kwargs):
        """ Maps to like """
        return self.like(*args, **kwargs)

    def unfavorite(self, *args, **kwargs):
        """ Maps to unlike """
        return self.unlike(*args, **kwargs)


    def __repr__(self):
        return "<Note by %s at %s>" % (self.actor, self.published.strftime("%Y/%m/%d"))
   
    def __str__(self):
        return self.__repr__()

    def serialize(self):
        """ Seralizes note to be posted """
        query = {
            "verb":self.VERB,
            "object":{
                "objectType":self.TYPE,
                "content":self.content,
            },
        }

        return json.dumps(query)

    @staticmethod
    def unserialize(data):
        """ Goes from JSON -> Note object """
        obj = data["object"]
        
        links = {}
        if "proxy_url" in obj["likes"]:
            links["likes"] = obj["likes"]["proxy_url"]
        else:
            links["likes"] = obj["likes"]["url"]

        if "proxy_url" in obj["replies"]:
            links["comments"] = obj["replies"]["proxy_url"]
        else:
            links["comments"] = obj["replies"]["url"]

        return Note(
            content=obj["content"],
            to=[], # todo: yeh
            cc=[], # todo: ^^
            actor=Note._pump.Person.unserialize(data["actor"]),
            updated=datetime.strptime(data["updated"], Note.TSFORMAT),
            published=datetime.strptime(data["published"], Note.TSFORMAT),
            links=links,
        )
