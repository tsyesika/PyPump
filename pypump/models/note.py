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
    
    VERB = "post"
    ENDPOINT = "/api/user/{username}/feed"

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

    def __init__(self, content, summary=None, nid=None, to=None, cc=None, 
                 actor=None, published=None, updated=None, links=None, 
                 deleted=True, *args, **kwargs):
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

        if type(people) == tuple:
            people = list(people)
        if type(people) != list:
            people = [people]

        for i, item in enumerate(people):
            if is_class(item):
                people[i] = item()

            if isinstance(people[i], self._pump.Person):
                people[i] = {
                    "id": people[i].id,
                    "objectType": people[i].objectType,
                    }
            else:
                # must be collection/list
                people[i] = people[i].serialize(as_dict=True)

        self._to = people

    def get_to(self):
        return self._to

    to = property(fset=set_to, fget=get_to)

    def set_cc(self, people):
        """ Allows you to set/change who it's cc'ed to """
        # check if it's been locked
        if isinstance(self._cc, tuple):
            raise ImmutableError("people", self)

        if type(people) == tuple:
            people = list(people)
        if type(people) != list:
            people = [people]

        for i, item in enumerate(people):
            if is_class(item):
                people[i] = item()

            if isinstance(people[i], self._pump.Person):
                people[i] = {
                    "id": people[i].id,
                    "objectType": people[i].objectType,
                    }
            else:
                # must be collection/list
                people[i] = people[i].serialize(as_dict=True)

        self._cc = people

    def get_cc(self):
        return self._cc

    cc = property(fset=set_cc, fget=get_cc)

    def send(self):
        """ Sends the post to the server """
        # lock the info in
        self._to = tuple(self._to)
        self._cc = tuple(self._cc)

        # post it!
        data = self._pump.request(
                self.ENDPOINT.format(username=self._pump.nickname),
                method="POST",
                data=self.serialize()
                )

        # we need to actually store the new note data the server has sent back
        if "error" in data:
            # oh dear, raise
            raise PumpException(data["error"])
         
        self.unserialize(data, obj=self)

        return self

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
                "objectType": self.objectType,
            }
        }

        data = self._pump.request(
                "/api/user/{username}/feed".format(username=self._pump.nickname),
                method="POST",
                data=activity
                )

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
                "objectType":self.objectType,
            }
        }

        data = self._pump.request(
                self.ENDPOINT.format(username=self._pump.nickname),
                method="POST",
                data=activity
                )

    def unlike(self, verb="unlike"):
        """ Unlikes the Note """
        activity = {
            "verb":verb,
            "object":{
                "id":self.id,
                "objectType":self.objectType,
            }
        }

        data = self._pump.request(
                self.ENDPOINT.format(username=self._pump.nickname),
                method="POST",
                data=activity
                )

    # synonyms
    def favorite(self, *args, **kwargs):
        """ Maps to like """
        return self.like(verb="favorite", *args, **kwargs)

    def unfavorite(self, *args, **kwargs):
        """ Maps to unlike """
        return self.unlike(verb="unfavorite", *args, **kwargs)

    def __repr__(self):
        note_type = "Deleted {0}".format(self.TYPE) if self.deleted else self.TYPE
        return "<{type} by {person} at {date}>".format(
                type=note_type,
                person=self.actor,
                date=self.published.strftime("%Y/%m/%d")
                )
   
    def __str__(self):
        return str(self.__repr__())

    def serialize(self):
        """ Seralizes note to be posted """
        query = {
            "verb":self.VERB,
            "object":{
                "objectType":self.objectType,
                "content":self.content,
            },
            "to": self._to,
            "cc": self._cc,
        }

        return json.dumps(query)

    @classmethod
    def unserialize_to_deleted(cls, data, obj=None):
        """ Unserializes to a deleted note """
        deleted_note = cls(str()) if obj is None else obj
        deleted_note.deleted = True

        deleted_note.id = data["id"] if "id" in data else ""
        deleted_note.actor = deleted_note._pump.Person.unserialize(data["actor"])        
        deleted_note.updated = datetime.strptime(data["updated"], cls.TSFORMAT)
        deleted_note.published = datetime.strptime(data["published"], cls.TSFORMAT)

        return deleted_note

    @classmethod
    def unserialize(cls, data, obj=None):
        """ Goes from JSON -> Note object """
        if data.get("verb", "") == "delete":
            return cls.unserialize_to_deleted(data, obj=obj)
        summary = None
        nid = data.get("id", None)
        links = {}
        if "object" in data:
            data_obj = data["object"]
            nid = data_obj.get("id", nid)
            content = data["object"].get("content", u"")
            summary = data["content"]
            if "proxy_url" in data_obj.get("likes", []):
                links["likes"] = data_obj["likes"]["proxy_url"]
            elif "likes" in data_obj:
                links["likes"] = data_obj["likes"]["url"]

            if "pump_io" in data_obj.get("replies", {}) and "proxyURL" in data_obj["replies"].get("pump_io", {}):
                url = data_obj["replies"]["pump_io"]["proxyURL"].lstrip("http://").lstrip("https://")
                links["comments"] = url.split("/", 1)[1]
            elif links.get("comments", []):
                links["comments"] = data_obj["replies"]["url"]
        else:
            content = data["content"]
        if obj is None:
            return cls(
                    nid=nid,
                    content=content,
                    summary=summary,
                    to=(), # todo still.
                    cc=(), # todo: ^^
                    actor=cls._pump.Person.unserialize(data["actor"]),
                    updated=datetime.strptime(data["updated"], cls.TSFORMAT),
                    published=datetime.strptime(data["published"], cls.TSFORMAT),
                    links=links,
                    )
        else:
            obj.content = content
            obj.summary = summary
            obj.id = nid
            obj.actor = cls._pump.Person.unserialize(data["actor"]) if "actor" in data else obj.actor
            obj.updated = datetime.strptime(data["updated"], cls.TSFORMAT)
            obj.published = datetime.strptime(data["published"], cls.TSFORMAT)
            obj._links = links
            return obj
