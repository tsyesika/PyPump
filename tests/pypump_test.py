from __future__ import absolute_import
from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from requests import exceptions as request_excs

from pypump import PyPump


class PyPumpTest(TestCase):
    @mock.patch("pypump.pypump.requests")
    def test_https_failover(self, requests_mock):
        store = mock.MagicMock()
        store.__iter__.return_value = []
        client = mock.Mock()
        verifier = mock.Mock()
        requests_mock.post.return_value.text = "%s=thingy&%s=secretthingy" % (PyPump.PARAM_TOKEN, PyPump.PARAM_TOKEN_SECRET)
        # re-add exceptions to mocked library
        requests_mock.exceptions = request_excs

        pump = PyPump(client, verifier, store=store)
        self.assertEqual(pump.protocol, "https")

        # verify == True
        fnc_mock = mock.Mock()
        fnc_mock.side_effect = request_excs.ConnectionError
        with self.assertRaises(request_excs.ConnectionError):
            pump._requester(fnc_mock, "")

        self.assertEqual(len(fnc_mock.call_args_list), 1)
        self.assertTrue(fnc_mock.call_args_list[0][0][0].startswith("https://"))
        self.assertEqual(pump.protocol, "https")

        # verify == False
        fnc_mock.reset_mock()
        pump.verify_requests = False
        with self.assertRaises(request_excs.ConnectionError):
            pump._requester(fnc_mock, "")

        self.assertEqual(len(fnc_mock.call_args_list), 2)
        self.assertTrue(fnc_mock.call_args_list[0][0][0].startswith("https://"))
        self.assertTrue(fnc_mock.call_args_list[1][0][0].startswith("http://"))
        # make sure that we're reset to https after
        self.assertEqual(pump.protocol, "https")
