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
import logging
import six

from pypump.exception.PumpException import PumpException

_log = logging.getLogger(__name__)

class AbstractModel(object):

    links = None

    @property
    def TYPE(self):
        return self.__class__.__name__

    @property
    def objectType(self):
        return self.TYPE.lower()

    _mapping = {
        "objectType":"TYPE",
    }

    def __init__(self, pypump=None, *args, **kwargs):
        """ Sets up pump instance """
        self.links = {}
        if pypump:
            self._pump = pypump

    def _post_activity(self, activity, unserialize=True):
        """ Posts a activity to feed """
        # I think we always want to post to feed
        feed_url = "{proto}://{server}/api/user/{username}/feed".format(
            proto=self._pump.protocol,
            server=self._pump.client.server,
            username=self._pump.client.nickname
        )

        data = self._pump.request(feed_url, method="POST", data=activity)

        if not data:
            return False

        if "error" in data:
            raise PumpException(data["error"])

        if unserialize:
            if "target" in data:
                # we probably want to unserialize target if it's there
                # true for collection.{add,remove}
                self.unserialize(data["target"])
            else:
                self.unserialize(data["object"])

        return True

    def __unicode__(self):
        return six.u(str(self))

    def __str__(self):
        return str(repr(self))

    def __bytes__(self):
        return self.b(str(self))

    def add_link(self, name, link):
        """ Adds a link to the model """

        self.links[name] = link
        return True

    def add_links(self, links, key="href", proxy_key="proxyURL", endpoints=None):
        """ Parses and adds block of links """
        if endpoints is None:
            endpoints = ["likes", "replies", "shares", "self", "followers",
                         "following", "lists", "favorites", "members"]

        if links.get("links"):
            for endpoint in links['links']:
                self.add_link(endpoint, links['links'][endpoint]["href"])

        for endpoint in endpoints:
            if links.get(endpoint, None) is None:
                continue

            if "pump_io" in links[endpoint]:
                self.add_link(endpoint, links[endpoint]["pump_io"][proxy_key])
            elif "url" in links[endpoint]:
                self.add_link(endpoint, links[endpoint]["url"])
            else:
                self.add_link(endpoint, links[endpoint][key])

        return self.links

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

from pypump.models.feed import Feed

class Likeable(object):
    """
        Provides the model with the like and unlike methods as well as
        the property likes which will look up who's liked the model instance
        and return you back a list of user objects
    
        must have links["likes"]
    """

    _likes = None

    @property
    def likes(self):
        """ Gets who's liked this object """
        endpoint = self.links["likes"]
        self._likes = self._likes or Feed(endpoint, pypump=self._pump)
        return self._likes

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
    _comments = None

    @property
    def comments(self):
        """ Fetches the comment objects for the models """
        endpoint = self.links["replies"]
        self._comments = self._comments or Feed(endpoint, pypump=self._pump)
        return self._comments

    def comment(self, comment):
        """ Posts a comment object on model """
        comment.in_reply_to = self
        comment.send()


class Shareable(object):
    """
        Provides the model with the share and unshare methods and shares
        property allowing you to see who's shared the model.

        must have _likes["shares"]
    """
    _shares = None

    @property
    def shares(self):
        """ Fetches the people who've shared the model """
        endpoint = self.links["shares"]
        self._shares = self._shares or Feed(endpoint, pypump=self._pump)
        return self._shares

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

class Postable(object):
    """ Adds methods to set to, cc and soon bcc as well as .send() """
    
    _to = list()
    _cc = list()
    _bto = list()
    _bcc = list()

    def _set_people(self, people):
        """ Sets who the object is sent to """
        if hasattr(people, "objectType"):
            people = [people]
        elif hasattr(people, "__iter__"):
            people = list(people)

        for i, person in enumerate(people):
            if isinstance(person, six.class_types):
                people[i] = person()
            
            if isinstance(people[i], type(self._pump.Person())):
                people[i] = {
                    "id": people[i].id,
                    "objectType": people[i].objectType,
                }
            else:
                # must be a collection
                people[i] = {
                    "id": people[i].id,
                    "objectType": "collection", 
                }

        return people
    # to
    def _get_to(self):
        return self._to

    def _set_to(self, *args, **kwargs):
        self._to = self._set_people(*args, **kwargs)

    to = property(fget=_get_to, fset=_set_to)

    # cc
    def _get_cc(self):
        return self._cc

    def _set_cc(self, *args, **kwargs):
        self._cc = self._set_people(*args, **kwargs)

    cc = property(fget=_get_cc, fset=_set_cc)

    # bto
    def _get_bto(self):
        return self.bto

    def _set_bto(self, *args, **kwargs):
        self._bto = self._set_people(*args, **kwargs)

    bto = property(fget=_get_bto, fset=_set_bto)

    # bcc
    def _get_bcc(self):
        return self.bcc
    def _set_bcc(self, *args, **kwargs):
        self._bcc = self._set_people(*args, **kwargs)

    bcc = property(fget=_get_bcc, fset=_set_bcc)

    def serialize(self, *args, **kwargs):
        # now add the to, cc, bto, bcc
        data = {
            "to": self._to,
            "cc": self._cc,
            "bto": self._bto,
            "bcc": self._bcc,
        }

        return data

    def send(self):
        """ Sends the data to the server """
        data = self.serialize()
        self._post_activity(data)
