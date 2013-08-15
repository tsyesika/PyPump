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

from pypump.compatability import *
from pypump.models.feed import Feed

class Inbox(Feed):

    OBJECT_TYPES = "Activity"
    
    @property
    def ENDPOINT(self):
        if self._ENDPOINT:
            return self._ENDPOINT
        
        self._ENDPOINT = "api/user/{username}/inbox".format(username=self.actor.username)
        return self.ENDPOINT
