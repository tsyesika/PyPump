# -*- coding: utf-8 -*-
##
# Copyright (C) 2010-2012 Reality <tinmachin3@gmail.com> and Psychedelic Squid <psquid@psquid.net>
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

from setuptools import setup

setup(name='PyPump',
      version='0.1',
      description='Python interface for the Pump API',
      url='https://github.com/xray7224/PyPump',
      author='Jessica Tallon',
      author_email='xray7224@googlemail.com',
      license='GPLv3',
      packages=['pypump'],
      zip_safe=False,
      install_requires=[
          'oauth',
          ]
)
