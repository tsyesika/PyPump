from __future__ import absolute_import

import six
from six.moves.urllib import parse

from tests import PyPumpTest


class WebPumpTest(PyPumpTest):
    """ Tests to ensure the WebPump works as it should do """
    def test_url_is_set(self):
        """ Tests that URL is provided with token for OAuth """
        self.assertTrue(isinstance(self.webpump.url, six.string_types))

        url = parse.urlparse(self.webpump.url)
        query = parse.parse_qs(url.query)

        self.assertEqual(url.netloc, self.webpump.client.webfinger.split("@", 1)[1])
        self.assertEqual(url.path, "/oauth/authorize")
