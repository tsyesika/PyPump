
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

from __future__ import absolute_import

import json
import os
import re
import stat
import datetime

from pypump.exception import ValidationError, StoreException

# Regex taken from WTForms
EMAIL_REGEX = re.compile(r"^.+@[^.].*\.[a-z]{2,10}$", re.IGNORECASE)


def webfinger_validator(webfinger):
    """ Validates webfinger is correct - should look like user@host.tld """
    error = "Invalid webfinger. Should be in format username@host.tld"
    if not EMAIL_REGEX.match(webfinger):
        raise ValidationError(error)


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

    def __init__(self, *args, **kwargs):
        self.__validators = {}
        return super(AbstractStore, self).__init__(*args, **kwargs)

    def __prefix_key(self, key):
        """ This will add the prefix to the key if one exists on the store """
        # If there isn't a prefix don't bother
        if self.prefix is None:
            return key

        # Don't prefix key if it already has it
        if key.startswith(self.prefix + "-"):
            return key

        return "{0}-{1}".format(self.prefix, key)

    def __setitem__(self, key, *args, **kwargs):
        if key in self.__validators.keys():
            self.__validators[key](*args, **kwargs)

        key = self.__prefix_key(key)
        super(AbstractStore, self).__setitem__(key, *args, **kwargs)
        self.save()

    def __getitem__(self, key, *args, **kwargs):
        key = self.__prefix_key(key)
        return super(AbstractStore, self).__getitem__(key, *args, **kwargs)

    def __contains__(self, key, *args, **kwargs):
        key = self.__prefix_key(key)
        return super(AbstractStore, self).__contains__(key, *args, **kwargs)

    def set_validator(self, key, validator):
        self.__validators[key] = validator

    def save(self):
        """ Save all attributes in store """
        raise NotImplementedError("This is a dummy class, abstract")

    def export(self):
        """ Exports as dictionary """
        data = {}
        for key, value in self.items():
            data[key] = value

        return data

    @classmethod
    def load(cls, webfinger, pypump):
        """ This create and populate a store object """
        raise NotImplementedError("This is a dummy class, abstract")

    def __str__(self):
        return str(self.export())


class DummyStore(AbstractStore):
    """
    This doesn't persistantly store any data it just acts like
    a regular dictionary. This shouldn't be used for anything but
    testing as nothing will be stored on disk.
    """

    def save(self):
        pass

    @classmethod
    def load(cls, webfinger, pypump):
        return cls()


class JSONStore(AbstractStore):
    """
    Persistant dictionary-like storage

    Will write out all changes to disk as they're made
    NB: Will overwrite any changes made to disk not on class.
    """

    def __init__(self, data=None, filename=None, *args, **kwargs):
        if filename is None:
            filename = self.get_filename()
        self.filename = filename

        if data is None:
            data = {}

        super(JSONStore, self).__init__(data, *args, **kwargs)

    def update(self, *args, **kwargs):
        return_value = super(JSONStore, self).update(*args, **kwargs)
        self.save()
        return return_value

    def save(self):
        """ Saves dictionary to disk in JSON format. """
        if self.filename is None:
            raise StoreException("Filename must be set to write store to disk")

        # We need an atomic way of re-writing the settings, we also need to
        # prevent only overwriting part of the settings file (see bug #116).
        # Create a temp file and only then re-name it to the config
        filename = "{filename}.{date}.tmp".format(
            filename=self.filename,
            date=datetime.datetime.utcnow().isoformat()
        )

        # The `open` built-in doesn't allow us to set the mode
        mode = stat.S_IRUSR | stat.S_IWUSR  # 0600
        fd = os.open(filename, os.O_WRONLY | os.O_CREAT, mode)
        fout = os.fdopen(fd, "w")
        fout.write(json.dumps(self.export()))
        fout.close()

        # Now we should remove the old config
        if os.path.isfile(self.filename):
            os.remove(self.filename)

        # Now rename the temp file to the real config file
        os.rename(filename, self.filename)

    @classmethod
    def get_filename(cls):
        """ Gets filename of store on disk """
        config_home = os.environ.get("XDG_CONFIG_HOME", "~/.config")
        config_home = os.path.expanduser(config_home)

        base_path = os.path.join(config_home, "PyPump")
        if not os.path.isdir(base_path):
            os.mkdir(base_path)

        return os.path.join(base_path, "credentials.json")

    @classmethod
    def load(cls, webfinger, pypump):
        """ Load JSON from disk into store object """
        filename = cls.get_filename()

        if os.path.isfile(filename):
            data = open(filename).read()
            data = json.loads(data)
            store = cls(data, filename=filename)
        else:
            store = cls(filename=filename)

        store.prefix = webfinger
        return store
