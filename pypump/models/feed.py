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
from pypump.exception import PyPumpException
from pypump.models import PumpObject, Mapper

_log = logging.getLogger(__name__)

class ItemList(object):
    """ This object is returned when iterating over a Feed """
    _done = False

    def __init__(self, feed, offset=None, stop=None, limit=None, since=None, before=None, cached=False):
        """
        feed: Feed object: Feed object to return items from
        offset: int or PumpObject: beginning of slice
        stop: int or PumpObject: end of slice
        limit: int or None: Number of objects to return
        since: PumpObject: Return objects newer than this
        before: PumpObject: Return objects older than this
        cached: bool: Return objects from feed._items instead of API

        """
        self.cache = []
        self.feed = feed
        self.url = self.feed.url
        self.itemcount = 0
        self._offset = offset

        #set limit based on offset and stop
        if isinstance(stop, int):
            if isinstance(offset, int):
                self._limit = stop - offset
            else:
                self._limit = stop
        else:
            self._limit = limit

        #set since to stop if stop is a PumpObject
        if self.get_obj_id(stop):
            self._since = self.get_obj_id(stop)
        else:
            self._since = self.get_obj_id(since)

        #set before to offset if offset is a PumpObject
        if self.get_obj_id(offset):
            self._before = self.get_obj_id(offset)
            self._offset = None
        else:
            self._before = self.get_obj_id(before)

        self._cached = cached

        if self._offset and (self._since or self._before):
            raise PyPumpException("can not have both offset and since/before parameters")
        elif self._since and self._before:
            raise PyPumpException("can not have both since and before parameters")


    def get_obj_id(self, item):
        """ Get the id of a PumpObject
        item: id string or PumpObject
        """
        if item is not None:
            if isinstance(item, six.string_types):
                return item
            elif hasattr(item, 'id'):
                return item.id

    def get_page(self, url):
        """ Get a page of items from API """
        if url:
            try:
                data = self.feed._request(url,
                                          offset=self._offset,
                                          since=self._since,
                                          before=self._before)
            except:
                return []
            # set values to False to avoid using them for next request
            self._before = False if self._before is not None else None
            self._since = False if self._since is not None else None
            if self._since is not None:
                # we want oldest items first when using 'since'
                return reversed(data['items'])
            else:
                return data['items']
        else:
            return []

    def get_cached(self):
        """ Get items from feed cache while trying to emulate
        how API handles offset/since/before parameters
        """
        def id_in_list(list, id):
            if id:
                if [i for i in list if i.id == id]:
                    return True
                else:
                    raise PyPumpException("id %r not in feed." % self._since)

        tmp = []
        if self._before is not None:
            #return list based on before param
            if not id_in_list(self.feed._items, self._before):
                return tmp
            if isinstance(self._before, six.string_types):
                found = False
                for i in self.feed._items:
                    if not found:
                        if i.id == self._before:
                            found = True
                        continue
                    else:
                        tmp.append(i)
                self._before = False
            return tmp

        if self._since is not None:
            #return list based on since param
            if not id_in_list(self.feed._items, self._since):
                return tmp
            if isinstance(self._since, six.string_types):
                found = False
                for i in self.feed._items:
                    if i.id == self._since:
                        found = True
                        break
                    else:
                        tmp.append(i)
                self._since = False
            return reversed(tmp)

        if not hasattr(self,'usedcache'):
            self.usedcache=True #invalidate cache

            if isinstance(self._offset, int):
                #return list based on offset
                return self.feed._items[self._offset:]
    
            return self.feed._items
        else:
            return tmp

    @property
    def done(self):
        """ Check if we should stop returning objects """
        if self._done:
            return self._done

        if self._limit is None:
            self._done = False
        elif self.itemcount >= self._limit:
            self._done = True

        return self._done

    def _build_cache(self):
        """ Build a list of objects from feed's cached items or API page"""
        self.cache = []
        if self.done:
            return

        for i in (self.get_cached() if self._cached else self.get_page(self.url)):
            if not self._cached:
                #some objects don't have objectType set (inbox activities)
                if not i.get("objectType"):
                    i["objectType"] = self.feed.object_types[0]
                obj = Mapper(pypump=self.feed._pump).get_object(i)

            else:
                obj = i
            self.cache.append(obj)

        #ran out of items
        if len(self.cache) <= 0:
            self._done = True

        # check what to do next time
        if self._since is not None:
            if self.feed.links.get('prev'):
                self.url = self.feed.links['prev']
                del self.feed.links['prev'] #avoid using it again
        else:
            if self.feed.links.get('next'):
                self.url = self.feed.links['next']
                del self.feed.links['next'] #avoid using it again
            else:
                self.url = None


    def __next__(self):
        """ Return next object or raise StopIteration """
        if len(self.cache) <= 0:
            self._build_cache()

        if self.done:
            raise StopIteration
        else:
            obj = self.cache.pop(0)

        self.itemcount +=1
        return obj

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()


