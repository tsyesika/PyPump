from __future__ import absolute_import
from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from pypump import PyPump


class PyPumpTest(TestCase):
    @mock.patch("pypump.pypump.requests")
    def test_https_failover(self, requests_mock):
        store = mock.MagicMock()
        store.__iter__.return_value = []
        client = mock.Mock()
        verifier = mock.Mock()
        requests_mock.post.return_value.text = "%s=thingy&%s=secretthingy" % (PyPump.PARAM_TOKEN, PyPump.PARAM_TOKEN_SECRET)

        pump = PyPump(client, verifier, store=store)
        self.assertEqual(pump.protocol, "https")
