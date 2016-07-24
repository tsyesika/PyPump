Upload Media
============

Uploading images (and in the future other types of media) via PyPump is
relatively easy. Firstly you will need to setup a Client and PyPump
model, information for how to do that can be found in the quick and
dirty guide.

Once you've uploaded an image you will be able to do::

  >>> my_image = pump.Image()
  >>> my_image.from_file("/home/jessica/my_image.jpg")

That is enough to post an image to pump (or MediaGoblin). You can now look at
the URL on the image model::

  >>> my_image.url
  'https://microca.st/Tsyesika/image/yZJCA42GTfCuaeEBqyc26Q'

----------------------
Interacting with Media
----------------------

Commenting
~~~~~~~~~~

You can then interact with this image::

  >> my_image.comment("Hai, this si my comment")

Liking
~~~~~~

If you want to like some media you can use::

  >> my_image.like()

.. note:: MediaGoblin currently doesn't support liking.

Deleting
~~~~~~~~

Deleting media is also easy::

  >> my_image.delete()

.. note:: MediaGoblin current doesn't support deletion of media.
