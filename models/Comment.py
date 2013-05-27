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

from datetime import datetime

class Comment:
    
    body = ""
    note = None # note it's a comment to
    updated = None
    published = None
    likes = []

    def __init__(self, body, note, published=None, updated=None, likes=[]):
        body = body
        note = note
        likes = likes
        
        if published:
            self.published = published 
        else:
            self.published = datetime.now()

        if updated:
            self.updated = updated
        else:
            self.updated = self.published

    def like(self):
        """ Will like the comment """
        pass

    def unlike(self):
        """ If comment is liked, it will unlike it """
        pass

    def delete(self):
        """ Will delete the comment if the comment is posted by you """
        pass

