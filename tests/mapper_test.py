from __future__ import absolute_import

from pypump.models import Mapper, PumpObject
from pypump.models.activity import Application
from tests import PyPumpTest


class MapperTest(PyPumpTest):
    def setUp(self):
        super(MapperTest, self).setUp()

    def test_get_object_unknown(self):
        """ Test creation of unknown activity model """
        test_data = {
            "objectType": "food",  # pypump.models.PumpObject
            "id": "https://example.com/api/food/pancake-v0.1a",
            "url": "https://example.com/food/pancake-v0.1a",
            "content": "flour, sugar, eggs, milk, beans",
            "displayName": "Pancakes (test version)",
            "author": {
                "objectType": "person",
                "id": "acct:badcook@example.com"
            }
        }
        test_obj = Mapper(pypump=self.pump).get_object(test_data)

        # Test unserialization is correct
        self.assertEqual(test_obj.object_type, test_data["objectType"])
        self.assertEqual(test_obj.id, test_data["id"])
        self.assertEqual(test_obj.url, test_data["url"])
        self.assertEqual(test_obj.content, test_data["content"])
        self.assertEqual(test_obj.display_name, test_data["displayName"])

        # test_obj should be PumpObject
        self.assertTrue(isinstance(test_obj, PumpObject))

        # test_obj.author should be PyPump.Person
        self.assertTrue(isinstance(test_obj.author, type(self.pump.Person())))

    def test_get_pump_model(self):
        """ Test creation of PyPump model """
        test_data = {
            "objectType": "person",  # pypump.models.person.Person
            "id": "acct:testuser@example.com"
        }
        test_obj = Mapper(pypump=self.pump).get_object(test_data)

        # Test person model was made
        self.assertTrue(isinstance(test_obj, type(self.pump.Person())))

    def test_get_activity_model(self):
        """ Test creation of known activity model """
        test_data = {
            "objectType": "application",  # pypump.models.activity.Application
            "id": "coolapp1.2",
            "displayName": "Cool app"
        }
        test_obj = Mapper(pypump=self.pump).get_object(test_data)

        self.assertTrue(isinstance(test_obj, Application))
