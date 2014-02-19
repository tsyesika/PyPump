#!/usr/bin/env python
##
#   Copyright (C) 2013 Jessica T. (Tsyesika) <xray7224@googlemail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
##

import os
import json
import argparse

from pypump import PyPump, Client

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

        client=Client(
            webfinger=webfinger,
            type='native',
            name=self.client_name,
            key=self.config.get(webfinger, {}).get('key'),
            secret=self.config.get(webfinger, {}).get('secret')
        )

        self.pump = PyPump(
            client=client,
            token=self.config.get(webfinger, {}).get('token'),
            secret=self.config.get(webfinger, {}).get('token_secret'),
            verifier_callback=self.verifier
        )

        # Add account credentials to config in case we didnt have it already
        self.config[webfinger] = {
            'key' : self.pump.get_registration()[0],
            'secret' : self.pump.get_registration()[1],
            'token' : self.pump.get_token()[0],
            'token_secret' : self.pump.get_token()[1],
        }

        self.write_config()

    def verifier(self, url):
        """ Will ask user to click link to accept app and write code """
        webbrowser.open(url)
        print('A browser should have opened up with a link to allow us to access')
        print('your account, follow the instructions on the link and paste the verifier')
        print('Code into here to give us access, if the browser didn\'t open, the link is:')
        print(url)
        print()
        return input('Verifier: ').lstrip(" ").rstrip(" ")

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
            note_title = self.args.note_title
        else:
            note_title = None
        note_content = self.args.note_content
        mynote = self.pump.Note(display_name=note_title, content = note_content)
        mynote.to = self.pump.me.followers
        mynote.cc = self.pump.Public
        mynote.send()

        return mynote.id or None

if __name__ == '__main__':
    app = App()
    url = app.post_note()

    if url:
        print('Note posted')
    else:
        print('Note could not be posted')
