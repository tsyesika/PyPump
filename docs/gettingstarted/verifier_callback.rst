Getting Verifier
================

For OAuth to allow OOB (Out of band) applications to have access to an account,
first we must provide a link and instructions for the user. Then we must provide
a means of copying the verifier into an application and relaying it to the server
with other tokens. The server will then provide us with the credentials that we can use.

You must write a method which takes a URL that the user needs to visit, provide some 
way for that user to input a string value (the verification), and then give that value to PyPump. This could
be simply a case of printing the link and using raw_input/input to get the verifier or it could
be a more complex function which redraws a GUI and opens a browser. 


Simple verifier
----------------

The following is an example of a simple verifier which could be used for a CLI (command line interface)
application. This method is actually the same function which is used to prompt the user to provide a
verifier in the PyPump Shell::

    def verifier(url):
        """ Asks for verification code for OAuth OOB """
        print("Please open and follow the instructions:")
        print(url)
        return raw_input("Verifier: ")

Callback
--------

Having a function which is called and then returns the verification might be more
difficult in GUI programs or other interfaces. We provide a callback mechanism that you
can use. If the verifier function returns None then PyPump assumes you will be
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
            client = Client(
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
