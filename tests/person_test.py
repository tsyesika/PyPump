from __future__ import absolute_import
from tests import PyPumpTest
from pypump.models.place import Place

class PersonTest(PyPumpTest):
    
    def setUp(self):
        super(PersonTest, self).setUp()
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
                "totalItems": 720,
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
    
    def test_follow(self):
        """ Tests that pypump sends correct data when attempting to follow a person """
        person = self.pump.Person("TestUser")
        
        # PyPump now expects the object returned back to it
        self.response.data = {"verb": "follow", "object": self.response.data}
        person.follow()

        # Test verb is 'follow'
        self.assertEquals(self.request["verb"], "follow")

        # Test ID is the correct ID
        self.assertEquals(person.id, self.request["object"]["id"])
        
        # Ensure object type is correct
        self.assertEquals(person.objectType, self.request["object"]["objectType"])

    def test_update(self):
        """ Test that a update works """
        person = self.pump.Person("TestUser")
        person.summary = "New summary!"
        person.display_name = "New user"
        
        self.response.data = {
            "verb": "update",
            "object": {
                "id": person.id,
                "summary": person.summary,
                "displayName": person.display_name,
                "objectType": "person",
            },
        }

        person.update()

        self.assertEqual(self.request["verb"], "update")
        self.assertEqual(self.request["object"]["id"], person.id)
        self.assertEqual(self.request["object"]["objectType"], person.objectType)
        self.assertEqual(self.request["object"]["summary"], person.summary)
        self.assertEqual(self.request["object"]["displayName"], person.display_name)

    def test_unfollow(self):
        """ Test that you can unfollow a person """
        person = self.pump.Person("TestUser")

        self.response.data = {"verb": "stop-following", "object": self.response.data}
        person.unfollow()

        self.assertEquals(self.request["verb"], "stop-following")
        self.assertEquals(self.request["object"]["id"], person.id)
        self.assertEquals(self.request["object"]["objectType"], person.objectType) 

    def test_minimal_unserialize(self):
        """ Test the smallest amount of data can be given to unserialize """
        self.response.data = {
            "id": "acct:TestUser@example.com",
            "objectType": "person",
        }

        person = self.pump.Person("TestUser")

        self.assertEquals(self.response["id"], person.id)
        self.assertEquals(self.response["objectType"], person.objectType)

    def test_unserialize(self):
        """ Tests person unserialization is successful """
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
        
        # Test place model was made
        self.assertTrue(isinstance(person.location, Place)) 
