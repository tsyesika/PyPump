from __future__ import absolute_import
from tests import PyPumpTest

class PersonTest(PyPumpTest):
    
    def test_unserialize(self):
        self.response.data = {
            "id": "acct:TestUser@example.com",
            "preferredUsername": "TestUser",
            "url": "http://example.com/TestUser",
            "displayName": "TestUser@example.com",
            "links": {
                "self": {
                    "href": "http://example.com/api/user/TestUser/profile",
                },
                "activity-inbox": {
                    "href": "http://example.com/api/user/TestUser/inbox",
                },
                "activity-outbox": {
                    "href": "http://example.com/api/user/TestUser/feed",
                },
            },
            "objectType": "person",
            "followers": {
                "url": "http://example.com/api/user/TestUser/followers",
                "totalItems": 72,
            },
            "following": {
                "url": "http://example.com/api/user/TestUser/following",
                "totalItems": 27,
            },
            "favorites": {
                "url": "http://example.com/api/user/TestUser/favorites",
                "totalItems": 7,
            },
            "location": {
                "objectType": "place",
                "displayName": "Home Tree, Pandora",
            },
            "summary": "I am a PyPump Test user, I am used for testing!",
            "image": {
                "url": "http://example.com/uploads/TestUser/some_image.jpg",
                "width": 96,
                "height": 96,
            },
            "pump_io": {
                "shared": False,
                "followed": False,
            },
            "updated": "2013-08-13T10:26:54Z",
            "liked": False,
            "shares": {
                "url": "http://example.com/api/person/BlahBlah/shares",
                "items": [],
            }
        }

        # Make the person object
        person = self.pump.Person("TestUser")

        # Test unserialization is correct
        self.assertEqual(person.id, self.response["id"])
        self.assertEqual(person.username, self.response["preferredUsername"])
        self.assertEqual(person.display_name, self.response["displayName"])
        self.assertEqual(person.url, self.response["url"])
        self.assertEqual(person.summary, self.response["summary"])

        # Test image model was made
        #self.assertTrue(isinstance(person.image, self.pump.Image))
        
        # Test location model was made
        self.assertTrue(isinstance(person.location, self.pump.Location)) 
