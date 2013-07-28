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

from pypump.models import AbstractModel
from pypump.compatability import *

@implement_to_string
class Location(AbstractModel):

    name = None
    longitude = None
    latitude = None

    def __init__(self, name, longitude, latitude, *args, **kwargs):
        super(Location, self).__init__(*args, **kwargs)
        self.name = name
        self.longitude = longitude
        self.latitude = latitude

    def __repr__(self):
        return "<{type} {name}>".format(type=self.TYPE, name=self.name)

    def __str__(self):
        return str(self.__repr__())

    @classmethod
    def unserialize(cls, data, obj=None):
        name = data.get("displayName", None)
        
        if ("lon" in data and "lat" in data):
            longitude = float(data["lon"])
            latitude = float(data["lat"])
        
        elif "position" in data:
            position = data["position"][:-1]
            if position[1:].find("+") != -1:
                latitude = position.lstrip("+").split("+", 1)[0]
                latitude = float(latitude)

                longitude = float(position[1:].split("+", 1)[1])
            else:
                latitude = position.lstrip("+").split("-", 1)[0]
                latitude = float(latitude)

                longitude = float(position[1:].split("-", 1)[1])               

        else:
            longitude = None
            latitude = None

        if obj is None:
            return cls(name=name, longitude=longitude, latitude=latitude)
        else:
            obj.name = name
            obj.longitude = longitude
            obj.latitude = latitude
            return obj
