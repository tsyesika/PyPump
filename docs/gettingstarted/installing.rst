=============
Installation
=============

Using pip
---------

The best way to install PyPump is via pip, if you haven't, setup::

    $ virtualenv path/to/virtualenv
    $ source path/to/virtualenv/bin/activate
    $ pip install pypump

If you get an error which looks like::

      Could not find a version that satisfies the requirement pypump (from versions: 0.1.6a, 0.1.7a, 0.1.8a, 0.1.9a, 0.2, 0.1a)
      Cleaning up...
      No distributions matching the version for pypump

You need to specify the latest version, for example::

    $ pip install pypump==0.4.1


Using git
---------

.. Warning:: The code on git may break, the code on pip is likely to be much more stable

You can if you want the latest and greatest use the copy on git, to do this execute::

    $ git clone https://github.com/xray7224/PyPump.git
    $ cd PyPump
    $ virtualenv .vt_env && . .vt_env/bin/activate
    $ pip install requests oauthlib requests-oauthlib

To keep this up to date use the following command inside the PyPump folder::

    $ git pull
