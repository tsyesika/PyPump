
===============
Quick 'n Dirty!
===============

Introduction
------------

.. warning:: This is not complete, this is used as a fast intro for those fairly familiar or a reference for those who are a little rusty with PyPump

PyPump is a library for `pump.io <http://pump.io>`_, this guide is designed to get you up to speed and using this library in a very short amount of time, to do that I avoid long winded explanations, if you're completely new to PyPump and/or pump.io please use :doc:`tutorial`.

Getting connected
-----------------

So we need to get started::

    >>> from pypump import PyPump

First time lets do all the oauth stuff::

    >>> pump = PyPump(webfinger, client_name="Quick 'n dirty", secure=True)

.. note:: Use *secure=True* if you need SSL

Super, next, I wanna see my inbox::

    >>> me = pump.Person("me@my.server.org")
    >>> my_inbox = me.inbox
    >>> for item in my_inbox[:20]:
    ...     print item.content

.. note:: using an index or slice makes the request. If you iterate over it without a request it **will** be empty,

Oh, my friend evan isn't there, I probably need to follow him::

    >>> evan = pump.Person("evan@e14n.org")
    >>> evan.follow()

Awesome. Lets check again::

    >>> for item in my_inbox[:20]:
    ...     print item

Oh there evan likes PyPump super::

    >>> awesome_note = my_inbox[1] # second note in my inbox
    >>> awesome_note.content
    'Oh wow, PyPump is awesome!'
    >>> awesome_note.like()

I wonder if someone else has liked that::

    >>> awesome_note.likes
    [me@my.server.org, joar@some.other.server]

Cool! Lets tell them about these docs::

    >>> my_comment = pump.Comment("Guys, if you like PyPump check out the docs!")
    >>> awesome_note.comment(my_comment)

I wonder what was posted last::

    >>> latest_item = my_inbox[0]
    >>> print latest_item
    <Image at <Image at https://some.server/uploads/somefriend/2013/7/7/0fXmLQ.png>>

Oh it's an image, lets see the thumb nail::

    >>> url = latest_item.thumb_url
    >>> fout = open("some_image.{0}".format(url.split(".")[-1], "wb")
    >>> import urllib2 # this will be different with python3
    >>> fout.write(urllib2.urlopen(url).read())
    >>> fout.close()

*looks at image*

Hmm, I want to see a bigger version::

    >>> large_url = latest_item.full_url
    >>> print large_url
    <Image at https://some.server/uploads/somefriend/2013/7/7/JkdX2.png">
    >>> # you will find Images often hold other pump.Image objects, we just need to extra the url
    >>> large_url = large_url.url
    >>> fout = open("some_image_larger.{0}".format(large_url.split(".")[-1], "wb")
    >>> fout.write(urllib2.urlopen(url).read())
    >>> fout.close()

*looks at larger image*

That looks awesome, Lets post a comment::

    >>> my_comment = pump.Comment("Great, super imaeg")
    >>> latest_item.comment(my_comment)

Oh no, I made a typo::

    >>> my_comment.delete()
    >>> my_comment.content = "Great, super image")
    >>> latest_item.ocmment(my_comment)

Much better, Lets make a note to tell people how easy this all is::

    >>> my_note = pump.Note("My gawd... PyPump is super easy to get started with")
    >>> my_note.send()

Lovely. Don't forget is there are any issues please issue them on our `GitHub <https://github.com/xray7224/PyPump/issues>`_!
