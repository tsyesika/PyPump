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
from Objects.Note import Note

time_format = "%Y-%m-%dT%H:%M:%SZ"

def parse_note(data):
    """ Takes raw API data and make an Note object """
    try:
        content = data["content"]
    except KeyError:
        content = ""

    try:
        to = data["to"]
    except KeyError:
        to = []

    try:
        cc = data["cc"]
    except KeyError:
        cc = data["cc"]

    try:
        actor = data["actor"]
    except KeyError:
        actor = None

    try:
        published = datetime.strptime(time_format, date["published"])
    except KeyError:
        published = None
        
    try:
        updated = datetime.strptime(time_format, data["updated"])
    except KeyError:
        updated = published

    return Note(
        content, actor, to, actor, 
        published=published, updated=updated
    ) 
