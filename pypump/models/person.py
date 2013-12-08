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

import six

from datetime import datetime
from dateutil.parser import parse

from pypump.models import AbstractModel
from pypump.models.feed import (Followers, Following, Lists,
                                Favorites, Inbox, Outbox)

class Person(AbstractModel):

    _mapping = {
        "preferredUsername":"username",
        "displayName":"display_name",
    }


    TYPE = "person"
    ENDPOINT = "/api/user/{username}/feed"

    id = ""
    username = ""
    display_name = ""
    url = "" # url to profile
    updated = None # Last time this was updated
    published = None # when they joined (I think?)
    location = None # place item
    summary = "" # lil bit about them =]    
    image = None # Image items

    _outbox = None
    _followers = None
    _following = None
    _favorites = None
    _lists = None

    @property
    def outbox(self):
        self._outbox = self._outbox or Outbox(self)
        return self._outbox

    @property
    def followers(self):
        self._followers = self._followers or Followers(self)
        return self._followers

    @property
    def following(self):
        self._following = self._following or Following(self)
        return self._following

    @property
    def favorites(self):
        self._favorites = self._favorites or Favorites(self)
        return self._favorites

    @property
    def lists(self):
        self._lists = self._lists or Lists(self)
        return self._lists

    def __init__(self, webfinger=None, id="", username="", url="", summary="", 
                 display_name="", image=None, 
                 published=None, updated=None, location=None,
                 *args, **kwargs):
        """
        id - the ID of the person. e.g. acct:Username@server.example
        username - persons username
        url - url to profile
        summary - summary of the user
        display_name - what the user want's to show up (default: username)
        image - image of the user (default: No image/None)
        published - when the user joined pump (default: None)
        updated - when the user last updated their profile (default: published)
        location - where the user resides (default: No location/None)
        """
        super(Person, self).__init__(*args, **kwargs)

        # okay we need to check if the webfinger is being used
        if isinstance(webfinger, six.string_types):
            # first clean up
            webfinger = webfinger.strip(" ")
            # okay now we need to look if it's on our servers or not.
            if "@" in webfinger:
                self.username, self.server = webfinger.split("@")
            else:
                # they probably just gave a username, the assumption is it's on our server!
                self.username, self.server = webfinger, self._pump.client.server
            if self.username == self._pump.client.nickname and self.server == self._pump.client.server:
                self.inbox = Inbox(self)
            data = self._pump.request("{proto}://{server}/api/user/{username}/profile".format(
                proto=self._pump.protocol,
                server=self.server,
                username=self.username
            ))
            self.unserialize(data)

        self.username = username or self.username
        self.url = url or self.url
        self.summary = summary or self.summary
        self.image = image or self.image
        self.display_name = display_name or self.display_name
        self.published = published or self.published
        self.updated = updated or self.updated
        self.isme = (self.username == self._pump.client.nickname and self.server == self._pump.client.server)

    @property
    def webfinger(self):
        return self.id.replace("acct:", "")

    def follow(self): 
        """ Follow person """
        activity = {
            "verb":"follow",
            "object":{
                "id":self.id,
                "objectType":self.objectType,
            }
        }

        self._post_activity(activity)

    def unfollow(self):
        """ Unfollow person """
        activity = {
            "verb":"stop-following",
            "object":{
                "id":self.id,
                "objectType":self.objectType,
            }
        }

        self._post_activity(activity)

    def update(self):
        """ Updates person object"""
        activity = {
            "verb":"update",
            "object":{
                "id": self.id,
                "objectType": self.objectType,
                "displayName": self.display_name,
                "summary": self.summary,
            }
        }

        self._post_activity(activity)

    def __repr__(self):
        return "<Person: {person}>".format(person=self.id.replace("acct:", ""))

    def __str__(self):
        return self.display_name or self.username or self.webfinger

    def unserialize_service(self, data):
        """ Unserializes the data from a service """
        self.id = data["id"]
        self.display = data["displayName"]
        self.updated = parse(data["updated"]) if "updated" in data else datetime.now()
        self.published = parse(data["published"]) if "published" in data else self.updated
        return self

    def unserialize(self, data):
        """ Goes from JSON -> Person object """
        if data.get("objectType", "") == "service":
            return self.unserialize_service(data)

        self.id = data["id"]
        self.server = self.id.replace("acct:", "").split("@")[-1]
        self.username = data.get("preferredUsername", None)
        self.display_name = data.get("displayName", None)
        self.url = data.get("url", None)
        self.summary = data.get("summary", None)
        self.updated = parse(data["updated"]) if "updated" in data else None
        self.published = parse(data["published"]) if "published" in data else self.updated
        self.updated = parse(data["updated"]) if "updated" in data else self.published
        self.isme = "acct:%s@%s" % (self._pump.client.nickname, self._pump.client.server) == self.id
        self.location = self._pump.Location().unserialize(data["location"]) if "location" in data else None

        return self
