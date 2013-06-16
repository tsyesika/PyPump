========
Tutorial
========

**NOTE:** This tutorial is prep for an API that does not yet actually
 exist... we're doing the documentation driven development route.  But
 this is what it should look like! ;)

PyPump and the Pump API
-----------------------

PyPump is tooling to implement and interface with the `Pump API
<https://github.com/e14n/pump.io/blob/master/API.md>`_, which is a
federation protocol for the web.  You can read the actual Pump API
docs to get a sense of all that, but here's a high level overview.

The Pump API is all about ActivityStreams and sending json-encoded
descriptions of activities back and forth across different users on
different sites.  At the highest conceptual level, it's not too
different from the idea of email servers sending emails back and
forth, but the messages (activities here) are much more specific and
cary more specific meaning about what "type" of message is being sent
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
  >>> pump = PyPump("mizbunny@example.org", client_name="Test.io", secure=True)
  # will return [<client key>, <client secret>, <expirey>]
  >>> client_credentials = pump.get_registration()
  # will return [<token>, <secret>]
  >>> client_tokens = pump.get_token()

(TODO: does this open a browser?  What's going on here?  How is
the user authenticated?)

You should store the client credentials somewhere.  You can now
reconnect like so::

  >>> pump = PyPump(
  ...          "mizbunny@example.org",
  ...          key=client_credentials[0], # the client key
  ...          secret=client_credentials[1], # the client secret
  ...          token=client_tokens[0], # the token key
  ...          token_secret=client_tokens[1], # the token secret
  ...          secure=True) # for using HTTPS

Okay, we're connected!  Next up, we want to check out what our last 30
messages are.  PyPump supports python-style index slicing::

  >>> recent_messages = pump.inbox[:30]  # get last 30 messages

We could print out each of the most recent messages like so::

  >>> for message in recent_messages:
  >>>     print message.body

Maybe we're just looking at our most recent message, and see it's from
our friend Evan.  It seems that he wants to invite us over for a
dinner party::

  >>> message = recent_messages[0]
  >>> message
  <Notice by evan at 04/05/2013>
  >>> message.author
  <User evan@e14n.com>
  >>> message.body
  "Yo, want to come over to dinner?  We're making asparagus!"

We can compose a reply::

  >>> from pypump.activities import Notice
  >>> reply = Notice(
  ...     pump,
  ...     body="I'd love to!",
  ...     reply_to=message.id,
  ...     to=[message.author])
  >>> reply.send()
  
(Since this Notice activity is being instantiated, it needs a
reference to our PyPump class instance.  Objects that you get back and
forth from the API themselves will try to keep track of their own
parent PyPump object for you.)

We could even favorite the previous message::

  >>> from pypump.activities import Favorite
  >>> fave = Favorite(
  ...     pump,
  ...     subject=message.id)

.. (Is this right?)

We can also check to see what our buddy's public feed is.  Maybe
he's said some interesting things?::

  >>> evan = message.author
  >>> for messages in evan.inbox:
  >>>     print message.body

.. TODO: Put a photo, or subscription, or some other activity example
   here...

.. Maybe we took a picture, and we want to post that picture to our
.. public feed so everyone can see it.  We can do this by posting it to
.. our outbox:
.. 
..   >>> from pypump.activities import Photo
..   >>> new_photo = Photo(
..   ...     pump,
..   ...     subject=

Want to see what the activity actually looks like?
All activities in pump.io have a .to_json() method::

  >>> import json
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

(The indent attribute here is passed to json.to_json to give prettier output.)

.. (Yes, that was stolen from the Pump API docs :))


(similarly, all activity classes provide a from_json() class method).

.. Things missing:
   - How to post to your public feed, as opposed to a list of specific
     people?
   - Show different types of activities
   - Explain how to implement an activity subclass?
