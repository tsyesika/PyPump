from __future__ import absolute_import
from tests import PyPumpTest

from pypump import Client

class ClientTest(PyPumpTest):
    """ Test that the clients can register and update via OpenID """

    def setUp(self):
        super(ClientTest, self).setUp()

        self.response.data = {
            "client_id": "MJEgFWzTk7yI3wqbv7Nvuw",
            "client_secret": "SiBOo5NVOSaljxA2auudgu4W4ufCwYVMnbkw5w3KOzY",
            "expires_at": 0,
        }

    def test_minimal_client_registeration(self):
        """ Test client registeration with minimal amount of data """
        client = Client(
            webfinger="TestUser@example.com",
            type="native",
        )

        client.set_pump(self.pump)
        client.register()

        self.assertEqual(client.key, self.response.data["client_id"])
        self.assertEqual(client.secret, self.response.data["client_secret"])
        self.assertEqual(client.expirey, self.response.data["expires_at"])

    def test_full_client_registration(self):
        """ Test a full client registration can take place """
        logo = "https://a.website.com/some_picture.png"

        client = Client(
            webfinger="TestUser@example.com",
            name="PyPumpTestClient",
            type="web",
            logo=logo,
        )

        client.set_pump(self.pump)
        client.register()

        self.assertEqual(self.request["logo_url"], logo) 
