from __future__ import absolute_import

from pypump import Client
from tests import PyPumpTest


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

        # Check we're registering a new client and sent correct data
        self.assertEqual(self.request["type"], "client_associate")
        self.assertEqual(self.request["application_type"], "native")

        # Check we got back the key, secret and expirey correctly
        self.assertEqual(client.key, self.response.data["client_id"])
        self.assertEqual(client.secret, self.response.data["client_secret"])
        self.assertEqual(client.expirey, self.response.data["expires_at"])

    def test_full_client_registration(self):
        """ Test a full client registration can take place """
        logo = "https://a.website.com/some_picture.png"
        contacts = ["dead@beef.com", "beef@dead.com"]

        client = Client(
            webfinger="TestUser@example.com",
            name="PyPumpTestClient",
            type="web",
            logo=logo,
            contacts=contacts
        )

        client.set_pump(self.pump)
        client.register()

        # Check data was sent correctly
        self.assertEqual(self.request["type"], "client_associate")
        self.assertEqual(self.request["logo_url"], logo)
        self.assertEqual(self.request["contacts"], " ".join(contacts))

        # Check we get back what we should
        self.assertEqual(self.response.data["client_id"], client.key)
        self.assertEqual(self.response.data["client_secret"], client.secret)
        self.assertEqual(self.response.data["expires_at"], client.expirey)

    def test_client_update(self):
        """ Tests that a client can be updated """
        # First make the client which we'll update
        client = Client(
            webfinger="TestUser@example.com",
            type="web"
        )

        client.set_pump(self.pump)
        client.register()

        # Now try and update the client
        client.type = "native"
        client.update()

        self.assertEqual(self.request["type"], "client_update")
        self.assertEqual(self.request["application_type"], "native")
