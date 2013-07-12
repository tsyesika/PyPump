import json
import sys
import os
from pypump import PyPump

try:
    from IPython.frontend.terminal.embed import InteractiveShellEmbed
    from IPython.config.loader import Config
except ImportError:
    print("You need to have ipython installed to run this")
    sys.exit(1)

store_path = os.path.expanduser("~/.pypump_test")


welcome_banner = """
Welcome to the PyPump testing shell,
We have setup the PyPump object for you:

pump = {pypump}

If you need help please visit our docs:
https://pypump.readthedocs.org/en/latest

Enjoy!
"""

def open_database(path):
    if os.path.exists(path):
        try:
            fin = open(path, "r")
            db = json.loads(fin.read())
            return db
        except Exception:
            print("There has been a problem parsing the database {0}".format(path))
            sys.exit(1)

    else:
        return {}

def save_database(db, path):
    """ Saves db as JSON to path """
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            print("There was an error removing database from {0}".format(path))
    try:
        fout = open(path, "w")
        db = json.dumps(db, sort_keys=True, indent=4, separators=(",", ": "))
        fout.write(db)
        fout.close()
    except Exception:
        raise
        print("There was an error saving the database to {0}".format(path))

    return db


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print("Usage:")
        print("     {0} <webfinger> <client_name>".format(sys.argv[0]))
        sys.exit(0)

    if "-v" in sys.argv or "--version" in sys.argv:
        if os.path.exists("VERSION"):
            print(open("VERSION", "r").read())
        else:
            print("Unknown.")
        sys.exit(0)

    if "--clean" in sys.argv:
        if not os.path.exists(store_path):
            print("Nothing to do.")
            sys.exit(0)

        try:
            os.remove(store_path)
            print("Removed all files used by PyPump tester")
        except Exception:
            print("Something went wrong, probably permissions")
            print("The file I should have been writing to is {0}".format(store_path))
        sys.exit(0)

    # go find the client info if it exists
    db = open_database(store_path)

    if "webfinger" not in db:
        # check they've given some cli commands then
        if len(sys.argv) <= 1:
            print("No webfinger ID on file, please specify one")
            sys.exit(1)

        # okay
        webfinger = sys.argv[1]
        if "@" not in webfinger:
            print("{0} doesn't look like a webfinger!".format(webfinger))
            sys.exit(1)

    else:
        if len(sys.argv) <= 1:
            webfinger = db["webfinger"]
        else:
            webfinger = sys.argv[1]
            db["webfinger"] = webfinger
        
    if len(sys.argv) <= 2:
        client_name = db.get("client_name", "PyPump")
    else:
        client_name = sys.argv[2]
        db["client_name"] = client_name

    pump = PyPump(
            webfinger,
            client_name=client_name,
            key=db.get("key", None),
            secret=db.get("secret", None),
            client_type=db.get("client_type", "native"),
            token=db.get("token", None),
            token_secret=db.get("token_secret", None),
            secure=db.get("secure", False)
            )

    # save client name and webfinger
    db["webfinger"] = webfinger
    db["client_name"] = client_name

    client = pump.get_registration()
    db["key"] = client[0]
    db["secret"] = client[1]
    db["expirey"] = client[2]

    tokens = pump.get_token()
    db["token"] = tokens[0]
    db["token_secret"] = tokens[1]
    
    save_database(db, store_path)

    # drop them into a shell
    cfg = Config()
    cfg.InteractiveShell.confirm_exit = False
    shell = InteractiveShellEmbed(
            config=cfg,
            banner1=welcome_banner.format(pypump=str(pump)),
            exit_msg="Remeber! Report any bugs to https://github.com/xray7224/PyPump/issues"
            )

    shell() 
