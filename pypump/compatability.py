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

"""
    This module is used to provide some python 2.6 to python 3.3 and above
    compatibility. This has been largely helped by the information at:
        http://lucumr.pocoo.org/2013/5/21/porting-to-python-3-redux/
"""

import sys
import types

# establish which version we're using
py_version = sys.version_info[0]

# handing strings
if py_version == 2:
    def to_bytes(string):
        """ Converts a python 2 string to bytes """
        if type(string) is types.StringType:
            return string

        # is it unicode?
        if type(string) is types.UnicodeType:
            return string.encode("utf-8")

        raise TypeError("Unknown type %s" % type(string))

    def to_unicode(string):
        """ Convert to unicode object """
        if type(string) is types.StringType:
            return string.decode("utf-8")
        if type(string) is types.UnicodeType:
            return string
        
        raise TypeError("Unknown type %s" % type(string))
elif py_version == 3:
    def to_bytes(string):
        """ Converts a python 3 string to bytes """
        if type(string) is bytes:
            return string

        if type(string) is str:
            return string.encode("utf-8")
    def to_unicode(string):
        """ Convert to unicode object """
        if type(string) is bytes:
            return string.decode("utf-8")
        if types(string) is str:
            return string
        raise TypeError("Unknown type %s" % string)
else:
    def to_bytes(string):
        """ not implemented """
        raise NotImplemented("Python version %s has no support for to_bytes" % py_version)


# types for isinstance(<x>, <type>)
if py_version == 2:
    text_type = str
    string_types = (str, unicode)
elif py_version == 3:
    text_type = str
    string_types = (str,)

# add decorators
if py_version == 2:
    def implement_to_string(cls):
        """ Adds to __str__ and __unicode__ methods when existing __str__ exists """
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda s: s.__unicode__().encode("utf-8")
        return cls
elif py_version == 3:
   def implement_to_string(cls):
        """ Adds __bytes__ to a clss with __str__ """
        cls.__bytes__ = lambda s: s.__str__().encode("utf-8")
        return cls
else:
    def implement_to_string(cls):
        raise NotImplemented("Python version %s has no support for implement_to_string" % py_version)

# is class?
def is_class(cls):
    """ Return bool depending on if cls is a class """
    return isinstance(cls, type)

# handles urllib change
if py_version == 2:
    import cgi
    parse_qs = cgi.parse_qs
elif py_version == 3:
    import urllib.parse
    parse_qs = urllib.parse.parse_qs
else:
    def parse_qs(*args, **kwargs):
        raise NotImplemented("Python version %s has no support for parse_qs" % py_version)

# raw_input vs. input
if py_version == 3:
    raw_input = input 
