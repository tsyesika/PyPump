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

class AbstractModel(object):

    @property
    def TYPE(self):
        return self.__class__.__name__

    @property
    def objectType(self):
        return self.TYPE.lower()

    _mapping = {
        "objectType":"TYPE",
    }

    _pump = None

    def __init__(self, pypump=None, *args, **kwargs):
        """ Sets up pump instance """
        if pypump:
            self._pump = pypump

    def _post_activity(self, activity):
        """ Posts a activity to feed """
        data = self._pump.request(self.ENDPOINT, method="POST", data=activity)

        if not data:
            return False

        if "error" in data:
            raise PumpException(data["error"])

        self.unserialize(data["object"], obj=self)

        return True

    def serialize(self, *args, **kwargs):
        """ Changes it from obj -> JSON """
        data = {}
        for item in dir(self):
            if item.startswith("_"):
                continue # we don't want
            
            value =  getattr(self, item)
            
            # we need to double check we're not in mapper
            item = self.remap(item)
            data[item] = value

        return json.dumps(data, *args, **kwargs)

    @staticmethod
    def unserialize(self, data, *args, **kwargs):
        """ Changes it from JSON -> obj """
        data = json.loads(data)

        klass = self(pypump=self._pump)

        for key, value in data.items():
            key = self.remap(key)
            if key is None:
                continue

            setattr(klass, key, value)            

        return klass

    def remap(self, data):
        """ Remaps """
        if data in self._mapping.keys():
            return self._mappping[data]
        elif data in self.__mapping.values():
            for k, v in self._mapping.items():
                if data == v:
                    return k

        return data

class Likeable(object):
    """
        Provides the model with the like and unlike methods as well as
        the property likes which will look up who's liked the model instance
        and return you back a list of user objects
    
        must have _links["likes"]
    """

    @property
    def likes(self):
        """ Gets who's liked this object """
        endpoint = self._links["likes"]
        likes = self._pump.request(endpoint, raw=True)
        likes_obj = []
        for l in likes.get("items", likes_obj):
            likes_obj.append(self._pump.Person.unserialize(l))
        
        return likes_obj

    favorites = likes

    def like(self, verb="like"):
        """ Likes the model """
        activity = {
            "verb": verb,
            "object": {
                "id": self.id,
                "objectType": self.objectType,
            }
        }

        self._post_activity(activity)

    def unlike(self, verb="unlike"):
        """ Unlikes the model """
        activity = {
            "verb": verb,
            "object": {
                "id": self.id,
                "objectType": self.objectType,
            }
        }

        self._post_activity(activity)

    def favorite(self):
        """ Favourite model """
        return self.like(verb="favorite")

    def unfavorite(self):
        """ Unfavourite model """
        return self.unlike(verb="unfavorite")

class Commentable(object):
    """
        Provides the model with the comment method allowing you to post
        a comment to on the model. It also provides an ability to read
        comments.

        must have _likes["replies"]
    """

    @property
    def comments(self):
        """ Fetches the comment objects for the models """
        endpoint = self._links["replies"]
        comments = self._pump.request(endpoint, raw=True)
        comments_obj = []
        for c in comments.get("items", comments_obj):
            comments_obj.append(self._pump.Comment.unserialize(c))
        return comments_obj

    def comment(self, comment):
        """ Posts a comment object on model """
        comment.inReplyTo = self
        comment.send()

class Shareable(object):
    """
        Provides the model with the share and unshare methods and shares
        property allowing you to see who's shared the model.

        must have _likes["shares"]
    """

    @property
    def shares(self):
        """ Fetches the people who've shared the model """
        endpoint = self._links["shares"]
        shares = self._pump.request(endpoint, raw=True)
        shares_obj = []
        for p in shares.get("items", shares_obj):
            shares_obj.append(self._pump.Person.unserialize(p))
        return shares_obj

    def share(self):
        """ Shares the model """
        activity = {
            "verb": "share",
            "object": {
                "id": self.id,
                "objectType": self.objectType,
            },
        }

        self._post_activity(activity)

    def unshare(self):
        """ Unshares a previously shared model """
        activity = {
            "verb": "unshare",
            "object": {
                "id": self.id,
                "objectType": self.objectType,
            },
        }

        self._post_activity(activity)

class Deleteable(object):
    """ Provides the model with the ability to be deleted """

    def delete(self):
        """ Delete's a model """
        activity = {
            "verb": "delete",
            "object": {
                "id": self.id,
                "objectType": self.objectType,
            }
        }

        self._post_activity(activity)

