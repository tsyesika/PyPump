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

import logging
import re
import six

from dateutil.parser import parse

from pypump.exception.PumpException import PumpException

_log = logging.getLogger(__name__)


class PumpObject(object):

    _ignore_attr = list()

    _mapping = {
        "attachments": "attachments",
        "author": "author",
        "content": "content",
        "display_name": "displayName",
        "downstream_duplicates": "downstreamDuplicates",
        "id": "id",
        "image": "image",
        "in_reply_to": "inReplyTo",
        "liked": "liked",
        "links": "links",
        "published": "published",
        "summary": "summary",
        "updated": "updated",
        "upstream_duplicates": "upstreamDuplicates",
        "url": "url",
        "deleted": "deleted",
        "object_type": "objectType",
        "_to": "to",
        "_cc": "cc",
        "_bto": "bto",
        "_bcc": "bcc",
        "_comments": "replies",
        "_followers": "followers",
        "_following": "following",
        "_likes": "likes",
        "_shares": "shares",
    }

    def __init__(self, pypump=None, *args, **kwargs):
        """ Sets up pump instance """
        self.links = {}
        if pypump:
            self._pump = pypump

        # combine mapping of self and PumpObject
        mapping = PumpObject._mapping.copy()
        mapping.update(self._mapping)
        self._mapping = mapping

        # remove unwanted attributes from mapping
        for i in self._ignore_attr:
            if self._mapping.get(i):
                del self._mapping[i]

        # add any missing attributes
        for key in self._mapping.keys():
            if not hasattr(self, key):
                setattr(self, key, None)

    def _verb(self, verb):
        """ Posts minimal activity with verb and bare self object.
        :param verb: verb to be used.
        """

        activity = {
            "verb": verb,
            "object": {
                "id": self.id,
                "objectType": self.object_type,
            }
        }

        self._post_activity(activity)

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
                # copy activity attributes into object
                if "author" not in data["object"]:
                    data["object"]["author"] = data["actor"]
                for key in ["to", "cc", "bto", "bcc"]:
                    if key not in data["object"] and key in data:
                        data["object"][key] = data[key]

                self.unserialize(data["object"])

        return True

    def __unicode__(self):
        if self.display_name is not None:
            return u'{name}'.format(name=self.display_name)
        else:
            return u'{type}'.format(type=self.object_type)

    if six.PY3:
        def __str__(self):
            return self.__unicode__()
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

    def _striptags(self, html):
        return re.sub(r'<[^>]+>', '', html)

    def _add_link(self, name, link):
        """ Adds a link to the model """

        self.links[name] = link
        return True

    def _add_links(self, links, key="href", proxy_key="proxyURL", endpoints=None):
        """ Parses and adds block of links """
        if endpoints is None:
            endpoints = ["likes", "replies", "shares", "self", "followers",
                         "following", "lists", "favorites", "members"]

        if links.get("links"):
            for endpoint in links['links']:
                # It would seem occasionally the links["links"][endpoint] is
                # just a string (what would be the href value). I don't know
                # why, it's likely a bug in pump.io but for now we'll support
                # this too.
                if isinstance(links['links'][endpoint], dict):
                    self._add_link(endpoint, links['links'][endpoint]["href"])
                else:
                    self._add_link(endpoint, links["links"][endpoint])

        for endpoint in endpoints:
            if links.get(endpoint, None) is None:
                continue

            if "pump_io" in links[endpoint]:
                self._add_link(endpoint, links[endpoint]["pump_io"][proxy_key])
            elif "url" in links[endpoint]:
                self._add_link(endpoint, links[endpoint]["url"])
            else:
                self._add_link(endpoint, links[endpoint][key])

        return self.links

    def unserialize(self, data):
        Mapper(pypump=self._pump).parse_map(self,
                                            mapping=self._mapping,
                                            data=data)
        self._add_links(data)
        return self


