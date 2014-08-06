Web Development using PyPump
============================

One of the problem with PyPump and Web development is that you often have
a view which is called and then must return a function. While it is possible
it may be difficult to use the regular PyPump callback routines. WebPump is a
subclassed version of PyPump which handles that for you.

The only real difference is you don't specify a `verifier_callback` (if you do
it will be ignored). Once the instanciation has completed you can guarantee
that the URL for the callback has been created.

Django
------

This is an example of a very basic django view which uses WebPump::

    from pypump import WebPump
    from app.models import PumpModel
    from django.shortcuts import redirect
    from django.exceptions import ObjectDoesNotExist

    def pump_view(request, webfinger):
        try:
            webfinger = PumpModel.objects.get(webfinger=webfinger)
        except ObjectDoesNotExist:
            webfinger = PumpModel.objects.create(webfinger=webfinger)
            webfinger.save()

        # make the WebPump object
        if webfinger.oauth_credentials:
            pump = WebPump(
                    webfinger.webfinger,
                    client_type="web",
                    client_name="DjangoApp",
                    key=webfinger.key,
                    secret=webfinger.secret
                    token=webfinger.token,
                    token_secret=token_secret,
                    callback_uri="http://my_app.com/oauth/authorize"
                    )
        else:
            pump = WebPump(
                    webfinger.webfinger,
                    client_type="web",
                    client_name="DjangoApp",
                    callback_uri="http://my_app.com/oauth/authorize"
                    )

        # save the client credentials as they won't change
        webfinger.key, webfinger.secret, webfinger.expirey = pump.get_registeration()
        
        # save the request tokens so we can identify the authorize callback
        webfinger.token, webfinger.secret = pump.get_registrat()

        # save the model back to db
        webfinger.save()

        if pump.url is not None:
            # The user must go to this url and will get bounced back to our
            # callback_uri we specified above and add the webfinger as a
            # session cookie.
            request.session["webfinger"] = webfinger
            return redirect(pump.url)

        # okay oauth completed successfully, we can just save the oauth
        # credentials and redirect.
        webfinger.token, webfinger.token_secret = pump.get_registration()
        webfinger.save()

        # redirect to profile!
        return redirect("/profile/{webfinger}".format(webfinger))

    def authorize_view(request):
        """ This is the redirect when authorization is complete """
        webfinger = request.session.get("webfinger", None)
        token, verifier = request.GET["token"], request.GET["verifier"]
        
        try:
            webfinger = PumpModel.objects.get(
                    webfiger=webfinger,
                    token=token
                    )

        except ObjectDoesNotExist:
            return redirect("/error") # tell them this is a invalid request

        pump = WebPump(
                webfinger.webfinger,
                client_name="DjangoApp",
                client_type="web",
                key=pump.key,
                secret=pump.secret,
                )

        pump.verifier(verifier)

        # Save the access tokens back now.
        webfinger.token, webfinger.token_secret = pump.get_registration()
        webfinger.save()

        # and redirect to their profile
        return redirect("/profile")
