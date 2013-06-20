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

from exceptions.ImmutableException import ImmutableException
from exceptions.PumpException import PumpException

from models import AbstractModel
from models.person import Person
from models.comment import Comment

class Note(AbstractModel):
    
    TYPE = "note"
    VERB = "post"
    ENDPOINT = "/api/user/%s/feed"

    id = ""
    content = ""
    actor = None # who posted.
    updated = None # last time this was updated
    published = None # When this was published
    deleted = False # has the note been deleted

    # where to?
    _to = []
    _cc = []
    

    _likes = [] # cache of likes
    _comments = [] # cache of comemnts

    _links = {}

    def __init__(self, content, nid=None, to=None, cc=None, actor=None, published=None, updated=None, links=None, deleted=True, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)

        self._links = links if links else {}

        self.id if nid else None
        self.content = content
        self._to = [] if to is None else to
        self._cc = [] if cc is None else cc
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

    likes = property(fget=_get_likes)

    def _get_comments(self): 
        """ Gets the comments """
        if self._comments:
            return self._comments

        endpoint = self._links["comments"]
        comments = self._pump.request(endpoint)
        for v in comments["items"]:
            self._comments.append(Comment.unserialize(v))

        return self._comments

    comments = property(_get_comments)

    def set_to(self, people):
        """ Allows you to set/change who it's to """
        # check if it's been locked
        if isinstance(self._to, tuple):
            raise ImmutableError("people", self)

        if isinstance(people, list):
            self._to = people
        elif isinstance(people, str):
            self._to = [people]
        else:
            raise TypeError("Unknown type %s (%s)" % (type(people), people))

    to = property(fset=set_to)

    def set_cc(self, people):
        """ Allows you to set/change who it's cc'ed to """
        # check if it's been locked
        if isinstance(self._cc, tuple):
            raise ImmutableError("people", self)

        if isinstance(people, list):
            self._cc = people
        elif isinstance(people, str):
            self._cc = [people]
        else:
            raise TypeError("Unknown type %s (%s)" % (type(people), people))

    cc = property(fset=set_cc, fget=_cc)

    def send(self):
        """ Sends the post to the server """
        # lock the info in
        self._to = tuple(self._to)
        self._cc = tuple(self._cc)

        # post it!
        data = self._pump.request(self.ENDPOINT % self._pump.nickname, method="POST", data=self.serialize())

        # we need to actually store the new note data the server has sent back
        if "error" in data:
            # oh dear, raise
            raise PumpException(data["error"])
         
        self.unserialize(data["object"], obj=self)

    def comment(self, comment):
        """ Posts a comment """
        # get self.id?
        comment.send()

    def delete(self):
        """ Delete's the note """
        activity = {
            "verb":"delete",
            "object":{
                "id":self.id,
                "objectType":self.TYPE,
            }
        }

        data = self._pump.request("/api/user/%s/feed" % self._pump.nickname, method="POST")
        
        if "verb" in data and data["verb"] == activity["verb"]:
            self.deleted = True
            return True

        return False

    def like(self):
        """ Likes the Note """
        activity = {
            "verb":"like",
            "object":{
                "id":self.id,
                "objectType":self.TYPE,
            }
        }

        data = self._pump.request("/api/user/%s/feed" % self._pump.nickname, methods="POST")

    def unlike(self, verb="unlike"):
        """ Unlikes the Note """
        activity = {
            "verb":verb,
            "object":{
                "id":self.id,
                "objectType":self.TYPE,
            }
        }

        data = self._pump.request("/api/user/%s/feed" % self._pump.nickname, method="POST")

    # synonyms
    def favorite(self, *args, **kwargs):
        """ Maps to like """
        return self.like(verb="favorite", *args, **kwargs)

    def unfavorite(self, *args, **kwargs):
        """ Maps to unlike """
        return self.unlike(verb="unfavorite", *args, **kwargs)

    def __repr__(self):
        note_type = "Deleted Note" if self.deleted else "Note"
        return "<%s by %s at %s>" % (note_type, self.actor, self.published.strftime("%Y/%m/%d"))
   
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
    def unserialize_to_deleted(data):
        """ Unserializes to a deleted note """
        deleted_note = Note("")
        delete_note.delete = True

        deleted_note.id = data["id"] if "id" in data else ""
        deleted_note.actor = self._pump.Person.unserialize(data["actor"])        
        deleted_note.updated = datetime.strptime(data["updated"], Note.TSFORMAT)
        deleted_note.published = datetime.strptime(data["published"], Note.TSFORMAT)

        return deleted_note

    @staticmethod
    def unserialize(data):
        """ Goes from JSON -> Note object """
        if data["verb"] == "delete":
            return Note.unserialize_to_deleted(date)

        obj = data["object"]
        
        links = {}
        if "proxy_url" in obj["likes"]:
            links["likes"] = obj["likes"]["proxy_url"]
        else:
            links["likes"] = obj["likes"]["url"]

        if "pump_io" in obj["replies"] and "proxyURL" in obj["replies"]["pump_io"]:
            url = obj["replies"]["pump_io"]["proxyURL"].lstrip("http://").lstrip("https://")
            links["comments"] = url.split("/", 1)[1]
        else:
            links["comments"] = obj["replies"]["url"]

        return Note(
            id=obj["id"],
            content=obj["content"],
            to=(), # todo still.
            cc=(), # todo: ^^
            actor=Note._pump.Person.unserialize(data["actor"]),
            updated=datetime.strptime(data["updated"], Note.TSFORMAT),
            published=datetime.strptime(data["published"], Note.TSFORMAT),
            links=links,
        )
