
Person
=======

This object represents a user on pump.io. 

.. note:: The pump variable is an instantiated PyPump class e.g. pump = PyPump("<webfinger>", client_name="<name>", etc...)

.. py:class:: Person

    This represents a Person object, These are used in getting their inboxes, information on, etc...
    

    .. py:attribute:: preferred_username

        This is the username (you should display the display_name) (unicode)::

	        >>> a_person.preferred_username
            u'Tsyesika' 

    .. py:attribute:: display_name

        This is the username you should display (unicode)::

            >>> a_person.display_name
            u'Tsyesìka'

    .. py:attribute:: updated

        This is when their profile was updated (datetime.datetime)::

            >>> a_person.updated
	        datetime.datetime(2013, 6, 15, 12, 31, 22, 134180)

    .. py:attribute:: published

        This is when their profile was first published (datetime.datetime)::

	        >>> a_person.published
            datetime.datetime(2013, 6, 15, 12, 31, 22, 134180)

    .. py:attribute:: url

        The URL to the profile (string)::

	        >>> a_person.url
            'https://pump.megworld.co.uk/Tsyesika'

    .. py:attribute:: inbox

        This is an iterable feed of inbox items (only available for the logged in person (Feed object)::

            >>> list(PyPump.me.inbox)
            [<Activity>, <Activity>]

    .. py:attribute:: outbox

        This is an iterable feed of outbox items (Feed object)::

            >>> list(a_person.outbox)
            [<Activity>, <Activity>]

    .. py:attribute:: followers

        This is an iterable feed of followers (Feed object)::

            >>> list(a_person.followers)
            [<Person: person1@yep.org>, <Person: person2@pumpit.com>, <Person: someoneelse@example.com>]

    .. py:attribute:: following

        This is an iterable feed of all the people they're following::

            >>> list(a_person.following)
            [<Person: TheBestPersonEvah@pump.megworld.co.uk>]

    .. py:attribute:: location

        This is the location of the user (Location object)::

             >>> a_person.location
             <Location: Manchester, UK>

    .. py:attribute:: summary

        This is the summer of the user (unicode)::

             >>> a_person.summary
             u'The maker of this fabulous library!'

    .. py:attribute:: image

        This is the image of the person (Image object)::

            >>> a_person.image
            <Image: https://pump.megworld.co.uk/uploads/Tsyesika/2013/6/15/blahblah.png>

    .. py:method:: follow

        This will follow the user if you're not already following them

    .. py:method:: unfollow

        This will stop following the user if you were following them

        

Example
-------

This shows how to follow someone::

    >>> a_person.follow() # yay we're now following them!

What happens when i try and follow someone I am?::

    >>> a_person.follow() # nothing? yep.
    
Well, I don't want to follow them::

    >>> a_person.unfollow() # awhh :(

You want to find yourfriend@pumpity.net::

    >>> my_friend = pump.Person("yourfriend@pumpity.net")
    Traceback (most recent call last):
        blah blah
        you know the drill
    DoesNotExist: Can't find yourfriend@pumpity.net

Oh that's right they're on pump.megworld.co.uk::

    >>> my_friend = pump.Person("myfriend@pump.megworld.co.uk")
    >>> # Awesome!
