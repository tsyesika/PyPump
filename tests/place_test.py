# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six

from tests import PyPumpTest


class PlaceTest(PyPumpTest):
    def setUp(self):
        super(PlaceTest, self).setUp()
        self.data = {
            "objectType": "place",
            "displayName": "Home Tree, Pandora",
        }

    def test_place_create(self):
        self.response.data = self.data
        place = self.pump.Place()

        # object is Place instance
        self.assertTrue(isinstance(place, type(self.pump.Place())))

        # object to string
        self.assertEqual(place.__str__(), 'unknown')

    def test_place_unserialize(self):
        # unserialize
        place = self.pump.Place().unserialize(self.data)

        # object to string
        self.assertEqual(place.__str__(), self.data['displayName'])
        place.display_name = u'Malmö, Sweden'

        if six.PY3:
            self.assertEqual(place.__str__(), place.display_name)
        else:
            self.assertEqual(place.__str__(), place.display_name.encode('utf-8'))
