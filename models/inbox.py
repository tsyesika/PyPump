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

from models import AbstractModel

class Inbox(AbstractModel):

    TYPE = "inbox"

    _inbox = []
    _limit = []

    def __getitem__(self, key):
        """ Adds Inbox[<inbox>] """
        return self._inbox[key]

    def __getslice__(self, start, end):
        """ allows for a limit """
        self._limit = [start, end]

    def __len__(self):
        """ Gives amount of items in the inbox """
        return len(self._inbox)
