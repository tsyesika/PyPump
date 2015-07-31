##
# Copyright (C) 2015 Jessica T. (Tsyesika) <xray7224@googlemail.com>
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
from pypump.models import (PumpObject, Likeable, Shareable, Commentable,
                           Deleteable, Uploadable)

_log = logging.getLogger(__name__)


class MediaObject(PumpObject, Likeable, Shareable, Commentable, Deleteable, Uploadable):

    object_type = 'dummy'
    _ignore_attr = ["summary"]
    _mapping = {
        "stream": "stream",
        "license": "license",
        "embed_code": "embedCode",
    }

    def __init__(self, display_name=None, content=None, license=None, **kwargs):
        super(MediaObject, self).__init__(**kwargs)

        self.display_name = display_name
        self.content = content
        self.license = license

    def __repr__(self):
        return "<{type} by {webfinger}>".format(
            type=self.object_type.capitalize(),
            webfinger=getattr(self.author, 'webfinger', 'unknown')
        )

    def __unicode__(self):
        return u"{type} by {webfinger}".format(
            type=self.object_type,
            webfinger=getattr(self.author, 'webfinger', 'unknown')
        )


class Video(MediaObject):

    object_type = 'video'


class Audio(MediaObject):

    object_type = 'audio'
