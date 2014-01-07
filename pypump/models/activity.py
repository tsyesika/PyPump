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

from dateutil.parser import parse
from pypump.models import AbstractModel

import pypump.models.activity
import six
import logging

_log = logging.getLogger(__name__)

class Mapper(object):
    """ Handles mapping of json attributes to models """

    # TODO probably better to move this into the models,
    # {"json_attr":("model_attr", "datatype"), .. } or similar
    literals = ["content", "display_name", "id", "objectType",
                "object_type", "summary", "url", "preferred_username",
                "verb", "username", "total_items", "liked",]
    dates = ["updated", "published", "deleted", "received"]
    objects = ["generator", "actor", "obj", "author", "in_reply_to", "location"]
    lists = ["to", "cc", "bcc", "bto","object_types"]
    #feeds = ["likes", "shares", "replies"]

    def __init__(self, pypump=None, *args, **kwargs):
        self._pump = pypump

    def parse_map(self, obj, mapping=None, ignore_attr=None, *args, **kwargs):
        """ Parses a dictionary of (model_attr, json_attr) items """
        mapping = mapping or obj._mapping
        ignore_attr = ignore_attr or obj._ignore_attr

        if "data" in kwargs:
            for k, v in mapping.items():
                if v in kwargs["data"] and k not in ignore_attr:
                    self.add_attr(obj, k, kwargs["data"][v], from_json=True)
                #elif k not in ignore_attr:
                    #_log.debug("Setting attribute %r to None" % k)
                    #self.set_none(obj, k)
        else:
            for k, v in mapping.items():
                if k in kwargs and k not in ignore_attr:
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
        else:
            _log.debug("Ignoring unknown attribute %r", key)

    def set_none(self, obj, key):
        setattr(obj, key, None)

    def set_literal(self, obj, key, data, from_json):
        setattr(obj, key, data)

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
                # Look for suitable activityobject model based on objectType
                obj = getattr(pypump.models.activity, data.get("objectType").capitalize())
                obj = obj(pypump=self._pump, data=data)
                _log.debug("Created activity.* model: %r" % obj.__class__)
                return obj
            except AttributeError as e:
                # Fall back to ActivityObject
                _log.debug("Exception: %s" % e)
                obj = ActivityObject(pypump=self._pump, data=data)
                _log.debug("Created ActivityObject: %r" % obj)
                return obj

    def set_object(self, obj, key, data, from_json):
        if from_json:
            setattr(obj, key, self.get_object(data))

    def set_date(self, obj, key, data, from_json):
        if from_json:
            setattr(obj, key, parse(data))

    def set_list(self, obj, key, data, from_json):
        if from_json:
            tmplist = []
            for i in data:
                if isinstance(i, six.string_types):
                    tmplist.append(i)
                else:
                    tmplist.append(self.get_object(i))
            setattr(obj, key, tmplist)


class ActivityObject(AbstractModel):
    """ Super class for activity objects,
        this class is used when we can't find a matching object type
    """
    _ignore_attr = []

    # Map of (model_attr, json_attr) pairs
    # TODO include attribute type here, see TODO in Mapper
    _mapping = {
        "attachments": "attachments",
        "author": "author",
        "content": "content",
        "display_name": "displayName",
        "downstream_duplicates": "downstreamDuplicates",
        "id": "id",
        "image": "image",
        "in_reply_to": "inReplyTo",
        "likes": "likes",
        "links": "links",
        "objectType": "objectType",
        "published": "published",
        "replies": "replies",
        "shares": "shares",
        "summary": "summary",
        "updated": "updated",
        "upstream_duplicates": "upstreamDuplicates",
        "url": "url",
        "deleted" : "deleted"
    }

    
    # We set these to None for now to remove the AbstractModel read-only properties so we can set our own attributes
    #TYPE = None
    objectType = None

    def __repr__(self):
        return "<{type}: {id}>".format(type=self.objectType, id=self.id)

    def __str__(self):
        return str(self.__repr__())

    def __init__(self, *args, **kwargs):
        super(ActivityObject, self).__init__(*args, **kwargs)
        Mapper(*args, **kwargs).parse_map(self,
                           mapping=ActivityObject._mapping,
                           ignore_attr=ActivityObject._ignore_attr,
                           *args,
                           **kwargs)


class Application(ActivityObject):
    _ignore_attr = ["likes", "replies", "shares"]
    _mapping = {}

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        Mapper(*args, **kwargs).parse_map(self, *args, **kwargs)


class Activity(AbstractModel):
    _ignore_attr = []
    _mapping = {
        "verb":"verb",
        "generator":"generator",
        "updated":"updated",
        "url":"url",
        "published":"published",
        "received":"received",
        "content":"content",
        "id":"id",
        "to":"to",
        "cc":"cc",
        "actor":"actor",
        "obj":"object"
    }

    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)
    
    def __repr__(self):
        return '<Activity: {webfinger} {verb}ed {model}>'.format(
            webfinger=self.actor.id.replace("acct:", ""),
            verb=self.verb.rstrip("e"), # english: e + ed = ed
            model=self.obj.objectType
        )

    def unserialize(self, data):
        """ From JSON -> Activity object """

        if "author" not in data["object"]:
            # add author if not set (true for posted objects in inbox/major)
            data["object"]["author"] = data["actor"]

        Mapper(pypump=self._pump).parse_map(self, data=data)
        self.add_links(data)

        return self

