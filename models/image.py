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

from models import AbstractModel

class Image(AbstractModel):
    
    TYPE = "image"

    # we need some methods to go grab the image for us.
    _full_url = ""
    _thumb_url = ""

    def __init__(self, full_url, thumb_url=None, width=None, height=None, *args, **kwargs):
        super(Image, self).__init__(self, *args, **kwargs)

        self._full_url = full_url
        self._thumb_url = full_url if thumb_url is None else thumb_url

        self.width = width
        self.height = height

    def __repr__(self):
        return "<Image at %s>" % self.url

    def __str__(self):
        return self.__repr__()

    def __get_full_url(self):
        if type(self._full_url) == self:
            return self._full_url.full_url
        
        return self._full_url

    full_url = property(__get_full_url)
    url = full_url

    def __get_thumb_url(self):
        if type(self._thumb_url) == self:
            return self._thumb_url.thumb_url
        
        return self._thumb_url
    
    thumb_url = property(__get_thumb_url)

    @staticmethod
    def unserialize(data, obj=None):
        full_url = None

        if "fullImage" in data:
            full_obj = data["fullImage"]
            full_url = Image.unsrialize(full_obj)
        
        if "image" in data:
            data = data["image"]
        
        url = data["url"]
        width = data["width"] if "width" in data else None
        height = data["height"] if "height" in data else None

        full_url = url if full_url is None else full_url

        if obj is None:
            return Image(full_url=full_url, thumb_url=url, height=height, width=width)
        else:
            obj._full_url = full_url
            obj._thumb_url = url
            obj.height = height
            obj.width = width
            return obj

