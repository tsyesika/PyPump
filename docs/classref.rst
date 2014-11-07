Class reference
====================

Essentials
----------

Classes doing most of the work.

.. module:: pypump
.. autoclass:: PyPump
.. autoclass:: Client

Pump objects
------------

Classes representing pump.io objects.

.. module:: pypump.models.note
.. autoclass:: Note
        :exclude-members: serialize
        :inherited-members:

.. module:: pypump.models.image
.. autoclass:: Image
        :inherited-members:

        .. attribute:: thumbnail
        
                :class:`ImageContainer <pypump.models.image.ImageContainer>`
                holding information about the thumbnail image.

        .. attribute:: original

                :class:`ImageContainer <pypump.models.image.ImageContainer>`
                holding information about the original image.

.. module:: pypump.models.person
.. autoclass:: Person
        :inherited-members:

.. .. module:: pypump.models.feed
.. .. autoclass:: Feed
.. .. autoclass:: Inbox
.. .. autoclass:: Outbox
.. .. autoclass:: Lists

Plumbing objects
----------------

Classes you probably don't need to know about.

.. autoclass:: pypump.models.image.ImageContainer
.. .. autoclass:: pypump.models.PumpObject
.. .. autoclass:: pypump.models.Mapper
