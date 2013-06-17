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

import json
from datetime import datetime

class Note(object):
    
    TYPE = "note"
    VERB = "post"
    pump = None

    content = ""
    actor = None # who posted.
    updated = None # last time this was updated
    published = None # When this was published

    # where to?
    to = []
    cc = []
    likes = []

    def __init__(self, content, to, actor, published=None, updated=None):
        self.content = content
        self.to = to
        self.actor = actor

        if published:
            self.published = published
        else:
            self.published = datetime.now()

        if updated:
            self.updated = updated
        else:
            self.updated = self.published

        # post it!
        self.pump.request(self.ENDPOINT, method="POST", data=self.serialize())
    
    def comment(self, comment):
        """ Posts a comment """
        pass

    def delete(self):
        """ Delete's the note """
        pass

    def like(self):
        """ Likes the Note """
        pass

    def __repr__(self):
        return self.content
   
    def __str__(self):
        return self.__repr__()

    def serialize(self):
        """ Seralizes note to be posted """
        query = {
            "verb":self.VERB,
            "object":{
                "objectType":self.TYPE,
                "content":self.content,
            },
        }

        return json.dumps(query)
