
Activity
========

This object represents pump.io's activities, these are used in feeds like `inbox`. 

.. note:: The pump variable is an instantiated PyPump class e.g. pump = PyPump("<webfinger>", client_name="<name>", etc...)

.. py:class:: Activity

    This represents an activity::

    >>>me = pump.Person("kabniel@microca.st")
    >>>my_inbox = me.inbox[:10]
    >>>my_activity = my_inbox[0]
    
    .. py:attribute:: id

        This is the id of the activity::

            >>> my_activity.id
            "https://e14n.com/api/activity/Y7Lxll6jSGSqTjFT5dbaqQ"

    .. py:attribute:: url

        This is the url of the activity::
        
            >>> my_activity.url
            'https://e14n.com/evan/activity/Y7Lxll6jSGSqTjFT5dbaqQ'

    .. py:attribute:: content

        This is the content of the activity::

            >>> my_activity.content
            "<a href='https://e14n.com/evan'>Evan Prodromou</a> posted <a href='https://e14n.com/evan/note/S8B6Y9i4SbS2rVw4sfb_5Q'>a note</a>"

    .. py:attribute:: actor

        This is who posted the activity (Person object)::

            >>> my_activity.actor
            <Person: evan@e14n.com>

    .. py:attribute:: updated

        This is when the activity was last updated. this is a datetime.datetime object

            >>> my_activity.updated
	    datetime.datetime(2013, 6, 15, 12, 31, 22, 134180)

    .. py:attribute:: published

        This is when the activity was first published, this is a datetime.datetime object

	    >>> my_activity.published
            datetime.datetime(2013, 6, 15, 12, 31, 22, 134180)

    .. py:attribute:: generator

        This is the client that generated the activity::

            >>> my_activity.generator
            <Generator: E14N Web>

    .. py:attribute:: obj

        This is the object that was affected by the activity::

            >>> my.activity.obj
            <Note>
            


Example
-------

No examples yet!
