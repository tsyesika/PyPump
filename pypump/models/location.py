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

    TYPE = "location"

    name = ""

    def __init__(self, name, *args, **kwargs):
        super(Location, self).__init__(*args, **kwargs)
        self.name = name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def unserialize(data, obj=None):
        name = data["displayName"]
        if obj is None:
            return Location(name=name)
        else:
            obj.name = name
            return obj

    # more will come later, I'm thinking hooks with OSM?
