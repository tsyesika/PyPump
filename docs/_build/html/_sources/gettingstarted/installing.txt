

Using pip
==========

The best way to install PyPump is via pip, if you have't, setup::

    virtualenv path/to/virtualenv
    source path/to/virtualenv/bin/activate
    pip install pypump


Using git
=========

.. Warning:: The code on git may break, the code on pip is likely to be much more stable

You can if you want the latest and greatest use the copy on git, to do this execute::

    git clone https://github.com/xray7224/PyPump.git
    cd PyPump
    git submodule init && git submodule update

To keep this up to date use the following command inside the PyPump folder::

    git pull
