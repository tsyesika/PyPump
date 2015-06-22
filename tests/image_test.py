from __future__ import absolute_import

from tests import PyPumpTest


class ImageTest(PyPumpTest):
    def setUp(self):
        super(ImageTest, self).setUp()
        self.imgdata = {
            "url": "https://example.com/testuser/image/Pi9rux49S6C1Yhta0zbxyz",
            "content": "<p>I think i killed santa! :O.</p>\n",
            "displayName": "O M G",
            "id": "https://example.com/api/image/Pi9rux49S6C1Yhta0zbxyz",
            "author": {
                "objectType": "person",
                "id": "acct:testuser@example.com",
            },
            "image": {
                "url": "https://example.com/uploads/testuser/2013/12/24/XMAS13_thumb.jpg",
                "height": 240,
                "width": 320,
            },
            "fullImage": {
                "url": "https://example.com/uploads/testuser/2013/12/24/XMAS13.jpg",
                "width": 1280,
                "height": 960,
            },
            "objectType": "image",
            "published": "2013-12-24T23:23:11Z",
            "updated": "2013-12-24T23:23:13Z",
            "links": {
                "self": {
                    "href": "https://example.com/api/image/Pi9rux49S6C1Yhta0zbxyz"
                }
            },
            "likes": {
                "url": "https://example.com/api/image/Pi9rux49S6C1Yhta0zbxyz/likes",
                "totalItems": 0,
            },
            "replies": {
                "url": "https://example.com/api/image/Pi9rux49S6C1Yhta0zbxyz/replies",
                "totalItems": 0,
            },
            "shares": {
                "url": "https://example.com/api/image/Pi9rux49S6C1Yhta0zbxyz/shares",
                "totalItems": 0,
            },
            "liked": "false",
            "pump_io": {
                "shared": "false",
            },
        }

        self.mini_data = {
            "objectType": "image",
            "id": "foo",
            "image": {
                "url": "https://example.com/uploads/testuser/2013/12/24/XMAS13_thumb.jpg",
                "height": 240,
                "width": 320,
            }
        }

        self.response.data = {
            "verb": "post",
            "object": self.imgdata,
        }

    def test_create_empty(self):
        image = self.pump.Image()

        # object to string
        self.assertEqual(image.__str__(), 'image by unknown')

    def test_mini_unserialize(self):
        image = self.pump.Image().unserialize(self.mini_data)

    def test_unserialize(self):
        """ Tests image unserialization is successful """
        # Make the image object
        image = self.pump.Image().unserialize(self.imgdata)

        # object is Image instance
        self.assertTrue(isinstance(image, type(self.pump.Image())))

        # object to string
        self.assertEqual(image.__str__(), 'image by testuser@example.com')

        # Test unserialization is correct
        self.assertEqual(image.id, self.imgdata["id"])
        self.assertEqual(image.url, self.imgdata["url"])
        self.assertEqual(image.thumbnail.url, self.imgdata["image"]["url"])
        self.assertEqual(image.original.url, self.imgdata["fullImage"]["url"])
        self.assertEqual(image.display_name, self.imgdata["displayName"])
        self.assertEqual(image.content, self.imgdata["content"])
        self.assertEqual(image.thumbnail.height, self.imgdata["image"]["height"])
        self.assertEqual(image.thumbnail.width, self.imgdata["image"]["width"])
        self.assertEqual(image.original.height, self.imgdata["fullImage"]["height"])
        self.assertEqual(image.original.width, self.imgdata["fullImage"]["width"])

    def test_upload_file(self):
        """ Test image can be uploaded succesfully """
        image = self.pump.Image(
            display_name="My lovely image",
            content="This is my sexy description"
        )

        # Check image has my attributs as they were set
        self.assertEqual(image.display_name, "My lovely image")
        self.assertEqual(image.content, "This is my sexy description")

        # Upload an image from the bucket
        image.from_file(self.bucket.path_to_png)

        # Test the data sent is correct.
        upload_request = self.requests[0]  # It always happens to be the first request

        # Test that the data is the same
        binary_image = open(self.bucket.path_to_png, "rb").read()
        self.assertEqual(upload_request.data, binary_image)
