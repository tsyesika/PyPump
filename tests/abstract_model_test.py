from __future__ import absolute_import
from tests import PyPumpTest

from pypump.models import AbstractModel

class AbstractModelTest(PyPumpTest):
    
    def setUp(self):
        super(AbstractModelTest, self).setUp()

        self.model = AbstractModel(pypump=self.pump)

        self.person_json = {
            "preferredUsername": "testuser",
            "url": "https://example.com/testuser",
            "displayName": "TestUser",
            "links": {
                "self": {
                    "href": "https://example.com/api/user/testuser/profile"
                },
                "activity-inbox": {
                    "href": "https://example.com/api/user/testuser/inbox"
                },
                "activity-outbox": {
                    "href": "https://example.com/api/user/testuser/feed"
                }
            },
            "objectType": "person",
            "updated": "2013-08-05T20:24:38Z",
            "published": "2013-03-26T18:00:09Z",
            "followers": {
                "url": "https://example.com/api/user/testuser/followers"
            },
            "following": {
                "url": "https://example.com/api/user/testuser/following"
            },
            "favorites": {
                "url": "https://example.com/api/user/testuser/favorites"
            },
            "lists": {
                "url": "https://example.com/api/user/testuser/lists/person"
            },
            "pump_io": { },
            "location": {
                "displayName": "North Pole",
                "objectType": "place"
            },
            "summary": "test summary",
            "liked": False,
            "image": {
                "url": "https://example.com/uploads/testuser/2013/3/27/n76Spw_thumb.jpg",
                "width": 96,
                "height": 96
            },
            "id": "acct:testuser@example.com"
        }

        self.note_json = {
            "objectType": "note",
            "content": "Test content",
            "published": "2013-12-22T06:27:13Z",
            "updated": "2013-12-22T06:27:13Z",
            "links": {
                "self": {
                    "href": "https://example.com/api/note/CkFucl8qSmald3qAHTllTw"
                }
            },
            "likes": {
                "url": "https://example.com/api/note/CkFucl8qSmald3qAHTllTw/likes",
                "totalItems": 0,
                "pump_io": {
                    "proxyURL": "https://example.com/api/proxy/pjwd3nrLR4O_gBYCvAp4mQ"
                }
            },
            "replies": {
                "url": "https://example.com/api/note/CkFucl8qSmald3qAHTllTw/replies",
                "totalItems": 0,
                "pump_io": {
                    "proxyURL": "https://example.com/api/proxy/99TGqO0ISoazXh-Q_nTinQ"
                }
            },
            "shares": {
                "url": "https://example.com/api/note/CkFucl8qSmald3qAHTllTw/shares",
                "totalItems": 0,
            },
            "url": "https://example.com/testuser/note/CkFucl8qSmald3qAHTllTw",
            "liked": False,
            "pump_io": {
                "shared": False,
                "proxyURL": "https://example.com/api/proxy/wEPeXhnqRw2E8p0j68QO_g"
            },
            "id": "https://example.com/api/note/CkFucl8qSmald3qAHTllTw"
        }

    def test_add_links_person(self):
        "add person object : add_links(person)"
        test_obj = self.person_json
        self.model.add_links(test_obj)

        self.assertTrue(self.model.links.get('self'))
        self.assertEqual(self.model.links['self'], test_obj['links']['self']['href'])
        self.assertTrue(self.model.links.get('activity-inbox'))
        self.assertEqual(self.model.links['activity-inbox'], test_obj['links']['activity-inbox']['href'])

    def test_add_links_note(self):
        "add notes object : add_links(note)"
        test_obj = self.note_json
        self.model.add_links(test_obj)

        self.assertTrue(self.model.links.get('self'))
        self.assertEqual(self.model.links['self'], test_obj['links']['self']['href'])

    def test_add_links_note_links(self):
        "add note's links object : add_links(note['links'])"
        test_obj = self.note_json
        self.model.add_links(test_obj['links'])

        self.assertTrue(self.model.links.get('self'))
        self.assertEqual(self.model.links['self'], test_obj['links']['self']['href'])

    def test_add_links_note_shares_no_proxy(self):
        "note's shares link without a proxyurl"
        test_obj = self.note_json
        self.model.add_links(test_obj)

        self.assertTrue(self.model.links.get('shares'))
        self.assertEqual(self.model.links['shares'], test_obj['shares']['url'])

    def test_add_links_note_likes_proxy(self):
        "note's likes link with a proxyurl"
        test_obj = self.note_json
        self.model.add_links(test_obj)

        self.assertTrue(self.model.links.get('likes'))
        self.assertEqual(self.model.links['likes'], test_obj['likes']['pump_io']['proxyURL'])
