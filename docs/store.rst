======
Store
======

Using store objects is the way PyPump handles the storing of certain
data it gets that needs to be saved to disk. There is several pieces
of data that might be stored such as:

- Client ID and secret
- OAuth request token and secret
- OAuth access token and secret

There might be others in the future too. The store object has an
interface like a dictionary. PyPump provides a disk JSON store which
allows you to easily just save the data to disk. You should note that
this data should be considered sensative as with it someone has access
to the users pump.io account.

Implementation
--------------

You probably want to provide your own storage object. There are two
extra methods other than dictionary methods you need to implement
are::

  @classmethod
  def load(cls, webfiger, pump):
      """
      This should return an instance of the store object full of any
      data that has been saved. It's your responsibility to set the
      `prefix` attribute on the store object.

      webfinger: String containing webfinger of user.
      pump: PyPump object loading the store object.
      """
      store = cls()
      store.prefix = webfinger
      return store

  def save(self):
      """
      This should save all the data to the storage.
      """
      pass

There is a `prefix` attribute will contain the webfinger of the user
the data belongs to. All the data stored and loaded should relate to
this webfinger.

The save is called frequently and multiple times. The AbstractStore
class will call the save method everytime something is set/changed on
the object.

PyPump
------

There are several ways to provide PyPump with a store object. You can
pass it in when you create the PyPump object e.g::

  >>> my_store = MyStore.load()
  >>> pump = PyPump(store=my_store, ...)

If no storage object is passed, PyPump will call the .create_store
method on itself. This will by default call .load(webfinger, pypump)
on whatever class is in store_class on PyPump. You can provide your
own class there::

  >>> class MyPump(PyPump):
  ...     store_class = MyStore
  ...
  >>> pump = MyPump(...)

This will use the MyStore class. If you want to do something else you
can always override the .create_store method::

  class MyPump(PyPump):
      def create_store(self):
          """ This should create and return the store object """
          return MyStore.load(
              webfinger=self.client.webfinger,
              pump=self
          )

For convenience, PyPump comes with a simple JSON store class,
`pypump.store.Store`.
