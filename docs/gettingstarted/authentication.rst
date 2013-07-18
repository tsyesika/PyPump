=============
Authorization
=============

What you need to know
---------------------

Pump.io uses oauth 1.0 with dynamic client registration, this available through a lot of libraries, PyPump uses `oauthlib <https://github.com/idan/oauthlib>`_ and a wrapper around it to provide an provide an interface with the `requests <http://docs.python-requests.org/en/latest/>`_ library - `requests-oauthlib <https://github.com/requests/requests-oauthlib>`. All of that is handled by PyPump however there are some things to know.

OAuth works by exchanging pre-established client credentials and token, you however have to provide those each time you make instantiate the PyPump object. You will have to provide a mechanism to store these so that you can you can provide them the next time.

Example
-------
The following will create (for the first time) a connection to a pump.io server for the user Tsyesika@io.theperplexingpariah.co.uk for my client named "Test.io"::

    >>> from pypump import PyPump
    >>> pump = PyPump("Tsyesika@io.theperplexingpariah.co.uk", client_name="Test.io")
    >>> client_credentials = pump.get_registration() # will return [<client key>, <client secret>, <expirey>]
    >>> client_tokens = pump.get_token() # will return [<token>, <secret>]

.. note:: If you're not using CLI you will need to override the *get_access* method on PyPump to ask for their varification token

An example of then connecting again (using the same variable names as above). This will produce a PyPump object which will use the same credentials as established above::

    >>> pump = PyPump(
    ...          "pump.megworld.co.uk",
    ...          key=client_credentials[0], # the client key
    ...          secret=client_credentials[1], # the client secret
    ...          token=client_tokens[0], # the token key
    ...          token_secret=client_tokens[1], # the token secret
    ...          )
