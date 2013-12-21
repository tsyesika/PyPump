from __future__ import absolute_import
from tests import PyPumpTest
from dateutil.parser import parse
from pypump.models.activity import ActivityObject, Application


class ActivityTest(PyPumpTest):
    
    def setUp(self):
        super(ActivityTest, self).setUp()
        self.response.data = {
            "to": [{
                "objectType" : "person",
                "id" : "acct:testuser@example.com"
            }],
            "cc": [{
                "objectType" : "person",
                "id" : "acct:testuser3@example.com"
            }],
            "verb": "post",
            "generator": {
                "objectType" : "application",
                "id" : "testapp"
            },
            "object": {
                "objectType" : "test",
                "content" : "testing testing",
                "id" : "testid1"
            },
            "actor": {
                "objectType" : "person",
                "id" : "acct:testuser2@example.com"
            },          
            "updated": "2013-12-24T16:58:42Z",
            "links": {
                "self" : {
                    "href" : "https://example.com/api/activity/abc"
                }
            },
            "url": "https://example.com/testuser2/activity/xyz",
            "published": "2013-12-24T16:58:42Z",
            "content": "<a href='https://example.com/testuser2'>testuser2@example.com</a> posted <a href='https://example.com/testuser2/test/xyz'>a test</a>",
            "id": "https://example.com/api/activity/abc"
        }

    def test_unserialize(self):
        """ Tests activity unserialization is successful """
        activity = self.pump.Activity().unserialize(self.response.data)

        self.assertTrue(isinstance(activity, type(self.pump.Activity())))

        # Test unserialized object attributes
        self.assertTrue(isinstance(activity.to[0], type(self.pump.Person())))
        self.assertTrue(isinstance(activity.cc[0], type(self.pump.Person())))
        self.assertEqual(activity.verb, self.response["verb"])
        self.assertTrue(isinstance(activity.generator, Application))
        self.assertTrue(isinstance(activity.obj, ActivityObject))
        self.assertTrue(isinstance(activity.actor, type(self.pump.Person())))
        self.assertTrue(activity.updated, parse(self.response["updated"]))
        self.assertTrue(activity.links["self"]["href"], self.response["links"]["self"]["href"])
        self.assertEqual(activity.url, self.response["url"])
        self.assertTrue(activity.published, parse(self.response["published"]))
        self.assertEqual(activity.content, self.response["content"])
        self.assertEqual(activity.id, self.response["id"])

    def test_deleted_image(self):
        """ Activity with deleted image should have image obj with 'deleted' attribute set"""
        # copy default response and replace object with a deleted image for this test
        data = self.response.data.copy()
        data['object'] = {
            "objectType" : "image",
            "deleted" : "2013-12-24T16:58:22",
            "id" : "https://example.com/api/image/uuid",
            "published" : "2013-12-24T16:55:22",
            "updated" : "2013-12-24T16:58:22",
            "author" : {
                "objectType" : "person",
                "id" : "acct:testuser@example.com"
            }
        }

        activity = self.pump.Activity().unserialize(data)

        self.assertTrue(isinstance(activity.obj, type(self.pump.Image())))
        self.assertEqual(activity.obj.deleted, parse(data['object']['deleted']))

    def test_deleted_custom_object(self):
        """ Activity with deleted test object should have test obj with 'deleted' attribute set """
        # copy default response and replace object with a deleted object for this test
        data = self.response.data.copy()
        data['object'] = {
            "objectType" : "test",
            "deleted" : "2013-12-24T16:58:22",
            "id" : "https://example.com/api/test/uuid",
            "published" : "2013-12-24T16:55:22",
            "updated" : "2013-12-24T16:58:22",
            "author" : {
                "objectType" : "person",
                "id" : "acct:testuser@example.com"
            }
        }

        activity = self.pump.Activity().unserialize(data)

        self.assertTrue(isinstance(activity.obj, ActivityObject))
        self.assertEqual(activity.obj.deleted, parse(data['object']['deleted']))

