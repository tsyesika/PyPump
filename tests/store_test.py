from __future__ import absolute_import

from tests import PyPumpTest
from pypump import AbstractStore

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
        with self.assertRaises(KeyError):
            store["coffee"]

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
        with self.assertRaises(KeyError):
            store["key"]

        self.assertEqual(store["hai-key"], "value")
