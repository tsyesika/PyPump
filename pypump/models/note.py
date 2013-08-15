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

from pypump.exception.ImmutableException import ImmutableException
from pypump.exception.PumpException import PumpException

from pypump.compatability import *

from pypump.models import AbstractModel

@implement_to_string
class Note(AbstractModel):
    
    VERB = "post"
    ENDPOINT = "/api/user/{username}/feed"

    id = ""
    content = ""
    updated = None # last time this was updated
    published = None # When this was published
    deleted = False # has the note been deleted
    liked = False

    # where to?
    _to = list()
    _cc = list()
    

    _links = dict()

    def __init__(self, content, id=None, to=None, cc=None, 
                 published=None, updated=None, links=None, 
                 deleted=False, liked=False, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)

        self._links = links if links else dict()

        self.id = id if id else None
        self.content = content
        self._to = list() if to is None else to
        self._cc = list() if cc is None else cc

        if published:
            self.published = published
        else:
            self.published = datetime.now()

        if updated:
            self.updated = updated
        else:
            self.updated = self.published
        self.deleted = deleted
        self.liked = liked

    def _get_likes(self):
        """ gets the likes """
        # gotta go get them.
        endpoint = self._links["likes"]
        likes = self._pump.request(endpoint, raw=True)
        likes_obj = list()
        for serialized_person in likes["items"]:
            likes_obj.append(self._pump.Person.unserialize(serialized_person))

        return likes_obj

    likes = property(fget=_get_likes)

    def _get_comments(self): 
        """ Gets the comments """
        endpoint = self._links["replies"]
        comments = self._pump.request(endpoint, raw=True)
        comments_obj = list()
        for v in comments.get("items", comments):
            comments_obj.append(self._pump.Comment.unserialize(v))

        return comments_obj

    comments = property(_get_comments)

    def _post_activity(self, activity):
        """ POSTs activity and updates self with new data in response """
        endpoint = self.ENDPOINT.format(username=self._pump.nickname)
        data = self._pump.request(endpoint, method="POST", data=activity)

        if not data:
            return False        

        if "error" in data:
            raise PumpException(data["error"])

        self.unserialize(data["object"], obj=self)

        return True

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

        activity = {
            "verb":self.VERB,
            "object":{
                "objectType":self.objectType,
                "content":self.content,
            },
            "to": self._to,
            "cc": self._cc,
        }

        return self._post_activity(activity)

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

        return self._post_activity(activity)

    def like(self):
        """ Likes the Note """
        activity = {
            "verb":"like",
            "object":{
                "id":self.id,
                "objectType":self.objectType,
            }
        }

        return self._post_activity(activity)

    def unlike(self, verb="unlike"):
        """ Unlikes the Note """
        activity = {
            "verb":verb,
            "object":{
                "id":self.id,
                "objectType":self.objectType,
            }
        }

        return self._post_activity(activity)

    # synonyms
    def favorite(self, *args, **kwargs):
        """ Maps to like """
        return self.like(verb="favorite", *args, **kwargs)

    def unfavorite(self, *args, **kwargs):
        """ Maps to unlike """
        return self.unlike(verb="unfavorite", *args, **kwargs)

    def __repr__(self):
        return "<{t}>".format(t=self.TYPE)
   
    def __str__(self):
        return str(self.__repr__())

    @classmethod
    def unserialize(cls, data, obj=None):
        """ Goes from JSON -> Note object """
        id = data.get("id", None)
        links = dict()
        content = data.get("content", u"")
        if "proxy_url" in data.get("likes", []):
            links["likes"] = data["likes"]["proxy_url"]
        elif "likes" in data:
            links["likes"] = data["likes"]["url"]

        if "pump_io" in data.get("replies", {}) and "proxyURL" in data["replies"].get("pump_io", {}):
            url = data["replies"]["pump_io"]["proxyURL"].split("://")[-1]
            links["replies"] = url.split("/", 1)[1]
        elif data.get("replies", None):
            links["replies"] = data["replies"]["url"]

        updated=parse(data["updated"])
        published=parse(data["published"])
        liked = data["liked"] if "liked" in data else False
        deleted = parse(data["deleted"]) if "deleted" in data else False

        if obj is None:
            return cls(
                    id=id,
                    content=content,
                    to=(), # todo still.
                    cc=(), # todo: ^^
                    updated=updated,
                    published=published,
                    links=links,
                    liked=liked,
                    deleted=deleted
                    )
        else:
            obj.content = content
            obj.id = id
            obj.updated = updated
            obj.published = published
            obj._links = links
            obj.liked = liked
            obj.deleted = deleted
            return obj
