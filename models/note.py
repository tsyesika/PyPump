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

from models import AbstractModel

class Note(AbstractModel):
    
    TYPE = "note"
    VERB = "post"
    TSFORMAT = "%Y-%m-%dT%H:%M:%SZ"

    content = ""
    actor = None # who posted.
    updated = None # last time this was updated
    published = None # When this was published

    # where to?
    to = []
    cc = []
    likes = []

    def __init__(self, content, to, actor, published=None, updated=None, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)

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

    def send(self):
        """ Sends the post to the server """
        # post it!
        self.pump.request(self.ENDPOINT, method="POST", data=self.serialize())
    
    def comment(self, comment):
        """ Posts a comment """
        # get self.id?
        comment.send()

    def delete(self):
        """ Delete's the note """
        pass

    def like(self):
        """ Likes the Note """
        pass    

    def unlike(self):
        """ Unlikes the Note """
        pass

    # synonyms
    def favorite(self, *args, **kwargs):
        """ Maps to like """
        return self.like(*args, **kwargs)

    def unfavorite(self, *args, **kwargs):
        """ Maps to unlike """
        return self.unlike(*args, **kwargs)


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

    @staticmethod
    def unserialize(self, data):
        """ Goes from JSON -> Note object """
        query = json.loads(data)
        return Note(
            content=data["content"],
            to=data["to"], # todo: convert to person objects
            #cc=data["cc"],
            actor=data["author"]["preferredUsername"],
            pypump=self.pump,
            updated=datetime.strptime(data["updated"], self.TSFORMAT),
            published=datetime.strptime(data["published"], self.TSFORMAT),
        )
