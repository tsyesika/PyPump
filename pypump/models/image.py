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
import datetime
from dateutil.parser import parse

from pypump.compatability import *
from pypump.models import (AbstractModel, Likeable, Commentable, Deleteable,
                           Shareable)

@implement_to_string
class Image(AbstractModel, Likeable, Shareable, Commentable, Deleteable):
    
    url = None
    actor = None
    author = actor
    summary = ""
    id = None
    updated = None
    published = None
    _links = None

    @property
    def ENDPOINT(self):
        return "/api/user/{username}/feed".format(self._pump.nickname)

    def __init__(self, id, url, content=None, actor=None, width=None, height=None,
                 published=None, updated=None, links=None, *args, **kwargs):
        super(Image, self).__init__(self, *args, **kwargs)

        self.id = id
        self.content = content
        self.actor = self.actor if actor is None else actor
        self.url = url
        self.published = published
        self.updated = updated
        self._links = dict() if links is None else links

    def __repr__(self):
        return "<{type} by {webfinger}>".format(
            type=self.TYPE,
            url=self.actor.webfinger)

    def __str__(self):
        return str(repr(self))

    @classmethod
    def unserialize(cls, data, obj=None):
        image_id = data["id"]
        if "fullImage" in data:
            full_image = data["fullImage"]["url"]
            full_image = cls(id=image_id, url=full_image)
        else:
            full_image = None

        if "image" in data:
            image = data["image"]["url"]
            image = cls(id=image_id, url=image)
        else:
            image = None

        author = cls._pump.Person.unserialize(data["author"])

        links = dict()
        for i in ["likes", "replies", "shares"]:
            if data.get(i, None):
                if "pump_io" in data[i]:
                    links[i] = data[i]["pump_io"]["proxyURL"]
                else:
                    links[i] = data[i]["url"]

        for i in [full_image, image]:
            i.actor = author
            i.published = parse(data["published"])
            i.updated = parse(data["updated"])
            i.display_name = data.get("displayName", str())

        # set the full and normal image on each one
        full_image.image = image
        full_image.original = full_image

        image.image = image
        image.original = full_image

        # and finally the links
        full_image._links = links
        image._links = links

        return image 
