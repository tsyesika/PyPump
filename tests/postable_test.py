from __future__ import absolute_import
from tests import PyPumpTest

from pypump.models import Postable

class PostableTest(PyPumpTest):
    
    def setUp(self):
        super(PostableTest, self).setUp()

        self.userdata = {"objectType" : "person",
                         "id" : "acct:testuser@example.com"}
        self.collectiondata = {"objectType" : "collection", 
                               "id" : "http://activityschema.org/collection/public"}

        self.testuser = self.pump.Person().unserialize(self.userdata)
        self.testcollection = self.pump.Collection().unserialize(self.collectiondata)

        self.postable = Postable()
        self.postable._pump = self.pump

    def test_set_person(self):
        self.postable.to = self.testuser
        #is list item a pump person?
        self.assertTrue(isinstance(self.postable.to[0], type(self.pump.Person())))

    def test_set_collection(self):
        self.postable.to = self.testcollection
        #is list item a pump collection?
        self.assertTrue(isinstance(self.postable.to[0], type(self.pump.Collection())))

    def test_serialize(self):
        self.postable.to = [self.testuser, self.testcollection]

        data = self.postable.serialize()

        self.assertEqual(data["to"][0], self.userdata)
        self.assertEqual(data["to"][1], self.collectiondata)

