from __future__ import absolute_import

import os
import shutil
import stat

from pypump import AbstractStore, JSONStore
from tests import PyPumpTest

class TestStore(AbstractStore):
    """ Provide a more testable store """
    save_called = False

    def save(self):
        """
        Should save data in store
        This will just change a flag to show it's been called
        """
        self.save_called = True

class StoreTest(PyPumpTest):
    """
    Test the store class
    """

    def test_store_and_get(self):
        """ Test that a value can be stored and then retrived """
        store = TestStore()

        # Check that it raises a key error when nothing has been stored.
        def empty_store_key():
            store["coffee"]
        self.assertRaises(KeyError, empty_store_key)
            
        # Store something
        store["coffee"] = "awesome"

        # Check we can get the same value back out
        self.assertEqual(store["coffee"], "awesome")


    def test_save_on_set(self):
        """ Test that save is called when a value is set """
        store = TestStore()

        # Check that save hasn't been called yet.
        self.assertEqual(store.save_called, False)

        # set some information
        store["coffee"] = "awesome"

        # Check save has been called
        self.assertEqual(store.save_called, True)

    def test_prefix(self):
        """ Test that the prefix is applied to the get and set keys """
        store = TestStore()
        store.prefix = "hai"

        # Test that we can store something and get it back
        store["key"] = "value"
        self.assertEqual(store["key"], "value")

        # Remove the prefix and check that we have to manually prefix
        # the key to get back the previously stored value.
        store.prefix = None

        # Unprefixed shouldn't exist.
        def empty_store_key():
            store["key"]
        self.assertRaises(KeyError, empty_store_key)

        self.assertEqual(store["hai-key"], "value")

class JSONStoreTest(PyPumpTest):
    """
    Test the JSON implementation of the store class
    """

    def setUp(self):
        filename = os.path.abspath(".")
        filename = os.path.join(filename, "pypumpstoretest.json")

        self.assertFalse(os.path.exists(filename), "{0} already exists".format(filename))

        self.filename = filename

    def tearDown(self):
        try:
            os.remove(self.filename)
        except OSError:
            pass

    def test_creating_pypump_dir(self):
        os.environ["XDG_CONFIG_HOME"] = os.path.join(os.path.abspath("."), "pypump_config")
        self.assertFalse(os.path.exists(os.environ["XDG_CONFIG_HOME"]), "{0} already exists".format(os.environ["XDG_CONFIG_HOME"]))

        store = JSONStore()
        store["unittest"] = "framework"

        shutil.rmtree(os.environ["XDG_CONFIG_HOME"], ignore_errors=True)

    def test_permissions(self):
        store = JSONStore(filename=self.filename)
        store["unittest"] = "framework"

        mode = os.stat(self.filename).st_mode

        #we're only going to test to make sure "others" can't read the file
        self.assertEqual(mode & stat.S_IRWXO, 0, "File mode is insecure")
