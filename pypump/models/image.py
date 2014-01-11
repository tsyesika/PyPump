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
import mimetypes
import os

from dateutil.parser import parse

from pypump.models import (AbstractModel, Postable, Likeable, Commentable,
                           Deleteable, Shareable)
from pypump.models.activity import Mapper

_log = logging.getLogger(__name__)

class ImageContainer(object):
    """ Container to hold about a specific image """
    def __init__(self, url, width, height):
        self.url = url
        self.width = width
        self.height = height

    def __repr__(self):
        return "<Image {width}x{height}".format(
            width=self.width,
            height=self.height
        )

class Image(AbstractModel, Postable, Likeable, Shareable, Commentable, Deleteable):

    _ignore_attr = []
    _mapping = {
        "id": "id",
        "url": "url",
        "display_name": "displayName",
        "summary": "summary",
        "content": "content",
        "author": "author",
        "published": "published",
        "updated": "updated",
        "deleted": "deleted",
    }

    id = None
    url = None
    display_name = None
    summary = None
    content = None
    author = None
    published = None
    updated = None
    deleted = None

    @property
    def ENDPOINT(self):
        return "/api/user/{username}/feed".format(self._pump.client.nickname)

    def __init__(self, id=None, url=None, display_name=None, content=None, 
                 author=None, published=None, updated=None, *args, **kwargs):

        super(Image, self).__init__(*args, **kwargs)

        self.id = id
        self.display_name = display_name
        self.content = content
        self.author = author
        self.url = url
        self.published = published
        self.updated = updated

    def __repr__(self):
        if self.author is None:
            return "<{type}>".format(type=self.TYPE)

        return "<{type} by {webfinger}>".format(
            type=self.TYPE,
            webfinger=self.author.webfinger)

    def from_file(self, filename):
        """ Uploads an image from a filename """
        mimetype = mimetypes.guess_type(filename)[0] or "application/octal-stream"
        headers = {
            "Content-Type": mimetype,
            "Content-Length": os.path.getsize(filename),
        }
        
        # upload image file
        image = self._pump.request(
                "/api/user/{0}/uploads".format(self._pump.client.nickname),
                method="POST",
                data=open(filename, "rb").read(),
                headers=headers,
                )

        # now send it to the feed
        data = {
            "verb": "post",
            "object": image,
        }
        data.update(self.serialize())

        if not self.content and not self.display_name:
            self._post_activity(data)
        else:
            self._post_activity(data, unserialize=False)

            # update image with display_name and content
            if self.content:
                image['content'] = self.content
            if self.display_name:
                image['displayName'] = self.display_name
            data = {
                "verb": "update",
                "object": image,
            }
            self._post_activity(data)

        return self

    def unserialize(self, data):

        if "fullImage" in data:
            full_image = data["fullImage"]
            self.original = ImageContainer(
                url=full_image["url"],
                height=full_image.get("height"),
                width=full_image.get("width")
            )
            
        if "image" in data:
            save_point = "original" if not hasattr(self, "original") else "thumbnail"
            thumbnail = data["image"]
            setattr(self, save_point, ImageContainer(
                url=thumbnail["url"],
                height=thumbnail.get("height"),
                width=thumbnail.get("width")
            ))
        Mapper(pypump=self._pump).parse_map(self, data=data)
        self.add_links(data)

        return self
