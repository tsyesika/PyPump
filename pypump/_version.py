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

##
# Version format (borrowed from mediagoblin):
# x.y       - final
# x.y.dev   - development version
##

__version__ = "0.5.dev"

## IMPORTANT: Code below is for calculating version not setting it

def get_release():
    """ Returns Release number """
    return __version__

def get_version():
    """ Returns version number (with .dev, .alpha, etc. parsed out) """
    return ".".join(__version__.split(".")[0:2])