class Mapper(object):

    """ Handles mapping of json attributes to models """

    # TODO probably better to move this into the models,
    # {"json_attr":("model_attr", "datatype"), .. } or similar
    literals = ["content", "display_name", "id", "object_type", "summary",
                "url", "preferred_username", "verb", "username",
                "total_items", "liked"]
    dates = ["updated", "published", "deleted", "received"]
    objects = ["generator", "actor", "obj", "author", "in_reply_to",
               "location"]
    lists = ["_to", "_cc", "_bto", "_bcc", "object_types", "_items"]
    feeds = ["_comments", "_followers", "_following", "_likes", "_shares"]

    def __init__(self, pypump=None, *args, **kwargs):
        self._pump = pypump

    def parse_map(self, obj, mapping=None, *args, **kwargs):
        """ Parses a dictionary of (model_attr, json_attr) items """
        mapping = mapping or obj._mapping

        if "data" in kwargs:
            for k, v in mapping.items():
                if kwargs["data"].get(v, None) is not None:
                    val = kwargs["data"][v]
                else:
                    val = None
                self.add_attr(obj, k, val, from_json=True)
        else:
            for k, v in mapping.items():
                if k in kwargs:
                    self.add_attr(obj, k, kwargs[k])

    def add_attr(self, obj, key, data, from_json=False):
        if key in self.objects:
            self.set_object(obj, key, data, from_json)
        elif key in self.dates:
            self.set_date(obj, key, data, from_json)
        elif key in self.lists:
            self.set_list(obj, key, data, from_json)
        elif key in self.literals:
            self.set_literal(obj, key, data, from_json)
        elif key in self.feeds:
            self.set_feed(obj, key, data, from_json)
        else:
            _log.debug("Ignoring unknown attribute %r", key)

    def set_literal(self, obj, key, data, from_json):
        if data is not None:
            setattr(obj, key, data)
        else:
            setattr(obj, key, None)

    def get_object(self, data):
        try:
            # Look for suitable PyPump model based on objectType
            obj_type = data.get("objectType").capitalize()
            obj = getattr(self._pump, obj_type)
            obj = obj().unserialize(data)
            _log.debug("Created PyPump model %r" % obj.__class__)
            return obj
        except AttributeError as e:
            _log.debug("Exception: %s" % e)
            try:
                import pypump.models.activity
                # Look for suitable pumpobject model based on objectType
                obj_type = data.get("objectType").capitalize()
                obj = getattr(pypump.models.activity, obj_type)
                obj = obj(pypump=self._pump).unserialize(data)
                _log.debug("Created activity.* model: %r" % obj.__class__)
                return obj
            except AttributeError as e:
                # Fall back to PumpObject
                _log.debug("Exception: %s" % e)
                obj = PumpObject(pypump=self._pump).unserialize(data)
                _log.debug("Created PumpObject: %r" % obj.object_type)
                return obj

    def set_object(self, obj, key, data, from_json):
        if from_json:
            if data is not None:
                setattr(obj, key, self.get_object(data))
            else:
                setattr(obj, key, None)

    def set_date(self, obj, key, data, from_json):
        if from_json:
            if data is not None:
                setattr(obj, key, parse(data))
            else:
                setattr(obj, key, None)

    def set_list(self, obj, key, data, from_json):
        if from_json:
            tmplist = []
            if data is not None:
                for i in data:
                    if isinstance(i, six.string_types):
                        tmplist.append(i)
                    else:
                        tmplist.append(self.get_object(i))
            setattr(obj, key, tmplist)

    def set_feed(self, obj, key, data, from_json):
        from pypump.models.feed import Feed
        if from_json:
            if data is not None:
                try:
                    setattr(obj, key, Feed(pypump=self._pump).unserialize(data))
                except Exception as e:
                    _log.debug("Exception %s" % e)
            else:
                setattr(obj, key, [])


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
        """ A :class:`Feed <pypump.models.feed.Feed>`
        of the people who've liked the object.

        Example:
            >>> for person in mynote.likes:
            ...     print(person.webfinger)
            ...
            pypumptest1@pumpity.net
            pypumptest2@pumpyourself.com
        """

        endpoint = self.links["likes"]
        self._likes = self._likes or Feed(endpoint, pypump=self._pump)
        return self._likes

    favorites = likes

    def like(self):
        """ Like the object.

        Example:
            >>> anote.liked
            False
            >>> anote.like()
            >>> anote.liked
            True
        """
        self._verb('like')

    def unlike(self):
        """ Unlike a previously liked object.

        Example:
            >>> anote.liked
            True
            >>> anote.unlike()
            >>> anote.liked
            False
        """

        self._verb('unlike')

    def favorite(self):
        """ Favorite the object. """
        self._verb('favorite')

    def unfavorite(self):
        """ Unfavorite a previously favorited object. """
        self._verb('unfavorite')


