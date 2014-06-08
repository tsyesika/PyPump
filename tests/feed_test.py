#-*- coding: utf-8 -*-
from tests import PyPumpTest
from pypump.models.feed import Feed, ItemList
import unittest, json
import six

class FeedTest(PyPumpTest):
    
    def setUp(self):
        super(FeedTest, self).setUp()
        #we dump to string since to make it readonly (we dont want to pop the items list by reference)
        self.response.data = json.dumps({
            "displayName": "Followers for Testuser",
            "url": "https://example.com/api/user/testuser/followers",
            "objectTypes": [
                "person"
            ],
            "items": [{"objectType" : "person", "id" : "acct:testuser%d@example.com" % i} for i in range(20)]
            ,
            "totalItems": 25,
            "author": { "objectType" : "person", "id" : "acct:testuser@example.com"},
            "links": {
                "self": {"href": "https://example.com/api/user/testuser/followers?offset=0&count=20"},
                "current": {"href": "https://example.com/api/user/testuser/followers"},
                "prev": {"href": "https://example.com/api/user/testuser/followers?since=acct%3Atestuser0%40example.com"},
                "next": {"href": "https://example.com/api/user/testuser/followers?before=acct%3Atestuser19%40example.com"}
            }
        })

        self.feed = Feed('https://example.com/api/user/testuser/followers', pypump=self.pump)

    def test_feed(self):
        #is a Feed object
        self.assertTrue(isinstance(self.feed, Feed))
        #object to string
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
        self.assertTrue(hasattr(self.feed, 'items'))
        self.assertTrue(isinstance(self.feed.items, ItemList))
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
        sliceditems = list(self.feed[:5])
        self.assertEqual(len(sliceditems), 5)
        self.assertEqual(sliceditems[0].id, self.response['items'][0]['id'])
        self.assertEqual(sliceditems[-1].id, self.response['items'][4]['id'])
    """
    ehh, how do we request offset in test code?
    def test_feed_slice_3_to_6(self):

        sliceditems = list(self.feed[3:6])
        self.assertEqual(len(sliceditems), 3)
        self.assertEqual(sliceditems[0].id, self.response['items'][3]['id'])
        self.assertEqual(sliceditems[-1].id, self.response['items'][5]['id'])
    """
