
# This has been taken from "Waterworks"
# Commit ID: dc05a36ed34ab94b657bcadeb70ccc3187227b2d
# URL: https://github.com/Aeva/waterworks
#
# PyPump is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPump is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPump.  If not, see <http://www.gnu.org/licenses/>.

import json
import os

class StoreException(Exception):
    pass

class AbstractStore(dict):
    """
    This should act like a dictionary. This should be persistant and
    save upon setting a value. The interface to this object is::

    >>> store = AbstractStore.load()
    >>> store["my-key"] = "my-value"
    >>> store["my-key"]
    'my-value'

    This must save when "my-value" was set (in __setitem__). There
    should also be a .save method which should take the entire object
    and write them out.
    """

    prefix = None

    def __prefix_key(self, key):
        # If there isn't a prefix don't bother
        if self.prefix is None:
            return key

        # Don't prefix key if it already has it
        if key.startswith(self.prefix):
            return key

        return "{0}-{1}".format(self.prefix, key)

    def __setitem__(self, key, *args, **kwargs):
        key = self.__prefix_key(key)
        return super(AbstractStore, self).__setitem__(key, *args, **kwargs)

    def __getitem__(self, key, *args, **kwargs):
        key = self.__prefix_key(key)
        return super(AbstractStore, self).__getitem__(key, *args, **kwargs)

    def __contains__(self, key, *args, **kwargs):
        key = self.__prefix_key(key)
        return super(AbstractStore, self).__contains__(key, *args, **kwargs)

    def save(self):
        """ Save all attributes in store """
        raise NotImplemented()

    @classmethod
    def load(self):
        """ This create and populate a store object """
        raise NotImplemented()

class Store(AbstractStore):
    """
        Persistant dictionary-like storage

        Will write out all changes to disk as their made
        NB: Will overwrite any changes made to disk not on class.
    """

    def update(self, *args, **kwargs):
        return_value = super(Store, self).update(*args, **kwargs)
        self.save()
        return return_value

    def __setitem__(self, *args, **kwargs):
        return_value = super(Store, self).__setitem__(*args, **kwargs)
        self.save()
        return return_value

    def save(self):
        """ Saves dictionary to disk in JSON format. """
        if self.filename is None:
            raise StoreException("A filename must be set to write storage to disk")

        # This seems a hack, is there a better way?
        prefix = self.prefix
        self.prefix = None
        data = json.dumps(self)
        self.prefix = prefix

        fout = open(self.filename, "w")
        fout.write(data)
        fout.close()

    @classmethod
    def get_filename(cls):
        XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", "~/.config")
        XDG_CONFIG_HOME = os.path.expanduser(XDG_CONFIG_HOME)

        CONFIG_BASE = os.path.join(XDG_CONFIG_HOME, "PyPump")
        if not os.path.isdir(CONFIG_BASE):
            os.mkdir(CONFIG_BASE)

        return os.path.join(CONFIG_BASE, "credentials.json")

    @classmethod
    def load(cls, webfinger, pypump):
        """ Load JSON from disk into store object """
        filename = cls.get_filename()

        if os.path.isfile(filename):
            data = open(filename).read()
            data = json.loads(data)
            store = cls(data)
        else:
            store = cls()

        store.filename = filename
        store.prefix = webfinger
        return store
