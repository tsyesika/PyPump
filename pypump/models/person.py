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

from pypump.models import PumpObject, Mapper, Addressable
from pypump.exception import PyPumpException
from pypump.models.feed import (Followers, Following, Lists,
                                Favorites, Inbox, Outbox)

class Person(PumpObject, Addressable):

    object_type = 'person'
    _ignore_attr = ['liked','in_reply_to']
    _mapping = {
        "username": "preferredUsername",
        "location":"location",
    }

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

    @property
    def server(self):
        return self.id.split("@")[-1]

    @property
    def isme(self):
        return (self.username == self._pump.client.nickname and self.server == self._pump.client.server)

    def __init__(self, webfinger=None, summary=None, username=None,
                 display_name=None, image=None, location=None,
                 *args, **kwargs):
        """
        webfinger - user@host.tld
        summary - summary of the user
        username - persons username
        display_name - what the user want's to show up (default: username)
        image - image of the user (default: No image/None)
        location - where the user resides (default: No location/None)
        """
        super(Person, self).__init__(*args, **kwargs)
        #do empty unserialize to add all attributes
        self.unserialize({'objectType':self.object_type})

        if isinstance(webfinger, six.string_types):
            if "@" in webfinger:
                # webfinger is being used
                self.id = "acct:{0}".format(webfinger)
                self.username = username or webfinger.split("@")[0]
            else:
                # webfinger looks like a username, we assume the user is on our server
                self.username = webfinger
                self.id = "acct:{0}@{1}".format(self.username, self._pump.client.server)

            self.summary = summary
            self.display_name = display_name
            self.image = image #TODO set proper image object
            self.location = location #TODO set proper Place object

            self._add_link('self', "{0}://{1}/api/user/{2}/profile".format(
                self._pump.protocol, self.server, self.username)
            )
            try:
                data = self._pump.request(self.links['self'])
                self.unserialize(data)
            except:
                pass

    def serialize(self, verb):
        data = super(Person, self).serialize()
        data.update({
            "verb":verb,
            "object":{
                "id":self.id,
                "objectType":self.object_type,
                "displayName": self.display_name,
                "summary": self.summary,
            }
        })

        return data

    def follow(self): 
        """ Follow person """
        data = self.serialize(verb="follow")
        self._post_activity(data)

    def unfollow(self):
        """ Unfollow person """
        data = self.serialize(verb="stop-following")
        self._post_activity(data)

    def update(self):
        #TODO update location
        """ Updates person object"""
        data = self.serialize(verb="update")
        self._post_activity(data)

    def __repr__(self):
        return "<{type}: {webfinger}>".format(
            type=self.object_type.capitalize(),
            webfinger=getattr(self, 'webfinger', 'unknown')
        )

    def __unicode__(self):
        return u"{0}".format(self.display_name or self.username or self.webfinger)

    def unserialize(self, data):
        """ Goes from JSON -> Person object """

        Mapper(pypump=self._pump).parse_map(self, data=data)
        self._add_links(data)

        return self
