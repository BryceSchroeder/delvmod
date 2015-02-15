#!/usr/bin/env python
# Copyright 2015 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
# Wiki: http://www.ferazelhosting.net/wiki/delv
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# "Cythera" and "Delver" are trademarks of either Glenn Andreas or 
# Ambrosia Software, Inc. 

from distutils.core import setup
import setuptools

setup(name='delv',
      version='0.1.4',
      description='Module for making tools interoperable with Delver',
      author='Bryce Schroeder',
      author_email='bryce.schroeder@gmail.com',
      license='GPL-3',
      url='http://www.ferazelhosting.net/wiki/delv',
	classifiers=["Development Status :: 2 - Pre-Alpha",
                     "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                     "Topic :: Games/Entertainment :: Role-Playing"],
      packages=['delv'])
