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

from pypump.models import (PumpObject, Postable, Likeable, Shareable,
                           Commentable, Deleteable)


class Note(PumpObject, Postable, Likeable, Shareable, Commentable, Deleteable):
    """ This object represents a pump.io **note**,
    notes are used to post text (or html) messages to the pump.io network.

    :param content: (optional) Note content.
    :param display_name: (optional) Note title.

    Usage::

        >>> mynote = pump.Note(content='<b>Hello</b> world!')
        >>> mynote.send()

    """

    object_type = 'note'
    _ignore_attr = ["summary"]
    _mapping = {}

    def __init__(self,
                 content=None,
                 display_name=None,
                 **kwargs):

        super(Note, self).__init__(**kwargs)

        self.content = content
        self.display_name = display_name

    def serialize(self):
        """ Converts the post to JSON """
        data = super(Note, self).serialize()
        data.update({
            "verb": "post",
            "object": {
                "objectType": self.object_type,
                "content": self.content,
            }
        })
        if self.display_name:
            data["object"]["displayName"] = self.display_name

        return data

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
