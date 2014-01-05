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
import six

from pypump.models import AbstractModel
from pypump.models.activity import Mapper

_log = logging.getLogger(__name__)

class ItemList(object):
    """ A feed's list of items """

    previous_id = None

    def __init__(self, feed, count=None, start=None, stop=None):
        self.feed = feed
        self.start = start
        self.stop = stop
        self.cache = list()
        self.count = count
        self.itercounter = 0

    def __iter__(self):
        return self

    def _should_stop(self, data):
        if not data:
            return True

        if type(self.stop) == int:
            if type(self.start) == int:
                # feed[start_int:stop_int]
                if self.stop and self.itercounter >= (self.stop - self.start):
                    return True
            elif self.start is not None:
                # feed[start_id:count_int]
                if self.itercounter >= self.stop:
                    return True
            elif self.start is None:
                if self.itercounter >= self.stop:
                    return True

        elif self.stop is not None:
            # feed[:stop_id]
            if self.stop == data["id"]:
                return True

    def _build_cache(self):
        if not self.previous_id:
            if type(self.start) == int:
                response = self.feed._request(count=self.count, offset=self.start)
            elif self.start is not None:
                response = self.feed._request(count=self.count, before=self.start)
            else:
                response = self.feed._request(count=self.count)
        elif "next" in self.feed.links:
            url = self.feed.links["next"]
            response = self.feed._request(count=self.count, feed_url=url)
        else:
            response = None
        
        self.cache = response["items"] if response else None

    def __next__(self):
        if not self.cache:
            self._build_cache()
        data = self.cache.pop(0) if self.cache else None

        if self._should_stop(data):
            raise StopIteration

        if not data.get("objectType"): # object without an objectType, grr
            data["objectType"] = self.feed.object_types[0].capitalize()
        obj = Mapper(pypump=self.feed._pump).get_object(data)
        self.previous_id = obj.id
        self.itercounter +=1
        return obj

    def next(self):
        return self.__next__()


class Feed(AbstractModel):
    id = None
    display_name = None
    total_items = None
    object_types = None
    url = None
    _parent = None
    _ENDPOINT = None

    @property
    def ENDPOINT(self):
        if self._ENDPOINT is None:
            raise NotImplementedError("Definition of the ENDPOINT must be done by subclass")
        return self._ENDPOINT

    @property
    def items(self):
        return ItemList(self)

    def __init__(self, feed_url=None, *args, **kwargs):
        super(Feed, self).__init__(*args, **kwargs)

        self._ENDPOINT = feed_url
        self.id = self.ENDPOINT

        tmp = self.total_items or list(self[:1]) # we do a request on init to get some info

    def __repr__(self):
        return "<Feed: {type}>".format(
            type = self.TYPE,
        )

    def __str__(self):
        return "{name}".format(name=self.display_name or self.TYPE)

    def __iter__(self):
        return ItemList(self)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.__getslice__(key)
        if type(key) is not int:
            raise TypeError('index must be integer')
        item = ItemList(self, count=1, start=key, stop=key+1)
        try:
            return item.next()
        except StopIteration:
            raise IndexError

    def __getslice__(self, s, e=None):
        if type(s) is not slice:
            s = slice(s,e)

        return ItemList(self, start=s.start, stop=s.stop)

    def _request(self, offset=None, count=None, since=None, before=None, feed_url=None):
        params = dict()
        for i in ["count", "offset", "since", "before"]:
            if eval(i):
                params[i] = eval(i)

        url = feed_url or self.ENDPOINT

        _log.debug("feed._request: url: %s, params: %s", url, params)
        data = self._pump.request(url, params=params)
        self.unserialize(data)
        return data

    def _subfeed(self, feedname):
        endpoint = self.ENDPOINT
        if not endpoint.endswith("/"):
            endpoint += "/"
        return endpoint + feedname

    def unserialize(self, data):
        ignore_attr = ["dummyattr",]
        mapping = {
            "display_name": "displayName",
            "total_items": "totalItems",
            "object_types": "objectTypes",
            "url": "url",
            "author": "author"
        }

        Mapper(pypump=self._pump).parse_map(self, mapping=mapping, ignore_attr=ignore_attr, data=data)
        self.links = {} # we need to delete old links or else we get infinite feeds
        self.add_links(data)


class Followers(Feed):
    """ Person's followers """

class Following(Feed):
    """ People followed by Person """

class Favorites(Feed):
    """ Person's favorites """

class Inbox(Feed):
    """ Person's inbox """
    _ENDPOINT = None
    _direct = None
    _minor = None
    _major = None

    def __init__(self, feed_url=None, *args, **kwargs):
        super(Inbox, self).__init__(feed_url, *args, **kwargs)
        if feed_url is not None:
            self._ENDPOINT = feed_url

    @property
    def ENDPOINT(self):
        return self._ENDPOINT

    @property
    def direct(self):
        endpoint = self._subfeed("direct")
        if "direct" in self.id or "major" in self.id or "minor" in self.id:
            return self
        self._direct = self._direct or self.__class__(endpoint, pypump=self._pump)
        return self._direct

    @property
    def major(self):
        endpoint = self._subfeed("major")
        if "major" in self.id or "minor" in self.id:
            return self
        self._major = self._major or self.__class__(endpoint, pypump=self._pump)
        return self._major

    @property
    def minor(self):
        endpoint = self._subfeed("minor")
        if "minor" in self.id or "major" in self.id:
            return self
        self._minor = self._minor or self.__class__(endpoint, pypump=self._pump)
        return self._minor


class Outbox(Feed):
    """ Person's outbox """
    _ENDPOINT = None
    _major = None
    _minor = None

    def __init__(self, feed_url=None, *args, **kwargs):
        super(Outbox, self).__init__(feed_url, *args, **kwargs)
        if feed_url is not None:
            self._ENDPOINT = feed_url

    @property
    def ENDPOINT(self):
        return self._ENDPOINT

    @property
    def major(self):
        endpoint = self._subfeed("major")
        if "major" in self.id or "minor" in self.id:
            return self
        self._major = self._major or self.__class__(endpoint, pypump=self._pump)
        return self._major

    @property
    def minor(self):
        endpoint = self._subfeed("minor")
        if "major" in self.id or "minor" in self.id:
            return self
        self._minor = self._minor or self.__class__(endpoint, pypump=self._pump)
        return self._minor


class Lists(Feed):
    _membertype="person"

    @property
    def membertype(self):
        return self._membertype

    @property
    def ENDPOINT(self):
        # offset and count doesnt work properly, see https://github.com/e14n/pump.io/issues/794
        return self._ENDPOINT

    def create(self, display_name, content=None):
        """ Creates a new list """
        activity = {
            "verb":"create",
            "object":{
                "objectType":"collection",
                "objectTypes":[self.membertype],
                "displayName":display_name,
                "content":content
            }
        }
        self._post_activity(activity, unserialize=False)

    def __getitem__(self, key):
        if isinstance(key, six.string_types):
            lists = list(self)
            for i in lists:
                if i.display_name == key:
                    return i
        else:
            return super(Lists, self).__getitem__(key)

