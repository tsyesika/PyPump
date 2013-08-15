========
Tutorial
========

.. note:: This tutorial is prep for an API that does not yet actually exist... we're doing the documentation driven development route.  But this is what it should look like! ;)

PyPump and the Pump API
-----------------------

PyPump is aiming to implement and interface with the `Pump API
<https://github.com/e14n/pump.io/blob/master/API.md>`_, which is a
federation protocol for the web.  You can read the actual Pump API
docs to get a sense of all that, but here's a high level overview.

The Pump API is all about ActivityStreams and sending json-encoded
descriptions of activities back and forth across different users on
different sites.  At the highest conceptual level, it's not too
different from the idea of email servers sending emails back and
forth, but the messages (activities here) are much more specific and
carry more specific meaning about what "type" of message is being sent
back and forth.  An activity can be a user "favoriting" something or
"posting an image" or what have you.

In the world of email, each user has an email address; in the world of
Pump, each user has a `webfinger <http://code.google.com/p/webfinger/>`_
address.  It looks pretty similar, but it's meant for the web.  For
the sake of this tutorial, you don't need to know how webfinger works;
the PyPump API will handle that for you.

Each user has two main feeds that are used for communication.  In the
Pump API docs' own wording:

- An **activity outbox** (probably at /api/user/<nickname>/feed). This
  is where the user posts new activities, and where others can read
  the user's activities.
- An **activity inbox** (probably at /api/user/<nickname>/inbox). This is
  where the user can read posts that were sent to him/her. Remote
  servers can post activities here to be delivered to the user.

(We use the inbox/outbox convention fairly strongly in PyPump.)

You should read the Pump spec, but sometimes coding examples are the
best way to learn.  So, that said, let's get into an example of using
PyPump!


A quick example
---------------

Let's assume you already have a user with the webfinger id of
mizbunny@example.org.  We want to check what our latest messages
are!  But before we can do that, we need to authenticate.  If this is
your first time, you need to authenticate this client::

      >>> from pypump import PyPump
      >>> pump = PyPump("mizbunny@example.org", client_name="Test.io")
      >>> client_credentials = pump.get_registration()
      # will return [<token>, <secret>]
      >>> client_tokens = pump.get_token()

The PyPump call will try to verify with OAuth, You may wish to override how it asks for authentication.
PyPump by default writes to standard out a URL for the user to click and reads in from standard in for a verification
code presented by the webserver.

You should store the client credentials somewhere.  You can now
reconnect like so::

    >>> pump = PyPump(
    ...          "mizbunny@example.org",
    ...          key=client_credentials[0], # the client key
    ...          secret=client_credentials[1], # the client secret
    ...          token=client_tokens[0], # the token key
    ...          token_secret=client_tokens[1], # the token secret
    ...          )

Okay, we're connected!  Next up, we want to check out what our last 30
items in our inbox are, but first we need to find ourselves::

    >>> me = pump.Person("mizbunny@example.org")
    >>> me.summary
    >>> 'Hello and welcome to my summary'

That looks like us, now to find our inbox items.
The inbox comes in three versions

- me.inbox.major is where major activities such as posted notes and images end up.
- me.inbox.minor is where minor activities such as likes and comments end up.
- me.inbox is a combination of both of the above.

We only want to see notes, so we use the major inbox.
The inbox supports python-style index slicing::

    >>> recent_activities = me.inbox.major[:30]  # get last 30 activities

We could print out each of the most recent activities like so::

    >>> for activity in recent_activities:
    >>>     print activity
    <Activity: Evan Prodromou posted a note>
    <Activity: jrobb posted a note>
    <Activity: jpope posted a note>
    <Activity: sazius posted a note>
    ...

Maybe we're just looking at our most recent message, and see it's from
our friend Evan.  It seems that he wants to invite us over for a
dinner party::

    >>> activity = recent_activities[0]
    >>> activity
    <Activity: Evan Prodromou posted a note>
    >>> message = activity.obj
    >>> message.author
    <User evan@e14n.com>
    >>> message.content
    "Yo, want to come over to dinner?  We're making asparagus!"

We can comment on the message saying we'd love to::

    >>> our_reply = pump.Comment("I'd love to!")
    >>> message.comment(our_reply) # this is evans message we got above!

(Since this Note activity is being instantiated, it needs a
reference to our PyPump class instance.  Objects that you get back and
forth from the API themselves will try to keep track of their own
parent PyPump object for you.)

We could even like/favourite the previous message::

    >>> message.like()

We can also check to see what our buddy's public feed is.  Maybe
he's said some interesting things?::

    >>> evan = message.author
    >>> for activity in evan.outbox:
    >>>     message = activity.obj
    >>>     print message.content

Prehaps we want to know a bit about Evan::

    >>> print evan.summary  

.. Maybe we took a picture, and we want to post that picture to our
.. public feed so everyone can see it.  We can do this by posting it to
.. our outbox:
.. 
..   >>> from pypump.activities import Photo
..   >>> new_photo = Photo(
..   ...     pump,
..   ...     subject=

Want to see what the model actually looks like?
All activities in pump.io have a .seralize method::

    >>> print message.to_json(indent=2)
    {
    "id": "http://coding.example/api/activity/bwkflwken",
    "actor": {
      "id": "acct:bwk@coding.example",
      "objectType": "person",
      "displayName": "Brian Kernighan"
    },
    "verb": "follow",
    "to": [{
      "id": "acct:ken@coding.example",
      "objectType": "person"
    }],
    "object": {
      "id": "acct:ken@coding.example",
      "objectType": "person",
      "displayName": "Ken Thompson"
    },
    "published": "1974-01-01T00:00:00",
    "links": [
        {"rel": "self", "href": "http://coding.example/api/activity/bwkflwken"}
    ]
    }

(The indent attribute here is passed to  to give prettier output.)

.. (Yes, that was stolen from the Pump API docs :))


(similarly, all activity classes provide a unserialize class method).

.. Things missing:
   - How to post to your public feed, as opposed to a list of specific
     people?
   - Show different types of activities
   - Explain how to implement an activity subclass?
