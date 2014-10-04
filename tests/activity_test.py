#-*- coding: utf-8 -*-
from __future__ import absolute_import
import six
from tests import PyPumpTest
from dateutil.parser import parse
from pypump.models.activity import Activity, Application
from pypump.models import PumpObject


class ActivityTest(PyPumpTest):
    
    def setUp(self):
        super(ActivityTest, self).setUp()
        self.response.data = {
            "objectType":"activity",
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
            "received": "2013-12-24T16:58:42Z",
            "content": "<a href='https://example.com/testuser2'>testuser2@example.com</a> posted <a href='https://example.com/testuser2/test/xyz'>a test</a>",
            "id": "https://example.com/api/activity/abc"
        }

        self.activity = Activity(pypump=self.pump).unserialize(self.response.data)

    def test_activity(self):
        #instance is Activity
        self.assertTrue(isinstance(self.activity, Activity))

        #object to string
        self.assertEqual(self.activity.__str__(), self.activity._striptags(self.activity.content))
        self.activity.content = u'Test användarson posted test'
        if six.PY3:
            self.assertEqual(self.activity.__str__(), self.activity.content)
        else:
            self.assertEqual(self.activity.__str__(), self.activity.content.encode('utf-8'))
    def test_activity_attr_verb(self):
        self.assertTrue(hasattr(self.activity, 'verb'))
        self.assertEqual(self.activity.verb, self.response["verb"])
    def test_activity_attr_generator(self):
        self.assertTrue(hasattr(self.activity, 'generator'))
        self.assertTrue(isinstance(self.activity.generator, Application))
    def test_activity_attr_obj(self):
        self.assertTrue(hasattr(self.activity, 'obj'))
        self.assertTrue(isinstance(self.activity.obj, PumpObject))
    def test_activity_attr_actor(self):
        self.assertTrue(hasattr(self.activity, 'actor'))
        self.assertTrue(isinstance(self.activity.actor, type(self.pump.Person())))
    def test_activity_attr_updated(self):
        self.assertTrue(hasattr(self.activity, 'updated'))
        self.assertTrue(self.activity.updated, parse(self.response["updated"]))
    def test_activity_attr_links(self):
        self.assertTrue(hasattr(self.activity, 'links'))
        self.assertTrue(self.activity.links["self"], self.response["links"]["self"]["href"])
    def test_activity_attr_url(self):
        self.assertTrue(hasattr(self.activity, 'url'))
        self.assertEqual(self.activity.url, self.response["url"])
    def test_activity_attr_published(self):
        self.assertTrue(hasattr(self.activity, 'published'))
        self.assertTrue(self.activity.published, parse(self.response["published"]))
    def test_activity_attr_received(self):
        self.assertTrue(hasattr(self.activity, 'received'))
        self.assertTrue(self.activity.received, parse(self.response["received"]))
    def test_activity_attr_content(self):
        self.assertTrue(hasattr(self.activity, 'content'))
        self.assertEqual(self.activity.content, self.response["content"])
    def test_activity_attr_id(self):
        self.assertTrue(hasattr(self.activity, 'id'))
        self.assertEqual(self.activity.id, self.response["id"])

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

        activity = Activity(pypump=self.pump).unserialize(data)

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

        activity = Activity(pypump=self.pump).unserialize(data)

        self.assertTrue(isinstance(activity.obj, PumpObject))
        self.assertEqual(activity.obj.deleted, parse(data['object']['deleted']))

