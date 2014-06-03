from __future__ import absolute_import
from tests import PyPumpTest
from dateutil.parser import parse

class NoteTest(PyPumpTest):
    
    def setUp(self):
        super(NoteTest, self).setUp()
        self.maxidata = {
            "displayName" : "note title",
            "content": "<p>note text</p>\n",
            "objectType": "note",
            "published": "2013-12-23T05:14:54Z",
            "updated": "2013-12-23T05:14:54Z",
            "links": {
                "self": {
                    "href": "https://example.com/api/note/8f40pLbdTQ-uY-ADbQrhwg"
                }
            },
            "likes": {
                "url": "https://example.com/api/note/8f40pLbdTQ-uY-ADbQrhwg/likes",
                "totalItems": 0
            },
            "replies": {
                "url": "https://example.com/api/note/8f40pLbdTQ-uY-ADbQrhwg/replies",
                "totalItems": 0
            },
            "shares": {
                "url": "https://example.com/api/note/8f40pLbdTQ-uY-ADbQrhwg/shares",
                "totalItems": 0
            },
            "url": "https://example.com/testuser/note/8f40pLbdTQ-uY-ADbQrhwg",
            "id": "https://example.com/api/note/8f40pLbdTQ-uY-ADbQrhwg",
            "liked": False,
            "pump_io": {
                "shared": False
            },
            "to": [{
                "objectType" : "person",
                "id" : "acct:notetestuser@example.com"
            }],
            "cc": [{
                "objectType" : "collection",
                "id" : "http://activityschema.org/collection/public"
            }],
        }

        self.minidata = {
            "objectType" : "note",
            "id": "https://example.com/api/note/8f40pLbdTQ-uY-ADbQrhwg",
        }

        #used in test_note_attr_*
        self.maxinote = self.pump.Note().unserialize(self.maxidata)

    def test_note_create(self):
        self.response.data = self.maxidata
        note = self.pump.Note('test')
        self.assertTrue(isinstance(note, type(self.pump.Note())))
    def test_note_minimal_unserialize(self):
        note = self.pump.Note().unserialize(self.minidata)
        self.assertTrue(isinstance(note, type(self.pump.Note())))
    def test_note_unserialize(self):
        note = self.pump.Note().unserialize(self.maxidata)
        self.assertTrue(isinstance(note, type(self.pump.Note())))
    def test_note_attr_display_name(self):
        self.assertTrue(hasattr(self.maxinote, 'display_name'))
        self.assertEqual(self.maxinote.display_name, self.maxidata["displayName"])
    def test_note_attr_content(self):
        self.assertTrue(hasattr(self.maxinote, 'content'))
        self.assertEqual(self.maxinote.content, self.maxidata["content"])
    def test_note_attr_published(self):
        self.assertTrue(hasattr(self.maxinote, 'published'))
        self.assertEqual(self.maxinote.published, parse(self.maxidata["published"]))
    def test_note_attr_updated(self):
        self.assertTrue(hasattr(self.maxinote, 'updated'))
        self.assertEqual(self.maxinote.updated, parse(self.maxidata["updated"]))
    def test_note_attr_links(self):
        self.assertTrue(hasattr(self.maxinote, 'links'))
        self.assertEqual(self.maxinote.links['self'], self.maxidata["links"]["self"]["href"])
    def test_note_attr_url(self):
        self.assertTrue(hasattr(self.maxinote, 'url'))
        self.assertEqual(self.maxinote.url, self.maxidata["url"])
    def test_note_attr_id(self):
        self.assertTrue(hasattr(self.maxinote, 'id'))
        self.assertEqual(self.maxinote.id, self.maxidata["id"])
    def test_note_attr_liked(self):
        self.assertTrue(hasattr(self.maxinote, 'liked'))
        self.assertEqual(self.maxinote.liked, self.maxidata["liked"])
    def test_note_attr_to(self):
        self.assertTrue(hasattr(self.maxinote, 'to'))
        self.assertTrue(isinstance(self.maxinote.to[0], type(self.pump.Person())))
    def test_note_attr_cc(self):
        self.assertTrue(hasattr(self.maxinote, 'cc'))
        self.assertTrue(isinstance(self.maxinote.cc[0], type(self.pump.Collection())))

