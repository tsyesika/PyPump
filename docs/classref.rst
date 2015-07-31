Class reference
====================

Essentials
----------

Classes doing most of the work.

.. autoclass:: pypump.PyPump
.. autoclass:: pypump.Client

Pump objects
------------

Classes representing pump.io objects:
        * :class:`Note <pypump.models.note.Note>`
        * :class:`Image <pypump.models.media.Image>`
        * :class:`Audio <pypump.models.media.Audio>`
        * :class:`Video <pypump.models.media.Video>`
        * :class:`Comment <pypump.models.comment.Comment>`
        * :class:`Person <pypump.models.person.Person>`
        * :class:`Inbox <pypump.models.feed.Inbox>`
        * :class:`Outbox <pypump.models.feed.Outbox>`
        * :class:`Lists <pypump.models.feed.Lists>`


.. autoclass:: pypump.models.note.Note
        :exclude-members: serialize
        :inherited-members:

.. autoclass:: pypump.models.media.Image
        :inherited-members:

        .. attribute:: thumbnail
        
                :class:`ImageContainer <pypump.models.media.ImageContainer>`
                holding information about the thumbnail image.

        .. attribute:: original

                :class:`ImageContainer <pypump.models.media.ImageContainer>`
                holding information about the original image.

.. autoclass:: pypump.models.media.Audio
        :inherited-members:

        .. attribute:: stream

                :class:`StreamContainer <pypump.models.media.StreamContainer>`
                holding information about the stream.

.. autoclass:: pypump.models.media.Video
        :inherited-members:

        .. attribute:: stream

                :class:`StreamContainer <pypump.models.media.StreamContainer>`
                holding information about the stream.


.. autoclass:: pypump.models.comment.Comment
        :inherited-members:

.. autoclass:: pypump.models.person.Person
        :inherited-members:

.. autoclass:: pypump.models.feed.Inbox
        :inherited-members:
.. autoclass:: pypump.models.feed.Outbox
        :inherited-members:
.. autoclass:: pypump.models.feed.Lists
        :inherited-members:

Low level objects
-----------------

Classes you probably don't need to know about.

.. autoclass:: pypump.models.media.ImageContainer
.. autoclass:: pypump.models.media.StreamContainer
.. .. autoclass:: pypump.models.PumpObject
.. .. autoclass:: pypump.models.Mapper

.. autoclass:: pypump.models.feed.Feed
        :inherited-members:
.. autoclass:: pypump.models.collection.Collection
        :inherited-members:
.. .. autoclass:: pypump.models.feed.ItemList
