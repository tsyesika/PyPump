
Posting a note
==============

.. alsosee: You should look at `gettingstarted/authentication` to learn how to instantiatePyPump object correctly.

This is how to post a note on Pump.io::

    >>> from PyPump.objects.note import Note
    >>> pump = PyPump("Tsyesika@pump.megworld.co.uk", key=..., secret=..., token=..., token_secret=...)
    >>> note = Note("Hey! This was posted by PyPump ^_^")


Commenting on a note
====================

