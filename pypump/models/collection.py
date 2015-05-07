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
import logging

from pypump.models import (PumpObject, Deleteable)
from pypump.models.feed import Feed

_log = logging.getLogger(__name__)


class Collection(PumpObject, Deleteable):
    """ This object represents a pump.io **collection**, collections have
    a members :class:`Feed <pypump.models.feed.Feed>` and methods for adding
    and removing objects to that feed.

    :param id: (optional) Collection id.

    Example:
        >>> friendlist = pump.me.lists['Friends']
        >>> list(friendlist.members)
        [<Person: alice@example.org>]
        >>> friendlist.add(pump.Person('bob@example.org'))
    """

    object_type = 'collection'
    _ignore_attr = ["in_reply_to"]
    _mapping = {
        "_members": "members"
    }

    def __init__(self, id=None, **kwargs):
        super(Collection, self).__init__(**kwargs)

        self.id = id

    @property
    def members(self):
        """ :class:`Feed <pypump.models.feed.Feed>` of collection members.
        """
        self._members = self._members or Feed(self.links["members"], pypump=self._pump)
        return self._members

    def add(self, obj):
        """ Adds a member to the collection.

        :param obj: Object to add.

        Example:
            >>> mycollection.add(pump.Person('bob@example.org'))
        """
        activity = {
            "verb": "add",
            "object": {
                "objectType": obj.object_type,
                "id": obj.id
            },
            "target": {
                "objectType": self.object_type,
                "id": self.id
            }
        }

        self._post_activity(activity)

        # Remove the cash so it's re-generated next time it's needed
        self._members = None

    def remove(self, obj):
        """ Removes a member from the collection.

        :param obj: Object to remove.

        Example:
            >>> mycollection.remove(pump.Person('bob@example.org'))
        """
        activity = {
            "verb": "remove",
            "object": {
                "objectType": obj.object_type,
                "id": obj.id
            },
            "target": {
                "objectType": self.object_type,
                "id": self.id
            }
        }

        self._post_activity(activity)

        # Remove the cash so it's re-generated next time it's needed
        self._members = None

    def __unicode__(self):
        return u'{0}'.format(self.display_name or self.id)

    def __repr__(self):
        return "<{type}: {id}>".format(type=self.object_type.capitalize(),
                                       id=self.id)


class Public(PumpObject):

    def __init__(self):
        self.id = "http://activityschema.org/collection/public"
        self.object_type = 'collection'
