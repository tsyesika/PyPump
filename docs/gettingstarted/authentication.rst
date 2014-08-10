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

    >>> from pypump import PyPump, Client
    >>> from pypump.utils import simple_verifier
    >>> client = Client(
    ...     webfinger="Tsyesika@io.theperplexingpariah.co.uk",
    ...     name="Test.io",
    ...     type="native"
    ...     )
    >>> pump = PyPump(client=client, verifier_callback=simple_verifier)
    >>> client_credentials = pump.get_registration() # will return [<client key>, <client secret>, <expirey>]
    >>> client_tokens = pump.get_token() # will return [<token>, <secret>]

.. note:: If you're not using CLI you will need to override the *get_access* method on PyPump to ask for their verification token

An example of then connecting again (using the same variable names as above). This will produce a PyPump object which will use the same credentials as established above::

    >>> client = Client(
    ...     webfinger="Tsyesika@io.theperplexingpariah.co.uk",
    ...     name="Test.io",
    ...     type="native",     
    ...     key=client_credentials[0], # client key
    ...     secret=client_credentials[1] # client secret
    ...     )
    >>> pump = PyPump(
    ...         client=client,          
    ...         token=client_tokens[0], # the token key
    ...         secret=client_tokens[1], # the token secret
    ...         verifier_callback=simple_verifier
    ...         )
