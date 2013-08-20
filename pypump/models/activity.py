##
# Copyright (C) 2013 Jessica T. (Tsyesika) <xray7224@googlemail.com>
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##

from dateutil.parser import parse as parse
import re
from pypump.models import AbstractModel
from pypump.compatability import *

#TODO clean up and move to own file
class Generator(object):
    """ The client used to generate the activity """
    display_name = None
    id = None

    def __repr__(self):
        return "<Generator: {g_name}>".format(g_name=self.display_name)

    def __init__(self, display_name=display_name, id=id, *args, **kwargs):
        self.display_name = display_name
        self.id = id

        super(Generator, self).__init__(*args, **kwargs)

    @classmethod
    def unserialize(cls, data):
        id = data["id"]
        display_name = data["displayName"] if "displayName" in data else "Unknown client"

        return cls(id=id, display_name=display_name)

#TODO clean up and move to own file
@implement_to_string
class Unknown(AbstractModel):
    """ This class is used when we can't find a matching object type """
    TYPE = None
    display_name = None

    def __repr__(self):
        return self.display_name if self.display_name else self.TYPE

    def __str__(self):
        return str(self.__repr__())

    def __init__(self, object_type=None, display_name=None, *args, **kwargs):
        self.TYPE = object_type
        self.display_name = display_name

        super(Unknown, self).__init__(*args, **kwargs)

    @classmethod
    def unserialize(cls, data):
        object_type = data["objectType"] if "objectType" in data else ""
        display_name = data["displayName"] if "displayName" in data else ""

        return cls(display_name=display_name, object_type=object_type)

@implement_to_string
class Activity(AbstractModel):
    obj = None
    verb = None
    actor = None
    generator = None
    updated = None
    url = None
    published = None
    content = None
    id = None

    def __init__(self, obj, verb, actor, generator,
                 updated, url, published, content, id, *args, **kwargs):

        super(Activity, self).__init__(*args, **kwargs)

        self.obj = obj
        self.verb = verb
        self.actor = actor
        self.generator = generator
        self.updated = updated
        self.url = url
        self.published = published
        self.content = content
        self.id = id
    
    def __repr__(self):
        return '<Activity: {webfinger} {verb}ed {model}>'.format(
                webfinger=self.actor.id[5:], # [5:] to strip of acct:
                verb=self.verb.rstrip("e"), # english: e + ed = ed
                model=self.obj.objectType
                )

    def __str__(self):
        return str(self.__repr__())

    @classmethod
    def unserialize(cls, data):
        """ From JSON -> Activity object """

        dataobj = data["object"]
        obj_type = dataobj["objectType"].capitalize()

        if "author" not in dataobj:
            # author is not set for posted objects in inbox/major, so we add it
            dataobj["author"] = data["actor"]

        try:
            objekt = getattr(cls._pump, obj_type)
            obj = objekt.unserialize(dataobj)
        except AttributeError:
            obj = Unknown.unserialize(dataobj)

        verb = data["verb"]
        actor = cls._pump.Person.unserialize(data["actor"])
        # generator is not always there (at least not for verb:'update' obj:Person)
        generator = Generator.unserialize(data["generator"]) if "generator" in data else None
        updated = parse(data["updated"])
        url = data["url"]
        published = parse(data["published"])
        content = data["content"]
        id = data["id"]

        return cls(obj, verb, actor, generator, updated,
                   url, published, content, id)

