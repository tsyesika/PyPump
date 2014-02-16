from __future__ import absolute_import

import unittest
import json
import six
import os

from pypump import WebPump, PyPump, Client

class Response(object):
    
    def __init__(self, url, data, params=None, status_code=200):
        self.url = url
        self.data = data
        self.status_code = status_code
        self.params = params or {}

    def __getitem__(self, key):
        return self.json()[key]

    def json(self):
        if isinstance(self.data, six.string_types):
            return json.loads(self.data)
        return self.data

    @property
    def content(self):
        return self.data

class Bucket(object):
    """ Container for useful test data """

    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)

class TestMixin(object):
    
    _response = None
    _unit_testing = True

    def __init__(self, *args, **kwargs):
        self.__oauth_testing = {
            'request': {
                'token': 'RequestToken',
                'token_secret': 'RequestTokenSecret',
            },
            'access': {
                'token': 'AccessToken',
                'token_secret': 'AccessTokenSecret',
            },
            'verifier': 'AVerifier',
        }

        # most of the time we don't want to go through oauth
        self.client = Client(
            webfinger="Test@example.com",
            key="AKey",
            secret="ASecret",
            name="PumpTest",
            type="native"
        )

        new_kwargs = dict(
            client=self.client,
        )

        self._response = kwargs.pop("response")
        self._testcase = kwargs.pop("testcase")

        new_kwargs.update(kwargs)

        super(TestMixin, self).__init__(*args, **new_kwargs)  

    def get_access(self, *args, **kwargs):
        """ Get verifier """
        return self.__oauth_testing['verifier']

    def request_token(self, *args, **kwargs):
        """ Gets request token and token secret """
        return self.__oauth_testing['request']

    def request_access(self, *args, **kwargs):
        """ Gets access token and token secret """
        return self.__oauth_testing['access']

    def set_status_code(self, status_code):
        if self._response is None:
            raise Exception("Response must be given before status code is specified")
        self._response.status_code = int(status_code)

    def get_status_code(self):
        return self._response.status_code

    def _requester(self, *args, **kwargs):
        """ Instead of requesting to a pump server we'll return the data we've been given """ 
        self._testcase.requests.append(Response(
            url=kwargs.get("endpoint", None),
            data=kwargs.get("data", None),
            params=kwargs.get("params", None)
        ))
        return self._response

class TestWebPump(TestMixin, WebPump):
    pass

class TestPump(TestMixin, PyPump):
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verifier_callback', self._callback)
        return super(TestPump, self).__init__(*args, **kwargs)

    def _callback(self, url):
        return 'a verifier'

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
        self.response = Response(url=None, data={})
        
        # These will be set when a request is made
        self.requests = []

        # Setup the bucket
        test_directory = os.path.abspath(os.path.dirname(__file__))
        self.bucket = Bucket(
            path_to_png=os.path.join(test_directory, "bucket", "test_image.png")
        )

        # make the pump object for testing.
        self.pump = TestPump(response=self.response, testcase=self)
        self.webpump = TestWebPump(response=self.response, testcase=self)

    @property
    def request(self):
        """ Returns the last (cronologically) request made """
        return self.requests[-1]
