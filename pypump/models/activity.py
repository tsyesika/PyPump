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

from dateutil.parser import parse as dateparse
from pypump.models import AbstractModel

import pypump.models.activity # dodgy
import logging

_log = logging.getLogger(__name__)

class Mapper(object):
    """ Handles mapping of json attributes to models """

    # TODO probably better to move this into the models,
    # {"json_attr":("model_attr", "datatype"), .. } or similar
    strings = ["content", "display_name", "id", "objectType", "object_type",
               "summary", "url", "preferred_username", "verb"]
    dates = ["updated", "published", "deleted"]
    objects = ["generator", "actor", "obj", "author", "in_reply_to"]
    #feeds = ["likes", "shares", "replies"]

    def parse_map(self, obj, mapping, *args, **kwargs):
        """ Parses a dictionary of (model_attr, json_attr) items """

        if "jsondata" in kwargs:
            for k, v in mapping.items():
                if v in kwargs["jsondata"] and k not in obj._ignore_attr:
                    self.add_attr(obj, k, kwargs["jsondata"][v], from_json=True)
        else:
            for k, v in mapping.items():
                if k in kwargs and k not in obj.ignore_attr:
                    self.add_attr(obj, k, kwargs[k])

    def add_attr(self, obj, key, data, from_json=False):
        if key in self.strings:
            self.set_string(obj, key, data, from_json)
        elif key in self.objects:
            self.set_object(obj, key, data, from_json)
        elif key in self.dates:
            self.set_date(obj, key, data, from_json)
        else:
            _log.info("ignoring unknown attribute %r", key)

    def set_string(self, obj, key, data, from_json):
        setattr(obj, key, data)

    def get_object(self, data):
        # We're only looking for models in this file for now.
        self.models = pypump.models.activity
        try:
            # Look for suitable model based on objectType
            objekt = getattr(self.models, data["objectType"].capitalize())
            return objekt(jsondata=data)
        except AttributeError:
            # Fall back to ActivityObject if not found
            return ActivityObject(jsondata=data)

    def set_object(self, obj, key, data, from_json):
        if from_json:
            setattr(obj, key, self.get_object(data))

    def set_date(self, obj, key, data, from_json):
        if from_json:
            setattr(obj, key, dateparse(data))


class ActivityObject(AbstractModel):
    """ Super class for activity objects,
        this class is used when we can't find a matching object type
    """
    _ignore_attr = list()

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
        "url": "url"
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
        Mapper().parse_map(self, ActivityObject._mapping, *args, **kwargs)


class Application(ActivityObject):
    _ignore_attr = ["likes", "replies", "shares"]
    _mapping = {}

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        Mapper().parse_map(self, self._mapping, *args, **kwargs)


class Activity(AbstractModel):

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

        # Attributes we don't need/have proper models for
        mapping = {
            "verb":"verb",
            "generator":"generator",
            "updated":"updated",
            "url":"url",
            "published":"published",
            "content":"content",
            "id":"id",
            "to":"to" # TODO not yet in Mapper
        }

        if "author" not in data["object"]:
            # add author if not set (true for posted objects in inbox/major)
            data["object"]["author"] = data["actor"]

        for model_attr, json_attr in {"actor":"actor", "obj":"object"}.items():
            try:
                objekt = getattr(self._pump, data[json_attr]["objectType"].capitalize())()
                setattr(self, model_attr, objekt.unserialize(data[json_attr]))
            except AttributeError:
                mapping[model_attr] = json_attr

        for model_attr, json_attr in mapping.items():
            if json_attr in data:
                Mapper().add_attr(self, model_attr, data[json_attr], from_json=True)

        return self

