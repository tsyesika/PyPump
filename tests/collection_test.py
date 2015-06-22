# -*- coding: utf-8 -*-
import six

from pypump.models.collection import Collection
from pypump.models.feed import Feed
from tests import PyPumpTest


class CollectionTest(PyPumpTest):
    def setUp(self):
        super(CollectionTest, self).setUp()
        self.response.data = {
            "content": "",
            "objectTypes": [
                "person"
            ],
            "displayName": "test list for testuser",
            "objectType": "collection",
            "author": {
                "objectType": "person",
                "id": "acct:testuser@example.com"
            },
            "published": "2014-08-31T20:54:25Z",
            "updated": "2014-08-31T20:54:25Z",
            "links": {
                "self": {
                    "href": "https://example.com/api/collection/CZGYt-ljQ2WcmqfU1n5znA"
                }
            },
            "likes": {
                "url": "https://example.com/api/collection/CZGYt-ljQ2WcmqfU1n5znA/likes"
            },
            "replies": {
                "url": "https://example.com/api/collection/CZGYt-ljQ2WcmqfU1n5znA/replies",
                "items": []
            },
            "shares": {
                "url": "https://example.com/api/collection/CZGYt-ljQ2WcmqfU1n5znA/shares",
                "items": []
            },
            "url": "https://example.com/testuser/list/CZGYt-ljQ2WcmqfU1n5znA",
            "id": "https://example.com/api/collection/CZGYt-ljQ2WcmqfU1n5znA",
            "members": {
                "totalItems": 0,
                "url": "https://example.com/api/collection/CZGYt-ljQ2WcmqfU1n5znA/members"
            },
            "liked": False,
            "pump_io": {
                "shared": False
            }
        }

        self.collection = Collection(pypump=self.pump).unserialize(self.response.data)

    def test_collection(self):
        # is a Collection object
        self.assertTrue(isinstance(self.collection, Collection))

        # object to string
        self.assertEqual(self.collection.__str__(), self.collection.display_name)
        self.collection.display_name = u'test list for Testanvändare'
        if six.PY3:
            self.assertEqual(self.collection.__str__(), self.collection.display_name)
        else:
            self.assertEqual(self.collection.__str__(), self.collection.display_name.encode('utf-8'))

    def test_collection_attr_display_name(self):
        self.assertTrue(hasattr(self.collection, 'display_name'))
        self.assertEqual(self.collection.display_name, self.response["displayName"])

    def test_collection_attr_url(self):
        self.assertTrue(hasattr(self.collection, 'url'))
        self.assertEqual(self.collection.url, self.response["url"])

    def test_collection_attr_members(self):
        self.assertTrue(hasattr(self.collection, 'members'))
        self.assertTrue(isinstance(self.collection.members, Feed))

    def test_collection_attr_author(self):
        self.assertTrue(hasattr(self.collection, 'author'))
        self.assertTrue(isinstance(self.collection.author, type(self.pump.Person())))

    def test_collection_attr_links(self):
        self.assertTrue(hasattr(self.collection, 'links'))

        # we should expand this test when we have settled on way to show links
        self.assertTrue(self.collection.links is not None)

    def test_collection_add(self):
        self.response.data = {
            "verb": "add",
            "object": {
                "objectType": "person",
                "id": "testuser2@example.com",
            },
            "target": {
                "objectType": "collection",
                "id": "https://example.com/api/collection/CZGYt-ljQ2WcmqfU1n5znA",
            }
        }

        person = self.pump.Person('testuser2@example.com')
        self.collection.add(person)

    def test_collection_remove(self):
        self.response.data = {
            "verb": "remove",
            "object": {
                "objectType": "person",
                "id": "testuser2@example.com"
            },
            "target": {
                "objectType": "collection",
                "id": "https://example.com/api/collection/CZGYt-ljQ2WcmqfU1n5znA",
            }
        }

        person = self.pump.Person('testuser2@example.com')
        self.collection.remove(person)
