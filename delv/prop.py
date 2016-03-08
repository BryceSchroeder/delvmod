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
# Please do not make trouble for me or the Technical Documentation Project by
# using this software to create versions of the "Cythera Data" file which 
# have bypassed registration checks.
# Also, remember that the "Cythera Data" file is copyrighted by Ambrosia and
# /or Glenn Andreas, and publishing modified versions without their permission
# would violate that copyright. 
#
# "Cythera" and "Delver" are trademarks of either Glenn Andreas or 
# Ambrosia Software, Inc. 
import store

class Prop(object):
    def __init__(self, pid, tile, offset_by_aspect, scripts, library):
        self.scripts=scripts
        self.tile = tile
        self.prop_type = pid
        self.offset_by_aspect = offset_by_aspect
        self.library = library
    def get_tile(self, aspect, rotated=False):
        return self.tile + (aspect)
    def get_debug_tile(self, aspect):
        return 0x016C+aspect #0x017F
    def get_offset(self, aspect, rotated=False):
        return self.offset_by_aspect[aspect]
    def get_name(self, aspect=0):
        return self.library.get_tile(self.get_tile(aspect)).get_name()

