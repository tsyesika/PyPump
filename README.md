# PyPump
This library has been written for python 3000 (python 3.x). This will allow you to interface with the pump.io platform (to see a functioning node please see http://pump.io/tryit). The library in it's state today is still very untested and incomplete and since pump.io is also still in an alpha phase no doubt that will change too (inturn we would change).

Updates will be coming soon.

## Requirements
My pyoauth3000 repo (drop it into the PyPump folder for now)
Python3000 (testing on python 3.3)

## Example
An example of posting a notice would be:

```
from PyPump.PyPump import PyPump

## now make the object
pump = PyPump('microca.st', key, secret)
pump.set_nickname("Tsyesika")
pump.post_note("This note will appear on my Tsyesika account on microca.st")
```

This is importing the PyPump class from the PyPump module. You then make the object, you're passing in the URL of the pump.io instance (microca.st for myself), the key and secret will soon be methods on PyPump however currently these are from the client registration API. There is a script in Scripts/client_reg which you edit the stuff inside [] and it'll give you those (key is called client_id) in json.

After that you set the nickname you would like to use and then you can use post_note()

There is also the inbox method

```
pump.inbox()
```

This will return a python dictionary which have a load of info on (more documentation to come I think though you can look at evens documentation page for it: https://github.com/e14n/pump.io/blob/master/API.md)


