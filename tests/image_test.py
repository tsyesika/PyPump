from __future__ import absolute_import
from tests import PyPumpTest

class ImageTest(PyPumpTest):
    
    def setUp(self):
        super(ImageTest, self).setUp()
        self.response.data = {
            "url": "https://example.com/testuser/image/Pi9rux49S6C1Yhta0zbxyz",
            "content": "<p>I think i killed santa! :O.</p>\n",
            "displayName": "O M G",
            "id": "https://example.com/api/image/Pi9rux49S6C1Yhta0zbxyz",
            "author": {
                "objectType": "person",
                "id" : "acct:testuser@example.com",
            },
            "image": {
                "url": "https://example.com/uploads/testuser/2013/12/24/XMAS13_thumb.jpg",
                "height": 240,
                "width": 320
            },
            "fullImage": {
                "url": "https://example.com/uploads/testuser/2013/12/24/XMAS13.jpg",
                "width": 1280,
                "height": 960
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
                "totalItems": 0
            },
            "replies": {
                "url": "https://example.com/api/image/Pi9rux49S6C1Yhta0zbxyz/replies",
                "totalItems": 0
            },
            "shares": {
                "url": "https://example.com/api/image/Pi9rux49S6C1Yhta0zbxyz/shares",
                "totalItems": 0
            },
            "liked": "false",
            "pump_io": {
                "shared": "false"
            }
        }

    def test_unserialize(self):
        """ Tests image unserialization is successful """
        # Make the image object
        image = self.pump.Image().unserialize(self.response.data)

        # Test unserialization is correct
        self.assertEqual(image.id, self.response["id"])
        self.assertEqual(image.url, self.response["url"])
        self.assertEqual(image.thumbnail.url, self.response["image"]["url"])
        self.assertEqual(image.original.url, self.response["fullImage"]["url"])
        self.assertEqual(image.display_name, self.response["displayName"])
        self.assertEqual(image.content, self.response["content"])
        self.assertEqual(image.thumbnail.height, self.response["image"]["height"])
        self.assertEqual(image.thumbnail.width, self.response["image"]["width"])
        self.assertEqual(image.original.height, self.response["fullImage"]["height"])
        self.assertEqual(image.original.width, self.response["fullImage"]["width"])

    def test_upload_file(self):
        """ Test image can be uploaded succesfully """
        image = self.pump.Image(
            display_name="My lovely image",
            content="This is my sexy description"
        )

        # Upload an image from the bucket
        image.from_file(self.bucket.path_to_png)
        
        # Check image has my attributs as they were set
        self.assertEqual(image.display_name, "My lovely image")
        self.assertEqual(image.content, "This is my sexy description")

        # Test the data sent is correct.
        upload_request = self.requests[0] # It always happens to be the first request
        
        self.assertEqual(image.display_name, upload_request.params["title"])
        self.assertEqual(image.content, upload_request.params["description"])
        self.assertTrue(self.bucket.path_to_png.endswith(upload_request.params["qqfile"]))


        # Test that the data is the same
        binary_image = open(self.bucket.path_to_png, "r").read()
        self.assertEqual(upload_request.data, binary_image)
