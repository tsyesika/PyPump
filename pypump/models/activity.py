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

from pypump.models import PumpObject, Mapper, Addressable

import logging

_log = logging.getLogger(__name__)


class Application(PumpObject):
    _ignore_attr = ["likes", "replies", "shares", "author", "content",
                    "in_reply_to", "liked", "summary"]
    _mapping = {}

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)


class Activity(PumpObject, Addressable):
    _ignore_attr = ["author", "deleted", "display_name", "in_reply_to",
                    "liked", "summary"]

    _mapping = {
        "verb": "verb",
        "generator": "generator",
        "received": "received",
        "actor": "actor",
        "obj": "object",
    }

    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Activity: {webfinger} {verb}ed {model}>'.format(
            webfinger=self.actor.id.replace("acct:", ""),
            verb=self.verb.rstrip("e"),  # english: e + ed = ed
            model=self.obj.object_type
        )

    def __unicode__(self):
        return u'{0}'.format(self._striptags(self.content))

    def unserialize(self, data):
        """ From JSON -> Activity object """

        # copy activity attributes into object
        if "author" not in data["object"]:
            data["object"]["author"] = data["actor"]
        for key in ["to", "cc", "bto", "bcc"]:
            if key not in data["object"] and key in data:
                data["object"][key] = data[key]

        Mapper(pypump=self._pump).parse_map(self, data=data)
        self._add_links(data)

        return self
