================
Getting Verifier
================

The default behavour of PyPump is to ask the user (in english) to click on a link
and paste in the verifier. It's done via a print statement and raw_input which usually
occur over standard in and standard out. Often this isn't very useful so PyPump provides
a very easy way using two callbacks to work with your program to ask them for the verifier.

We have a link the user must click, it'll take them to an Authorization page asking
them to permit your program access, if they allow your program they will be taken to a
page that will have the verifier on, this needs to be entered into your program.

The default experiance via PyPump
----------------------------------
This is how PyPump by default asks::

    To allow us to use your pump.io please follow the instructions at:
    https://some.server/oauth/authorize?oauth_token=b_Tf-y1yXrPbfkOXj-PhFQ

Callbacks
---------

The callbacks work by you define a callback for when PyPump would like to be
called with the `url` when PyPump would like you to ask the user for the verifier
the prototype of the function is::

    def ask_verifier(self, url):
        """ This should display the url and ask the user to authorize your app """
        pass
        # pypump ignores the return value

Once you have the verifier you need to call `verifier`::

    >>> verifier
    c_Fe-91tXrPbfkOXj-xKFu
    >>> pypump_instance.verifier(verifier)


Example
-------

I wrote this, it's not a real GUI framework, I didn't want to weight this down
with a lot of other cruft, this is just to show a rough example of how this might
work::

    from pypump import PyPump
    from gui_framework import Window, Widgets    

    class MyGui(object):

        pump = None

        def __init__(self):
            self.window = Window()
            self.window.add(
                Widgets.Message("Checking authorization...")
                )

        def return_verifier(self):
            """ Hands the verifier back to PyPump """
            if self.pump is None:
                raise Exception("You need to set PyPump")

            verifier = self.verifier.get()
            self.pump.verifier(verifier)
            # Done!

        def ask_verifier(self, url):
            """ Will display a message with URL and a text box for the verifier """
            self.window.clear()
            self.verifier = Widgets.Textbox()
            self.button = Widgets.Button()
            self.window.add(
                Widgets.Message("Please authorize me!"),
                Widgets.Message(url),
                self.verifier,
                button,
                )
            self.button.when_clicked(self.return_verifier)


    gui = MyGui()

    pump = PyPump(
        "someome@server.org",
        client_name="MyClient",
        verifier_callback=gui.ask_verifier
        )
    gui.pump = pump
