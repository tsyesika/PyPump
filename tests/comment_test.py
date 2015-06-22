from __future__ import absolute_import

from dateutil.parser import parse

from tests import PyPumpTest


class CommentTest(PyPumpTest):
    def setUp(self):
        super(CommentTest, self).setUp()
        self.maxidata = {
            "content": "test content",
            "inReplyTo": {
                "objectType": "note",
                "id": "noteid"
            },
            "objectType": "comment",
            "author": {
                "objectType": "person",
                "id": "acct:testuser@example.com"
            },
            "published": "2014-01-04T17:39:21Z",
            "updated": "2014-01-04T17:39:21Z",
            "links": {
                "self": {
                    "href": "https://example.com/api/comment/UOsxSKbITXixW5r_HAyO2A"
                }
            },
            "likes": {
                "url": "https://example.com/api/comment/UOsxSKbITXixW5r_HAyO2A/likes",
                "totalItems": 0
            },
            "replies": {
                "url": "https://example.com/api/comment/UOsxSKbITXixW5r_HAyO2A/replies",
                "totalItems": 0
            },
            "shares": {
                "url": "https://example.com/api/comment/UOsxSKbITXixW5r_HAyO2A/shares",
                "totalItems": 0
            },
            "url": "https://example.com/testuser/comment/UOsxSKbITXixW5r_HAyO2A",
            "id": "https://example.com/api/comment/UOsxSKbITXixW5r_HAyO2A",
            "liked": True,
            "pump_io": {
                "shared": False
            }
        }

        self.minidata = {
            "objectType": "comment",
            "id": "https://example.com/api/comment/8f40pLbdTQ-uY-ADbQrhwg",
        }

        # used in test_comment_attr_*
        self.maxicomment = self.pump.Comment().unserialize(self.maxidata)

    def test_comment(self):
        self.response.data = self.maxidata
        comment = self.pump.Comment('test')
        self.assertTrue(isinstance(comment, type(self.pump.Comment())))
        self.assertEqual(comment.__str__(), 'comment by unknown')

    def test_comment_minimal_unserialize(self):
        comment = self.pump.Comment().unserialize(self.minidata)
        self.assertTrue(isinstance(comment, type(self.pump.Comment())))

    def test_comment_unserialize(self):
        comment = self.pump.Comment().unserialize(self.maxidata)
        self.assertTrue(isinstance(comment, type(self.pump.Comment())))

    def test_comment_attr_content(self):
        self.assertTrue(hasattr(self.maxicomment, 'content'))
        self.assertEqual(self.maxicomment.content, self.maxidata["content"])

    def test_comment_attr_published(self):
        self.assertTrue(hasattr(self.maxicomment, 'published'))
        self.assertEqual(self.maxicomment.published, parse(self.maxidata["published"]))

    def test_comment_attr_updated(self):
        self.assertTrue(hasattr(self.maxicomment, 'updated'))
        self.assertEqual(self.maxicomment.updated, parse(self.maxidata["updated"]))

    def test_comment_attr_links(self):
        self.assertTrue(hasattr(self.maxicomment, 'links'))
        self.assertEqual(self.maxicomment.links['self'], self.maxidata["links"]["self"]["href"])

    def test_comment_attr_url(self):
        self.assertTrue(hasattr(self.maxicomment, 'url'))
        self.assertEqual(self.maxicomment.url, self.maxidata["url"])

    def test_comment_attr_id(self):
        self.assertTrue(hasattr(self.maxicomment, 'id'))
        self.assertEqual(self.maxicomment.id, self.maxidata["id"])

    def test_comment_attr_liked(self):
        self.assertTrue(hasattr(self.maxicomment, 'liked'))
        self.assertEqual(self.maxicomment.liked, self.maxidata["liked"])

    def test_comment_attr_in_reply_to(self):
        self.assertTrue(hasattr(self.maxicomment, 'in_reply_to'))
        self.assertTrue(isinstance(self.maxicomment.in_reply_to, type(self.pump.Note())))

    def test_comment_attr_author(self):
        self.assertTrue(hasattr(self.maxicomment, 'author'))
        self.assertTrue(isinstance(self.maxicomment.author, type(self.pump.Person())))
