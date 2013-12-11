from __future__ import absolute_import

import unittest
import json
import six

from pypump import PyPump, Client

class Response(object):
    
    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def __getitem__(self, key):
        return self.json()[key]

    def json(self):
        if isinstance(self.data, six.string_types):
            return json.loads(self.data)
        return self.data

    @property
    def content(self):
        return self.data

class TestPump(PyPump):
    
    _response = None
    _unit_testing = True

    def __init__(self, *args, **kwargs):
        # most of the time we don't want to go through oauth
        client = Client(
            webfinger="Test@example.com",
            key="AKey",
            secret="ASecret",
            name="PumpTest",
            type="native"
        )

        new_kwargs = dict(
            client=client,
            token="AToken",
            secret="ATokenSecret",
            )

        self._response = kwargs.pop("response")
        self._testcase = kwargs.pop("testcase")

        new_kwargs.update(kwargs)
        super(TestPump, self).__init__(*args, **new_kwargs)

    def set_status_code(self, status_code):
        if self._response is None:
            raise Exception("Response must be given before status code is specified")
        self._response.status_code = int(status_code)

    def get_status_code(self):
        return self._response.status_code

    def _requester(self, *args, **kwargs):
        """ Instead of requesting to a pump server we'll return the data we've been given """
        self._testcase.request = Response(kwargs.get("data", None))
        self._testcase.params = kwargs.get("params", None)
        return self._response

class PyPumpTest(unittest.TestCase):
    """
        This is the base test class for PyPump.
        
        This will provide a testing PyPump class which allows you to easily
        test code in PyPump. It easily allows you to specify pump server return
        values.

    """

    def setUp(self):
        """ This will setup everything needed to test PyPump """
        # response from server, any string will be treated as a json string
        self.response = Response({})
        
        # These will be set when a request is made
        self.request = None
        self.params = None
        
        # make the pump object for testing.
        self.pump = TestPump(response=self.response, testcase=self)