class Feed(PumpObject):
    _ignore_attr = []
    _mapping = {"display_name": "displayName",
                "url": "url",
                "object_types": "objectTypes",
                "_items": "items",
                "author": "author",
                "total_items": "totalItems",
               }

    def __init__(self, url=None, *args, **kwargs):
        super(Feed, self).__init__(*args, **kwargs)
        self.unserialize() #do empty unserialize to set all attributes
        self.url = url or None

    def items(self, offset=None, limit=20, since=None, before=None, *args, **kwargs):
        """ Get a feed's items.
        offset: Amount of items to skip before returning data
        since:  Return items added after this id (ordered old -> new)
        before: Return items added before this id (ordered new -> old)
        limit: Amount of items to return
        """
        if self._items is not None and self.total_items is not None:
            if len(self._items) >= self.total_items:
                #return cached items
                return ItemList(self, offset=offset, limit=limit, since=since, before=before, cached=True)

        return ItemList(self, offset=offset, limit=limit, since=since, before=before)

    def _request(self, url, offset=None, since=None, before=None):
        params = dict()
        for i in ["offset", "since", "before"]:
            if eval(i):
                params[i] = eval(i)
        _log.debug("Feed._request: url: %s, params: %s", url, params)
        data = self._pump.request(url, params=params)
        self.unserialize(data)
        return data

    def unserialize(self, data={}):
        Mapper(pypump=self._pump).parse_map(self, data=data)
        self.add_links(data)
        self.url = data.get('pump_io', {}).get('proxyURL') or self.url
        return self

    def _subfeed(self, feedname):
        """ Used for Inbox/Outbox major/minor/direct subfeeds """
        url = self.url
        if not url.endswith("/"):
            url += "/"
        return url + feedname

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.__getslice__(key)

        if type(key) is not int:
            raise TypeError('index must be integer')
        item = ItemList(self, limit=1, offset=key, stop=key+1)
        try:
            return item.next()
        except StopIteration:
            raise IndexError

    def __getslice__(self, s, e=None):
        if type(s) is not slice:
            s = slice(s,e)

        if self._items is not None and self.total_items is not None:
            if len(self._items) >= self.total_items:
                #return cached items
                return ItemList(self, offset=s.start, stop=s.stop, cached=True)

        return ItemList(self, offset=s.start, stop=s.stop)

    def __iter__(self):
        return self.items(limit=None)

    def __repr__(self):
        return '<Feed: {url}>'.format(url=self.url)

    def __unicode__(self):
        return u'{name}'.format(name=self.display_name or '')


class Followers(Feed):
    """ Person's followers """

class Following(Feed):
    """ People followed by Person """

class Favorites(Feed):
    """ Person's favorites """
    #API bug, can only get 20 items, see https://github.com/xray7224/PyPump/issues/65

class Inbox(Feed):
    """ Person's inbox """
    _direct = None
    _minor = None
    _major = None

    def __init__(self, *args, **kwargs):
        super(Inbox, self).__init__(*args, **kwargs)

    @property
    def direct(self):
        url = self._subfeed("direct")
        if "direct" in self.url or "major" in self.url or "minor" in self.url:
            return self
        self._direct = self._direct or self.__class__(url, pypump=self._pump)
        return self._direct
    
    @property
    def major(self):
        url = self._subfeed("major")
        if "major" in self.url or "minor" in self.url:
            return self
        self._major = self._major or self.__class__(url, pypump=self._pump)
        return self._major
    
    @property
    def minor(self):
        url = self._subfeed("minor")
        if "minor" in self.url or "major" in self.url:
            return self
        self._minor = self._minor or self.__class__(url, pypump=self._pump)
        return self._minor


class Outbox(Feed):
    """ Person's outbox """
    _major = None
    _minor = None

    def __init__(self, *args, **kwargs):
        super(Outbox, self).__init__(*args, **kwargs)

    @property
    def major(self):
        url = self._subfeed("major")
        if "major" in self.url or "minor" in self.url:
            return self
        self._major = self._major or self.__class__(url, pypump=self._pump)
        return self._major

    @property
    def minor(self):
        url = self._subfeed("minor")
        if "major" in self.url or "minor" in self.url:
            return self
        self._minor = self._minor or self.__class__(url, pypump=self._pump)
        return self._minor


class Lists(Feed):
    # API bug, offset and count doesnt work right,
    # see https://github.com/e14n/pump.io/issues/794
    # TODO can not see lists for persons on remote server (need more auth than 2-leg)
    _membertype="person"

    @property
    def membertype(self):
        return self._membertype

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

