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

from pypump.exception.ImmutableException import ImmutableException
from pypump.exception.PumpException import PumpException

from pypump.compatability import *

from pypump.models import AbstractModel
from pypump.models.person import Person
from pypump.models.comment import Comment

@implement_to_string
class Note(AbstractModel):
    
    TYPE = "note"
    VERB = "post"
    ENDPOINT = "/api/user/%s/feed"

    id = ""
    summary = ""
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

    def __init__(self, content, summary=None, nid=None, to=None, cc=None, actor=None, published=None, updated=None, links=None, deleted=True, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)

        self._links = links if links else {}

        self.id = nid if nid else None
        self.summary = "" if summary is None else summary
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
        likes = self._pump.request(endpoint, raw=True)
        for k,v in likes["items"].items():
            self._likes.append(Person.unserialize(v))

        return self._likes

    likes = property(fget=_get_likes)

    def _get_comments(self): 
        """ Gets the comments """
        if self._comments:
            return self._comments

        endpoint = self._links["comments"]
        comments = self._pump.request(endpoint, raw=True)
        for v in comments.get("items", []):
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
        comment.note = self
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

        data = self._pump.request("/api/user/%s/feed" % self._pump.nickname, method="POST", data=activity)
        
        if data.get("verb", None) == activity["verb"]:
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

        data = self._pump.request("/api/user/%s/feed" % self._pump.nickname, method="POST", data=activity)

    def unlike(self, verb="unlike"):
        """ Unlikes the Note """
        activity = {
            "verb":verb,
            "object":{
                "id":self.id,
                "objectType":self.TYPE,
            }
        }

        data = self._pump.request("/api/user/%s/feed" % self._pump.nickname, method="POST", data=activity)

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
    def unserialize_to_deleted(data, obj=None):
        """ Unserializes to a deleted note """
        deleted_note = Note("") if obj is None else obj
        deleted_note.deleted = True

        deleted_note.id = data["id"] if "id" in data else ""
        deleted_note.actor = deleted_note._pump.Person.unserialize(data["actor"])        
        deleted_note.updated = datetime.strptime(data["updated"], Note.TSFORMAT)
        deleted_note.published = datetime.strptime(data["published"], Note.TSFORMAT)

        return deleted_note

    @staticmethod
    def unserialize(data, obj=None):
        """ Goes from JSON -> Note object """
        if data.get("verb", "") == "delete":
            return Note.unserialize_to_deleted(data, obj=obj)

        summary = None
        nid = data.get("id", None)
        links = {}
        if "object" in data:
            nid = data["object"].get("id", None)
            data_obj = data["object"]
            content = data["object"].get("content", u"")
            summary = data["content"]
            if "proxy_url" in data_obj.get("likes", []):
                links["likes"] = data_obj["likes"]["proxy_url"]
            elif "likes" in data_obj:
                links["likes"] = data_obj["likes"]["url"]

            if "pump_io" in data_obj.get("replies", {}) and "proxyURL" in data_obj.get["replies"].get("pump_io", {}):
                url = data_obj["replies"]["pump_io"]["proxyURL"].lstrip("http://").lstrip("https://")
                links["comments"] = url.split("/", 1)[1]
            elif links.get("comments", []):
                links["comments"] = data_obj["replies"]["url"]
        else:
            content = data["content"]
        if obj is None:
            return Note(
                    nid=nid,
                    content=content,
                    summary=summary,
                    to=(), # todo still.
                    cc=(), # todo: ^^
                    actor=Note._pump.Person.unserialize(data["actor"]),
                    updated=datetime.strptime(data["updated"], Note.TSFORMAT),
                    published=datetime.strptime(data["published"], Note.TSFORMAT),
                    links=links,
                    )
        else:
            obj = Note(content=content)
            obj.summary = summary
            obj.id = nid
            obj.actor = Note._pump.Person.unserialize(data["actor"]) if "actor" in data else obj.actor
            obj.updated = datetime.strptime(data["updated"], Note.TSFORMAT)
            obj.published = datetime.strptime(data["published"], Note.TSFORMAT)
            obj._links = links
            return obj
