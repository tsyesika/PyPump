#!/usr/bin/env python

import os, json, argparse
from pypump import PyPump

class App(object):

    client_name = 'pypump-post-note'
    pump = None
    config_file = os.path.join(os.environ['HOME'],'.config',
                               client_name, 'config.json')
    config = dict()

    def __init__(self):
        """ Init app and log in to our pump.io account """

        # Set up argparse
        self.parser = argparse.ArgumentParser(description='Post a note to the pump.io network')
        self.parser.add_argument('-u', '--user', dest='webfinger', required=True, help='user@example.com')
        self.parser.add_argument('-t', '--title', dest='note_title', default=None, help='Note title')
        self.parser.add_argument('-n', '--note', dest='note_content', required=True, help='Note content')
        self.args = self.parser.parse_args()

        self.read_config()

        # Try to login to our pump.io account using account credentials
        # from config, if our webfinger is not found in config we will
        # have to authorize the app with our account.
        webfinger = self.args.webfinger
        self.pump = PyPump(
            webfinger,
            client_name = self.client_name,
            **self.config.get(webfinger, {})
        )

        # Add account credentials to config in case we didnt have it already
        self.config[webfinger] = {
            'key' : self.pump.get_registration()[0],
            'secret' : self.pump.get_registration()[1],
            'token' : self.pump.get_token()[0],
            'token_secret' : self.pump.get_token()[1],
        }

        self.write_config()

    def write_config(self):
        """ Write config to file """
        if not os.path.exists(os.path.dirname(self.config_file)):
            os.makedirs(os.path.dirname(self.config_file))
        with open(self.config_file, 'w') as f:
            f.write(json.dumps(self.config))
            f.close()
    
    def read_config(self):
        """ Read config from file """
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.loads(f.read())
                f.close()
        except IOError:
            return False
        return True

    def post_note(self):
        """ Post note and return the URL of the posted note """
        if self.args.note_title:
            note_title = "<h1>{title}</h1>".format(title=self.args.note_title)
        else:
            note_title = ""
        note_content = self.args.note_content
        mynote = self.pump.Note(note_title + note_content)
        mynote.to = self.pump.me.followers
        mynote.cc = self.pump.Public
        if mynote.send():
            return mynote.id
        else:
            return None

if __name__ == '__main__':
    app = App()
    url = app.post_note()

    if url:
        print('Note posted')
    else:
        print('Note could not be posted')
