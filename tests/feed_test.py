# -*- coding: utf-8 -*-
import six

from pypump.models.feed import Feed
from tests import PyPumpTest


class FeedTest(PyPumpTest):
    def setUp(self):
        super(FeedTest, self).setUp()
        self.response.data = {
            "displayName": "Followers for Testuser",
            "url": "https://example.com/api/user/testuser/followers",
            "objectTypes": [
                "person"
            ],
            "items": [{"objectType": "person", "id": "acct:testuser%d@example.com" % i} for i in range(20)],
            "totalItems": 20,
            "author": {"objectType": "person", "id": "acct:testuser@example.com"},
            "links": {
                "self": {"href": "https://example.com/api/user/testuser/followers?offset=0&count=20"},
                "current": {"href": "https://example.com/api/user/testuser/followers"},
                "prev": {"href": "https://example.com/api/user/testuser/followers?since=acct%3Atestuser0%40example.com"},
                "next": {"href": "https://example.com/api/user/testuser/followers?before=acct%3Atestuser19%40example.com"},
            }
        }

        self.feed = Feed(pypump=self.pump).unserialize(self.response.data)

    def test_feed(self):
        # is a Feed object
        self.assertTrue(isinstance(self.feed, Feed))

        # object to string
        self.assertEqual(self.feed.__str__(), self.feed.display_name)
        self.feed.display_name = u'Followers for Testanvändare'

        if six.PY3:
            self.assertEqual(self.feed.__str__(), self.feed.display_name)
        else:
            self.assertEqual(self.feed.__str__(), self.feed.display_name.encode('utf-8'))

    def test_feed_attr_display_name(self):
        self.assertTrue(hasattr(self.feed, 'display_name'))
        self.assertEqual(self.feed.display_name, self.response["displayName"])

    def test_feed_attr_url(self):
        self.assertTrue(hasattr(self.feed, 'url'))
        self.assertEqual(self.feed.url, self.response["url"])

    def test_feed_attr_object_types(self):
        self.assertTrue(hasattr(self.feed, 'object_types'))
        self.assertEqual(self.feed.object_types, self.response["objectTypes"])

    def test_feed_attr_items(self):
        self.assertTrue(hasattr(self.feed, '_items'))
        self.assertTrue(isinstance(self.feed._items, list))

    def test_feed_attr_total_items(self):
        self.assertTrue(hasattr(self.feed, 'total_items'))
        self.assertEqual(self.feed.total_items, self.response["totalItems"])

    def test_feed_attr_author(self):
        self.assertTrue(hasattr(self.feed, 'author'))
        self.assertTrue(isinstance(self.feed.author, type(self.pump.Person())))

    def test_feed_attr_links(self):
        self.assertTrue(hasattr(self.feed, 'links'))

        # we should expand this test when we have settled on way to show links
        self.assertTrue(self.feed.links is not None)

    def test_feed_slice_0_to_5(self):
        sliceditems = self.feed[:5]
        self.assertEqual(len(sliceditems), 5)
        self.assertEqual(sliceditems[0].id, self.response['items'][0]['id'])
        self.assertEqual(list(sliceditems)[-1].id, self.response['items'][4]['id'])

    def test_feed_slice_3_to_6(self):
        sliceditems = self.feed[3:6]
        self.assertEqual(len(sliceditems), 3)
        self.assertEqual(sliceditems[0].id, self.response['items'][3]['id'])
        self.assertEqual(list(sliceditems)[-1].id, self.response['items'][5]['id'])

    def test_feed_slice_id_to_inf(self):
        sliceditems = self.feed[slice('acct:testuser10@example.com', None)]
        self.assertEqual(len(sliceditems), 9)
        self.assertEqual(sliceditems[0].id, self.response['items'][11]['id'])
        self.assertEqual(list(sliceditems)[-1].id, self.response['items'][19]['id'])

    def test_feed_slice_zero_to_id(self):
        sliceditems = self.feed[slice('acct:testuser5@example.com')]
        self.assertEqual(len(sliceditems), 5)
        self.assertEqual(list(sliceditems)[-1].id, self.response['items'][0]['id'])
        self.assertEqual(sliceditems[0].id, self.response['items'][4]['id'])

    def test_feed_items_before(self):
        # before and limit 3
        items = self.feed.items(before='acct:testuser10@example.com', limit=3)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].id, self.response['items'][11]['id'])
        self.assertEqual(list(items)[-1].id, self.response['items'][13]['id'])

    def test_feed_items_since(self):
        # since and limit 12 (limit more than items returned)
        items = self.feed.items(since='acct:testuser10@example.com', limit=12)
        self.assertEqual(len(items), 10)
        self.assertEqual(items[0].id, self.response['items'][9]['id'])
        self.assertEqual(list(items)[-1].id, self.response['items'][0]['id'])

    def test_feed_items_no_limit(self):
        # no limit
        items = self.feed.items(limit=None)
        self.assertEqual(len(items), 20)
        self.assertEqual(items[0].id, self.response['items'][0]['id'])
        self.assertEqual(list(items)[-1].id, self.response['items'][19]['id'])

    def test_feed_items_offset(self):
        # offset
        items = self.feed.items(offset=18)
        self.assertEqual(len(items), 2)

        # offset and limit
        items = self.feed.items(offset=10, limit=5)
        self.assertEqual(len(items), 5)
