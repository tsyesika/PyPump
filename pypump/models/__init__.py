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
import os
import mimetypes

from dateutil.parser import parse

from pypump.exceptions import PumpException

_log = logging.getLogger(__name__)


class PumpObject(object):

    _ignore_attr = list()

    _mapping = {
        "attachments": ("attachments", "literal"),
        "author": ("author", "PumpObject"),
        "content": ("content", "literal"),
        "display_name": ("displayName", "literal"),
        "downstream_duplicates": ("downstreamDuplicates", "list"),
        "id": ("id", "literal"),
        "in_reply_to": ("inReplyTo", "PumpObject"),
        "liked": ("liked", "literal"),
        # Links are not handled by Mapper yet # "links": ("links", None),
        "published": ("published", "date"),
        "summary": ("summary", "literal"),
        "updated": ("updated", "date"),
        "upstream_duplicates": ("upstreamDuplicates", "list"),
        "url": ("url", "literal"),
        "deleted": ("deleted", "date"),
        "object_type": ("objectType", "literal"),
        "_to": ("to", "list"),
        "_cc": ("cc", "list"),
        "_bto": ("bto", "list"),
        "_bcc": ("bcc", "list"),
        "_comments": ("replies", "Feed"),
        "_followers": ("followers", "Followers"),
        "_following": ("following", "Following"),
        "_likes": ("likes", "Feed"),
        "_shares": ("shares", "Feed")
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

    def __init__(self, pypump=None, *args, **kwargs):
        self._pump = pypump

    def parse_map(self, obj, mapping=None, *args, **kwargs):
        """ Parses a dictionary of (model_attr, json_attr) items """
        mapping = mapping or obj._mapping

        if "data" in kwargs:
            for k, v in mapping.items():
                if kwargs["data"].get(v[0], None) is not None:
                    val = kwargs["data"][v[0]]
                else:
                    val = None
                self.add_attr(obj, k, val, v[1], from_json=True)
        else:
            for k, v in mapping.items():
                if k in kwargs:
                    self.add_attr(obj, k, kwargs[k], v[1])

    def add_attr(self, obj, key, data, data_type, from_json=False):
        if data_type == "date":
            self.set_date(obj, key, data, from_json)
        elif data_type == "list":
            self.set_list(obj, key, data, from_json)
        elif data_type == "literal":
            self.set_literal(obj, key, data, from_json)
        else:
            self.set_object(obj, key, data, data_type, from_json)

    def set_literal(self, obj, key, data, from_json):
        if data is not None:
            setattr(obj, key, data)
        else:
            setattr(obj, key, None)

    def get_object(self, data, obj_type=None):
        """ Return PumpObject based on object type"""

        try:
            if obj_type is None or obj_type == "PumpObject":
                obj_type = data.get("objectType").capitalize()
        except:
            pass
        if obj_type is None:
            _log.debug("Mapper: No object type for data : %r" % data)
            return

        import pypump.models.activity

        if getattr(self._pump, obj_type, False):
            # Primary objects (Pump.Note etc)
            obj = getattr(self._pump, obj_type)
        elif getattr(pypump.models.activity, obj_type, False):
            # Secondary objects (Activity, Application)
            obj = getattr(pypump.models.activity, obj_type)
        elif getattr(pypump.models.feed, obj_type, False):
            # Feed objects
            obj = getattr(pypump.models.feed, obj_type)
        elif data.get("objectType", False):
            # Fall back to PumpObject
            obj = PumpObject
        else:
            _log.debug("Mapper: No object found for data: %r" % data)
            return
        obj = obj(pypump=self._pump).unserialize(data)
        _log.debug("Created PumpObject: %r" % obj_type)
        return obj

    def set_object(self, obj, key, data, data_type, from_json):
        if from_json:
            if data is not None:
                pump_obj = self.get_object(data, data_type)
                if pump_obj is not None:
                    setattr(obj, key, pump_obj)
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
        if self._likes is None:
            self._likes = Feed(endpoint, pypump=self._pump)
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
        if self._comments is None:
            self._comments = Feed(endpoint, pypump=self._pump)
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
        if self._shares is None:
            self._shares = Feed(endpoint, pypump=self._pump)
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


class Uploadable(Addressable):
    """ Adds .from_file() """

    def from_file(self, filename):
        """ Uploads a file from a filename on your system.

        :param filename: Path to file on your system.

        Example:
            >>> myimage.from_file('/path/to/dinner.png')
        """

        mimetype = mimetypes.guess_type(filename)[0] or "application/octal-stream"
        headers = {
            "Content-Type": mimetype,
            "Content-Length": os.path.getsize(filename),
        }

        # upload file
        file_data = self._pump.request(
            "/api/user/{0}/uploads".format(self._pump.client.nickname),
            method="POST",
            data=open(filename, "rb").read(),
            headers=headers,
        )

        # now post it to the feed
        data = {
            "verb": "post",
            "object": file_data,
        }
        data.update(self.serialize())

        if not self.content and not self.display_name and not self.license:
            self._post_activity(data)
        else:
            self._post_activity(data, unserialize=False)

            # update post with display_name and content
            if self.content:
                file_data['content'] = self.content
            if self.display_name:
                file_data['displayName'] = self.display_name
            if self.license:
                file_data['license'] = self.license
            data = {
                "verb": "update",
                "object": file_data,
            }
            self._post_activity(data)

        return self
