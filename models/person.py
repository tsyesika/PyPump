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

from datetime import datetime

from models import AbstractModel

class Person(AbstractModel):

    _mapping = {
        "preferredUsername":"username",
        "displayName":"display_name",
    }


    TYPE = "person"

    id = ""
    username = ""
    display_name = ""
    url = "" # url to profile
    updated = None # Last time this was updated
    published = None # when they joined (I think?)
    location = None # place item
    summary = "" # lil bit about them =]    
    image = None # Image items

    is_self = False # is this you?

    def __init__(self, id="", username="", url="", summary="", 
                 display_name="", image=None, published=None, 
                 updated=None, location=None, me=None, *args, **kwargs):
        """
        id - the ID of the person. e.g. acct:Username@server.example
        username - persons username
        url - url to profile
        summary - summary of the user
        display_name - what the user want's to show up (defualt: username)
        image - image of the user (default: No image/None)
        published - when the user joined pump (default: now)
        updated - when the user last updated their profile (default: published)
        location - where the user resides (default: No location/None)
        me - you, used to set is_self, if not given it assumes this person _isn't_ you
        """
        super(Person, self).__init__(*args, **kwargs)

        self.id = id
        self.username = username
        self.url = url
        self.summary = summary
        self.image = image        

        if display_name:
            self.display_name = display_name
        else:
            self.display_name = self.username

        if published:
            self.published = published
        else:
            self.published = datetime.now()
        
        if updated:
            self.updated = updated
        else:
            self.updated = self.published

        if me and self.id == me.id:
            self.is_self = True

    def follow(self): 
        """ You follow this user """
        pass

    def unfollow(self):
        """ Unfollow a user """
        pass

    def __repr__(self):
        return self.id.lstrip("acct:")

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def unserialize(data, obj=None):
        """ Goes from JSON -> Person object """
        self = Person() if obj is None else obj
        
        username = data["preferredUsername"]
        display = data["displayName"]

        self.id = "acct:%s@%s" % (username, self._pump.server)
        self.username = username
        self.display_name = display
        self.url = data["links"]["self"]["href"]
        self.summary = data["summary"]
        self.updated = datetime.strptime(data["updated"], self.TSFORMAT)
        self.published = datetime.strptime(data["published"], self.TSFORMAT) if "published" in data else self.updated
        self.me = True if "acct:%s@%s" % (self._pump.nickname, self._pump.server) == self.id else False
        self.location = self._pump.Location.unserialize(data["location"])

        return self
