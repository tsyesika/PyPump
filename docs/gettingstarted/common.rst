
Posting a note
==============

.. alsosee: You should look at `gettingstarted/authentication` to learn how to instantiatePyPump object correctly.

This is how to post a note on Pump.io::

    >>> from PyPump.objects.note import Note
    >>> pump = PyPump("Tsyesika@pump.megworld.co.uk", key=..., secret=..., token=..., token_secret=...)
    >>> note = Note("Hey! This was posted by PyPump ^_^")


Commenting on a note
--------------------

You need to create a Comment object and then use the comment method on the note

    >>> my_note
    <Note: "This is a note!">
    >>> my_comment = Comment("This is a comment")
    >>> my_note.comment(my_comment)
    >>> # done!


