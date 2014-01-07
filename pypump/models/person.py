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
from pypump.exception import PyPumpException
from pypump.models.feed import (Followers, Following, Lists,
                                Favorites, Inbox, Outbox)
from pypump.models.activity import Mapper

class Person(AbstractModel):

    _ignore_attr = []
    _mapping = {
        "id": "id",
        "url": "url",
        "username": "preferredUsername",
        "display_name": "displayName",
        "summary": "summary",
        "updated": "updated",
        "published":"published",
        "location":"location",
    }

    TYPE = "person"
    ENDPOINT = "/api/user/{username}/feed"

    id = None
    username = None
    display_name = None
    url = None # url to profile
    updated = None # Last time this was updated
    published = None # when they joined (I think?)
    location = None # place item
    summary = None # lil bit about them =]    
    image = None # Image items

    _inbox = None
    _outbox = None
    _followers = None
    _following = None
    _favorites = None
    _lists = None

    @property
    def outbox(self):
        self._outbox = self._outbox or Outbox(self.links['activity-outbox'],pypump=self._pump)
        return self._outbox

    @property
    def followers(self):
        self._followers = self._followers or Followers(self.links['followers'],pypump=self._pump)
        return self._followers

    @property
    def following(self):
        self._following = self._following or Following(self.links['following'],pypump=self._pump)
        return self._following

    @property
    def favorites(self):
        self._favorites = self._favorites or Favorites(self.links['favorites'],pypump=self._pump)
        return self._favorites

    @property
    def lists(self):
        self._lists = self._lists or Lists(self.links['lists'],pypump=self._pump)
        return self._lists

    @property
    def inbox(self):
        if not self.isme:
            raise PyPumpException("You can't read other people's inboxes")
        self._inbox = self._inbox or Inbox(self.links['activity-inbox'], pypump=self._pump)
        return self._inbox

    @property
    def webfinger(self):
        return self.id.replace("acct:", "")

    def __init__(self, webfinger=None, id=None, username=None, url=None, summary=None, 
                 display_name=None, image=None, 
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

            self.add_link('self', "{0}://{1}/api/user/{2}/profile".format(
                self._pump.protocol, self.server, self.username)
            )
            data = self._pump.request(self.links['self'])
            self.unserialize(data)

        self.username = username or self.username
        self.url = url or self.url
        self.summary = summary or self.summary
        self.image = image or self.image
        self.display_name = display_name or self.display_name
        self.published = published or self.published
        self.updated = updated or self.updated
        self.isme = (self.username == self._pump.client.nickname and self.server == self._pump.client.server)

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

    def unserialize(self, data):
        """ Goes from JSON -> Person object """

        Mapper(pypump=self._pump).parse_map(self, data=data)
        self.server = self.id.replace("acct:", "").split("@")[-1]
        self.isme = "acct:%s@%s" % (self._pump.client.nickname, self._pump.client.server) == self.id
        self.add_links(data)

        return self
