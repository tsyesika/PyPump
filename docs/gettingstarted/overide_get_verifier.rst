===========================
Overriding getting verifier
===========================

By default pypump just asks via stdout and stdin for the verification, this 
probably isn't that useful if you're writing a GUI or web application and using
PyPump... Overriding this is fairly simple!

The current code
----------------

It may be a good idea to look at what the PyPyump code looks like::

    def get_access(self, token):
        """ this asks the user to let us use their account """

        print("To allow us to use your pump.io please follow the instructions at:")
        print("{protocol}://{server}/oauth/authorize?oauth_token={token}".format(
                protocol=self.protocol,
                server=self.server,
                token=token.decode("utf-8")
                ))
        
        code = raw_input("Verifier Code: ").lstrip(" ").rstrip(" ")
        return code

As you can tell we store the protocol and server information you need to construct
URL on the pypump object. The token should be representable by ASCII however just
for precautions we decode it into unicode by asuming that it's in UTF-8

Example
-------

Lets try and override this for a GTK application then::

    from pypump import PyPump
    class MyPump(PyPump):
        
        def get_access(self, token):
            token = token.decode("utf-8") # I like working with utf-8
            url = "{protocol}://{server}/oauth/authorize?oauth_token={token}"
            url = url.format(protocol=self.protocol, server=self.server, token=token)
            
            # now we ask the user
            verifier = some_function_to_ask_user(url) 
            
            return verifier


