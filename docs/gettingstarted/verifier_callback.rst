================
Getting Verifier
================

As part of OAuth to allow OOB (Out of band) applications to have access to the account
we have a link that they will click, follow the instructions and then copy the verifier
into the application which we then relay to the server with other tokens. The server
will them provide us with the credentials that we can use.

You will need to write a method which takes a URL that the user needs to visit and provide
some way of the users inputting string value which you will then give to PyPump. This could
just be a case of printing the link and using raw_input/input to get the verifier or it could
be a more complex funtion which redraws a GUI and opens a browser. 


Simple verifier
----------------

The following is an example of a simple verifier which could be used for a CLI (command line interface)
application. This method is actually the same function which is used to prompt the user to provide a
verifier in the PyPump Shell::

    def verifier(url):
        """ Asks for verification code for OAuth OOB """
        print "Please open and follow the instructions:"
        print url
        return raw_input("Verifier: ")

Callback
--------

Having a function which is called and then returns back the verification might be more
difficult in GUI programs or other interfaces. We provide a callback mechamism that you
can use. If the verifier function returns None then PyPump assumes you will be be then
calling PyPump.verifier which takes the verifier as the argument.

Complex GUI example
-------------------

As an attempt to avoid writing an example which is tied to one GUI library, I have made
one up in order to demonstrate exactly what might be involved::

    import webbrowser # it's a python module - really, check it out.

    from pypump import Client, PyPump

    class MyWindow(guilib.Window):

        def __init__(self, *args, **kwargs):
            
            # Write out to the screen telling them what we're doing
            self.draw("Please wait, loading...")

            # setup pypump object
            clinet = Client(
                webfinger='someone@server.com',
                type='native',
                name='An awesome GUI client'
            )

            self.pump = PyPump(
                client=client,
                verifier_callback=self.ask_for_verifier
            )


        def ask_for_verifier(self, url):
            """ Takes a URL, opens it and asks for a verifier """
            # Open the URL in a browser
            webbrowser.open(url)

            # Clear other stuff from window
            self.clear_window()

            # draw a text input box and a button to submit
            self.draw(guilib.InputBox('Verifier:', name='verifier'))
            self.draw(guilib.Button('Verify!', onclick=self.verifier))

        def verifier(self, verifier):
            """ When the button is clicked it sends the verifier here which we give to PyPump """
            self.pump.verifier(verifier)


If you return anything from your verifier callback, pypump will expect that to be
the verifier code so unless you're actually using a simple method, ensure you return
None.