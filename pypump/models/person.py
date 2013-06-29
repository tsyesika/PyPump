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

from pypump.exception.PumpException import PumpException
from pypump.models import AbstractModel
from pypump.compatability import *

@implement_to_string
class Person(AbstractModel):

    _mapping = {
        "preferredUsername":"username",
        "displayName":"display_name",
    }


    TYPE = "person"
    ENDPOINT = "/api/user/%s/feed"

    id = ""
    username = ""
    display_name = ""
    url = "" # url to profile
    updated = None # Last time this was updated
    published = None # when they joined (I think?)
    location = None # place item
    summary = "" # lil bit about them =]    
    image = None # Image items
    inbox = None

    is_self = False # is this you?

    def __init__(self, webfinger=None, id="", username="", url="", summary="", 
                 inbox=None, display_name="", image=None, published=None, 
                 updated=None, location=None, me=None, *args, **kwargs):
        """
        id - the ID of the person. e.g. acct:Username@server.example
        username - persons username
        url - url to profile
        summary - summary of the user
        inbox - This is the persons inbox
        display_name - what the user want's to show up (defualt: username)
        image - image of the user (default: No image/None)
        published - when the user joined pump (default: now)
        updated - when the user last updated their profile (default: published)
        location - where the user resides (default: No location/None)
        me - you, used to set is_self, if not given it assumes this person _isn't_ you
        """
        super(Person, self).__init__(*args, **kwargs)

        # okay we need to check if the webfinger is being used
        if isinstance(webfinger, string_types):
            # first clean up
            webfinger = webfinger.lstrip(" ").rstrip(" ")
            # okay now we need to look if it's on our servers or not.
            if "@" in webfinger:
                username, server = webfinger.split("@")
            else:
                # they probably just gave a username, the assumption is it's on our server!
                username, server = webfinger, self._pump.server
            self.inbox = self._pump.Inbox(username=self)
            # now do some checking
            if server == self._pump.server:
                # cool we can get quite a bit of info.
                data = self._pump.request("/api/user/%s/profile" % username)
                self.unserialize(data, obj=self)
                # lets hope we've found it
                return
            else:
                # right not a huge amount we can do
                self.id = "acct:%s@%s" % (username, server)
                self.username = username
                self.server = server
                self.is_self = False
                self.inbox = self._pump.Inbox("/api/user/%s/inbox" % username) if inbox is None else inbox
                return 

        self.id = id
        self.inbox = self._pump.Inbox(self) if inbox is None else inbox
        self.username = username
        self.url = url
        self.summary = summary
        self.image = image        

        if display_name:
            self.display_name = display_name
        else:
            self.display_name = self.username

        if published:
            self.published = published
        else:
            self.published = datetime.now()
        
        if updated:
            self.updated = updated
        else:
            self.updated = self.published

        if me and self.id == me.id:
            self.is_self = True

    def follow(self): 
        """ You follow this user """
        activity = {
            "verb":"follow",
            "object":{
                "id":self.id,
                "objectType":"person",
            }
        }

        endpoint = self.ENDPOINT % self._pump.nickname

        data = self._pump.request(endpoint, method="POST", data=activity)

        if "error" in data:
            raise PumpException(data["error"])

        self.unserialize(data, obj=self) 
        return True

    def unfollow(self):
        """ Unfollow a user """
        activity = {
            "verb":"unfollow",
            "object":{
                "id":self.id,
                "objectType":"person",
            }
        }

        endpoint = self.ENDPOINT % self._pump.nickname

        data = self._pump.request(endpoint, method="POST", data=activity)

        if "error" in data:
            raise PumpException(data["error"])

        # now to do something!

    def __repr__(self):
        return self.id.lstrip("acct:")

    def __str__(self):
        return self.__repr__()

    @classmethod
    def unserialize_service(cls, data, obj):
        """ Unserializes the data from a service """
        id = data["id"]
        display = data["displayName"]
        updated = datetime.strptime(data["updated"], cls.TSFORMAT) if "updated" in data else datetime.now()
        published = datetime.strptime(data["published"], cls.TSFORMAT) if "published" in data else updated

        if obj is None:
            obj = cls()

        obj.id = id
        obj.display = display
        obj.updated = updated
        obj.published = published
        return obj

    @classmethod
    def unserialize(cls, data, obj=None):
        """ Goes from JSON -> Person object """
        if data.get("objectType", "") == "service":
            return cls.unserialize_service(data, obj)

        self = cls() if obj is None else obj

        if "verb" in data and data["verb"] in ["follow", "unfollow"]:
            return None

    
        username = data["preferredUsername"]
        display = data["displayName"]

        self.id = "acct:%s@%s" % (username, self._pump.server)
        self.username = username
        self.display_name = display
        self.url = data["links"]["self"]["href"]
        self.summary = data["summary"] if "summary" in data else ""
        self.updated = datetime.strptime(data["updated"], cls.TSFORMAT) if "updated" in data else datetime.now()
        self.published = datetime.strptime(data["published"], cls.TSFORMAT) if "published" in data else self.updated
        self.me = True if "acct:%s@%s" % (self._pump.nickname, self._pump.server) == self.id else False
        self.location = self._pump.Location.unserialize(data["location"]) if "location" in data else None

        self.updated = datetime.strptime(data["updated"], self.TSFORMAT) if "updated" in data else datetime.now()
        return self
