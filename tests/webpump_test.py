from __future__ import absolute_import

from six.moves.urllib import parse

from tests import PyPumpTest
from pypump import WebPump, Client

class WebPumpTest(PyPumpTest):
    """ Tests to ensure the WebPump works as it should do """

    def setUp(self):
        super(WebPumpTest, self).setUp()

        self.client = Client(
            webfinger="Test@somewhere.com",
            key="someKey",
            secret="someSecret",
            type="web"
        )

    def test_url_is_set(self):
        """ Tests that URL is provided with token for OAuth """
        pump = WebPump(self.client)
        self.assertOk(pump.url)

        url = parse(pump.url)
        query = parse.parse_qs(url.query)

        self.assertEqual(url.netloc, "somewhere.com")
        self.assertEqual(url.path, "/oauth/authorize")
        self.assertTrue("token" in query)
        self.assertEqual(pump.get_registration()[0], query["token"])