class Commentable(object):
    """
        Provides the model with the comment method allowing you to post
        a comment to on the model. It also provides an ability to read
        comments.

        must have _links["replies"]
    """
    _comments = None

    @property
    def comments(self):
        """ A :class:`Feed <pypump.models.feed.Feed>`
        of the comments for the object.

        Example:
            >>> for comment in mynote.comments:
            ...     print(comment)
            ...
            comment by pypumptest2@pumpyourself.com
        """

        endpoint = self.links["replies"]
        self._comments = self._comments or Feed(endpoint, pypump=self._pump)
        return self._comments

    def comment(self, comment):
        """ Add a :class:`Comment <pypump.models.comment.Comment>`
        to the object.

        :param comment: A :class:`Comment <pypump.models.comment.Comment>`
            instance, text content is also accepted.

        Example:
            >>> anote.comment(pump.Comment('I agree!'))

            """
        if isinstance(comment, six.string_types):
            comment = self._pump.Comment(comment)

        comment.in_reply_to = self
        comment.send()


class Shareable(object):
    """
        Provides the model with the share and unshare methods and shares
        property allowing you to see who's shared the model.

        must have _links["shares"]
    """
    _shares = None

    @property
    def shares(self):
        """ A :class:`Feed <pypump.models.feed.Feed>`
        of the people who've shared the object.

        Example:
            >>> for person in mynote.shares:
            ...     print(person.webfinger)
            ...
            pypumptest1@pumpity.net
            pypumptest2@pumpyourself.com
        """

        endpoint = self.links["shares"]
        self._shares = self._shares or Feed(endpoint, pypump=self._pump)
        return self._shares

    def share(self):
        """ Share the object.

        Example:
            >>> anote.share()
        """

        self._verb('share')

    def unshare(self):
        """ Unshare a previously shared object.

        Example:
            >>> anote.unshare()
        """

        self._verb('unshare')


class Deleteable(object):
    """ Provides the model with the ability to be deleted """

    def delete(self):
        """ Delete the object content on the server.

        Example:
            >>> mynote.deleted
            >>> mynote.delete()
            >>> mynote.deleted
            datetime.datetime(2014, 10, 19, 9, 26, 39, tzinfo=tzutc())
        """

        self._verb('delete')


class Addressable(object):
    """ Adds methods to set to, cc, bto, bcc"""

    _to = list()
    _cc = list()
    _bto = list()
    _bcc = list()

    def _set_people(self, people):
        """ Sets who the object is sent to """
        if hasattr(people, "object_type"):
            people = [people]
        elif hasattr(people, "__iter__"):
            people = list(people)

        return people

    def _serialize_people(self, people):
        tmp = []
        for person in people:
            if isinstance(person, six.class_types):
                tmp.append(person())

            if isinstance(person, type(self._pump.Person())):
                tmp.append({
                    "id": person.id,
                    "objectType": person.object_type,
                })
            else:
                # probably a collection
                tmp.append({
                    "id": person.id,
                    "objectType": "collection",
                })

        return tmp

    # to
    def _get_to(self):
        """List of primary recipients.
        If entry is a :class:`Person` the object will show up
        in their direct inbox when sent.

        Example:
            >>> mynote = pump.Note('hello pypumptest1')
            >>> mynote.to = pump.Person('pypumptest1@pumpity.net')
            >>> mynote.to
            [<Person: pypumptest1@pumpity.net>]
        """
        return self._to

    def _set_to(self, *args, **kwargs):
        self._to = self._set_people(*args, **kwargs)

    to = property(fget=_get_to, fset=_set_to)

    # cc
    def _get_cc(self):
        """List of secondary recipients.
        The object will show up in the recipients inbox when sent.

        Example:
            >>> mynote = pump.Note('hello world')
            >>> mynote.cc = pump.Public
        """
        return self._cc

    def _set_cc(self, *args, **kwargs):
        self._cc = self._set_people(*args, **kwargs)

    cc = property(fget=_get_cc, fset=_set_cc)

    # bto
    def _get_bto(self):
        return self._bto

    def _set_bto(self, *args, **kwargs):
        self._bto = self._set_people(*args, **kwargs)

    bto = property(fget=_get_bto, fset=_set_bto)

    # bcc
    def _get_bcc(self):
        return self._bcc

    def _set_bcc(self, *args, **kwargs):
        self._bcc = self._set_people(*args, **kwargs)

    bcc = property(fget=_get_bcc, fset=_set_bcc)

    def serialize(self, *args, **kwargs):
        # now add the to, cc, bto, bcc
        data = {
            "to": self._serialize_people(self._to),
            "cc": self._serialize_people(self._cc),
            "bto": self._serialize_people(self._bto),
            "bcc": self._serialize_people(self._bcc),
        }

        return data


class Postable(Addressable):
    """ Adds .send() """

    def send(self):
        """ Send the object to the server.

        Example:
            >>> mynote = pump.Note('Hello world!)
            >>> mynote.send()
        """
        data = self.serialize()
        self._post_activity(data)
