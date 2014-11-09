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

from pypump.models import PumpObject, Addressable
from pypump.exception import PyPumpException
from pypump.models.feed import (Followers, Following, Lists,
                                Favorites, Inbox, Outbox)


class Person(PumpObject, Addressable):
    """ This object represents a pump.io **person**,
    a person is a user on the pump.io network.

    :param webfinger: User ID in ``nickname@hostname`` format.

    Example:
        >>> alice = pump.Person('alice@example.org')
        >>> print(alice.summary)
        Hi, I'm Alice
        >>> mynote = pump.Note('Hey Alice, it's Bob!')
        >>> mynote.to = alice
        >>> mynote.send()
    """

    object_type = 'person'
    _ignore_attr = ['liked', 'in_reply_to']
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
        """ :class:`Outbox feed <pypump.models.feed.Outbox>` with all
        :class:`activities <pypump.models.activity.Activity>` sent by the person.

        Example:
            >>> for activity in pump.me.outbox[:2]:
            ...     print(activity)
            ...
            pypumptest2 unliked a comment in reply to a note
            pypumptest2 deleted a note
        """
        self._outbox = self._outbox or Outbox(self.links['activity-outbox'], pypump=self._pump)
        return self._outbox

    @property
    def followers(self):
        """ :class:`Feed <pypump.models.feed.Feed>` with all
        :class:`Person <pypump.models.person.Person>` objects following the person.

        Example:
            >>> alice = pump.Person('alice@example.org')
            >>> for follower in alice.followers[:2]:
            ...     print(follower.id)
            ...
            acct:bob@example.org
            acct:carol@example.org
        """
        self._followers = self._followers or Followers(self.links['followers'], pypump=self._pump)
        return self._followers

    @property
    def following(self):
        """ :class:`Feed <pypump.models.feed.Feed>` with all
        :class:`Person <pypump.models.person.Person>` objects followed by the person.

        Example:
            >>> bob = pump.Person('bob@example.org')
            >>> for followee in bob.following[:3]:
            ...     print(followee.id)
            ...
            acct:alice@example.org
            acct:duncan@example.org
        """
        self._following = self._following or Following(self.links['following'], pypump=self._pump)
        return self._following

    @property
    def favorites(self):
        """ :class:`Feed <pypump.models.feed.Feed>` with all objects
        liked/favorited by the person.

        Example:
            >>> for like in pump.me.favorites[:3]:
            ...     print(like)
            ...
            note by alice@example.org
            image by bob@example.org
            comment by evan@e14n.com
        """
        self._favorites = self._favorites or Favorites(self.links['favorites'], pypump=self._pump)
        return self._favorites

    @property
    def lists(self):
        """ :class:`Lists feed <pypump.models.feed.Lists>` with all lists
        owned by the person.

        Example:
            >>> for list in pump.me.lists:
            ...     print(list)
            ...
            Acquaintances
            Family
            Coworkers
            Friends
        """
        self._lists = self._lists or Lists(self.links['lists'], pypump=self._pump)
        return self._lists

    @property
    def inbox(self):
        """ :class:`Inbox feed <pypump.models.feed.Inbox>` with all
        :class:`activities <pypump.models.activity.Activity>`
        received by the person, can only be read if logged in as the owner.

        Example:
            >>> for activity in pump.me.inbox[:2]:
            ...     print(activity.id)
            ...
            https://microca.st/api/activity/BvqXQOwXShSey1HxYuJQBQ
            https://pumpyourself.com/api/activity/iQGdnz5-T-auXnbUUdXh-A
        """
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

    def __init__(self, webfinger=None, **kwargs):
        super(Person, self).__init__(**kwargs)

        if isinstance(webfinger, six.string_types):
            if "@" not in webfinger:  # TODO do better validation
                raise PyPumpException("Not a valid webfinger: %s" % webfinger)

            self.id = "acct:{0}".format(webfinger)
            self.username = webfinger.split("@")[0]

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
            "verb": verb,
            "object": {
                "id": self.id,
                "objectType": self.object_type,
                "displayName": self.display_name,
                "summary": self.summary,
            }
        })

        return data

    def follow(self):
        """ Follow person """
        self._verb('follow')

    def unfollow(self):
        """ Unfollow person """
        self._verb('stop-following')

    def update(self):
        # TODO update location
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
