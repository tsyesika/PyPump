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
                           Deleteable, Uploadable, Mapper)

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

    def _get_fileurl(self, data):
        if data.get("pump_io", {}).get("proxyURL"):
            return data["pump_io"]["proxyURL"]
        else:
            return data["url"]

    def unserialize(self, data):
        if "stream" in data:
            stream = data["stream"]
            self.stream = StreamContainer(
                url=self._get_fileurl(stream)
            )
        Mapper(pypump=self._pump).parse_map(self, data=data)
        self._add_links(data)
        return self


class StreamContainer(object):
    """ Container that holds information about a stream.

    :param url: URL to the file on the pump.io server.
    """
    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "<Stream: {url}>".format(url=self.url)


class Video(MediaObject):
    """ This object represents a pump.io **video** object,
    video objects are used to post video content with optional text (or html) messages
    to the pump.io network.

    :param content: (optional) Video text content.
    :param display_name: (optional) Video title.

    Example:
        >>> myogv = pump.Video(display_name='Happy Caturday!')
        >>> myogv.from_file('/path/to/kitteh.ogv')
    """

    object_type = 'video'


class Audio(MediaObject):
    """ This object represents a pump.io **audio** object,
    audio objects are used to post audio content with optional text (or html) messages
    to the pump.io network.

    :param content: (optional) Audio text content.
    :param display_name: (optional) Audio title.

    Example:
        >>> myogg = pump.Audio(display_name='Happy Caturday!')
        >>> myogg.from_file('/path/to/kitteh.ogg')
    """

    object_type = 'audio'


class ImageContainer(object):
    """ Container that holds information about an image.

    :param url: URL to image file on the pump.io server.
    :param width: Width of the image.
    :param height: Height of the image.
    """
    def __init__(self, url, width, height):
        self.url = url
        self.width = width
        self.height = height

    def __repr__(self):
        return "<Image {width}x{height}>".format(
            width=self.width,
            height=self.height
        )


class Image(MediaObject):
    """ This object represents a pump.io **image**,
    images are used to post image content with optional text (or html) messages
    to the pump.io network.

    :param content: (optional) Image text content.
    :param display_name: (optional) Image title.

    Example:
        >>> myimage = pump.Image(display_name='Happy Caturday!')
        >>> myimage.from_file('/path/to/kitteh.png')
    """

    object_type = 'image'
    _ignore_attr = ["summary", "image"]
    _mapping = {
        "thumbnail": "image",
        "original": "fullImage",
        "license": "license",
    }

    def unserialize(self, data):
        if "image" in data:
            thumbnail = data["image"]
            self.thumbnail = ImageContainer(
                url=self._get_fileurl(thumbnail),
                height=thumbnail.get("height"),
                width=thumbnail.get("width")
            )

        if "fullImage" in data:
            full_image = data["fullImage"]
            self.original = ImageContainer(
                url=self._get_fileurl(full_image),
                height=full_image.get("height"),
                width=full_image.get("width")
            )
        else:
            self.original = self.thumbnail

        Mapper(pypump=self._pump).parse_map(self, data=data)
        self._add_links(data)

        return self
