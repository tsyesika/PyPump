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

