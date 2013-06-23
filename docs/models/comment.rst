
Comment
=======

This object represents pump.io's comments, these are posted on Notes and Images. 

.. note:: The pump variable is an instantiated PyPump class e.g. pump = PyPump("<webfinger>", client_name="<name>", etc...)

.. py:class:: Comment

    This represents a Comment object, These are used in reply to other others such as Images or Notes.
    

    .. py:attribute:: content

        This is the content of the Comment (string)::

	    >>> my_comment = pump.Comment("This is a comment")
            >>> my_comment.content
            "This is a comment" 

    .. py:attribute:: actor

        This is who posted the Comment (Person object)::

            >>> my_comment = pump.Comment("This is a comment")
            >>> my_comment.actor
            <Person: Tsyesika@pump.megworld.co.uk>

    .. py:attribute:: updated

        This is when it was last updated (e.g. liked) this is a datetime.datetime object

            >>> my_comment.updated
	    datetime.datetime(2013, 6, 15, 12, 31, 22, 134180)

    .. py:attribute:: published

        This is when the Comment was first published, this is a datetime.datetime object

	    >>> my_comment.published
            datetime.datetime(2013, 6, 15, 12, 31, 22, 134180)

    .. py:method:: like()

        This likes/favourites a comment

    .. py:method:: unlike()

        This unlikes/unfavourites a comment

    .. py:method:: delete()

        This will delete the object.


.. note:: favourite and unfavourite methods are mapped to their respective like and unlike methods.


Example
-------

This shows making a comment on a note::

    >>> my_note
    <Note: "This is a note">
    >>> my_comment = pump.Comment("Oh hey, i'm commenting with PyPump!") # pump is instance of PyPump
    >>> my_note.comment(my_comment)

You want to like the comment because you think PyPump is cool?::

    >>> my_comment.like()
    
What's that, you don't think PyPump is cool? :(::

    >>> my_comment.unlike()

And you want to delete your comment?::

    >>> my_comment.delete()
    >>> my_comment = None

.. warning: Using a deleted comment will cause DoesNotExist to be raised

