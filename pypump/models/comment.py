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

from pypump.models import (PumpObject, Commentable, Likeable, Shareable,
                           Deleteable, Postable)


class Comment(PumpObject, Likeable, Shareable, Deleteable, Commentable, Postable):
    """ This object represents a pump.io **comment**,
    comments are used to post text (or html) messages in reply to other objects on the pump.io network.

    :param content: (optional) Comment content.
    :param in_reply_to: (optional) Object to reply to.

    Example:
        >>> catpic
        <Image by alice@example.org>
        >>> mycomment = pump.Comment(content='Best cat pic ever!', in_reply_to=catpic)
        >>> mycomment.send()

    """

    object_type = 'comment'
    _ignore_attr = ["summary"]
    _mapping = {}

    def __init__(self, content=None, in_reply_to=None, **kwargs):

        super(Comment, self).__init__(**kwargs)

        self.content = content
        self.in_reply_to = in_reply_to

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

    def serialize(self):
        data = super(Comment, self).serialize()
        data.update({
            "verb": "post",
            "object": {
                "objectType": self.object_type,
                "content": self.content,
                "inReplyTo": {
                    "id": self.in_reply_to.id,
                    "objectType": self.in_reply_to.object_type,
                },
            },
        })

        return data
