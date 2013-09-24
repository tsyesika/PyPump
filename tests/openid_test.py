from __future__ import absolute_import
from tests import PyPumpTest

from pypump.openid import OpenID

class OpenIDTest(PyPumpTest):
    """ Test that the clients can register and update via OpenID """

    def setUp(self):
        super(OpenIDTest, self).setUp()

        self.response.data = {
            "client_id": "MJEgFWzTk7yI3wqbv7Nvuw",
            "client_secret": "SiBOo5NVOSaljxA2auudgu4W4ufCwYVMnbkw5w3KOzY",
            "expires_at": 0,
        }

    def test_minimal_client_registeration(self):
        """ Test client registeration with minimal amount of data """
        openid = OpenID(
            server="TestUser@example.com",
            client_name="PyPumpTestClient",
            application_type="native",
        )

        consumer = openid.register_client()

        self.assertEqual(consumer.key, self.response.data["client_id"])
        self.assertEqual(consumer.secret, self.response.data["client_secret"])
        self.assertEqual(consumer.expirey, self.response.data["expires_at"])

    def test_full_client_registration(self):
        """ Test a full client registration can take place """
        logo_url = "https://a.website.com/some_picture.png"

        openid = OpenID(
            server="TestUser@example.com",
            client_name="PyPumpTestClient",
            application_type="web",
            logo_url=logo_url,
        )

        consumer = openid.register_client()

        self.assertEqual(self.request["logo_url"], logo_url) 
