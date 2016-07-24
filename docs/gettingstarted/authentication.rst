Authorization
=============

What you need to know
---------------------

Pump.io uses OAuth 1.0 with dynamic client registration, this is available through a lot of libraries, PyPump uses `oauthlib <https://github.com/idan/oauthlib>`_ and a wrapper around it to provide an provide an interface with the `requests <http://docs.python-requests.org/en/latest/>`_ library - `requests-oauthlib <https://github.com/requests/requests-oauthlib>`. All of that is handled by PyPump however there are some things to know.

OAuth works by exchanging pre-established client credentials and tokens, you however have to provide those each time you instantiate the PyPump object. You will have to provide a mechanism to store these so that you can you can provide them the next time.

.. note::
        As of version 0.6 PyPump is storing credentials using an internal :doc:`../store` object.

Example
-------
The following will create (for the first time) a connection to a pump.io server for the user Tsyesika@io.theperplexingpariah.co.uk for my client named "Test.io"::

    >>> from pypump import PyPump, Client
    >>> client = Client(
    ...     webfinger="Tsyesika@io.theperplexingpariah.co.uk",
    ...     name="Test.io",
    ...     type="native"
    ...)
    >>> def simple_verifier(url):
    ...     print('Go to: ' + url)
    ...     return raw_input('Verifier: ') # they will get a code back
    >>> pump = PyPump(client=client, verifier_callback=simple_verifier)

An example of then connecting again (using the same variable names as above). This will produce a PyPump object which will use the same credentials as established above::

    >>> client = Client(
    ...     webfinger="Tsyesika@io.theperplexingpariah.co.uk",
    ...     name="Test.io",
    ...     type="native",
    ...     )
    >>> pump = PyPump(
    ...         client=client,
    ...         verifier_callback=simple_verifier
    ...         )
