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
import archive
class Library(object):
    """This class is a wrapper around one or more Delver archives, and 
       facilitates retrieving various kinds of objects by their resource
       ID. I.e, whereas the delv.archive.Scenario object will return a 
       delv.archive.Resource object when asked for resource ID 0x8E91,
       the library will return a delv.graphics.TileSheet object. 

       The Library also provides facilities that integrate multiple
       resources into logical parts, e.g. it unifies graphical tiles
       with their names and properties, and allows them to be retrieved
       under a simple API.
 
       The library is a read-only facility and it assumes that its underlying
       archive does not change from under it. If that assumption is not true,
       i.e. if you are using it as part of an editor, you will need to tell
       the library the underlying archive has changed with .update(). This 
       will purge all caches."""
    def __init__(self, *archives):
        """Create a new library, using the archives provided. The search path
           will be from last to first, i.e. if you say Library(A, B, C) and 
           archives B and C both contain a resource 0xFFFF, and you ask for
           0xFFFF, you will get the one from archive C."""
        self.archives = archives[::-1]
    def get_resource(self, resid):
        """Get a resource by its resource ID or subindex,n pair."""
        for archive in self.archives:
            r = archive.get(resid)
            if r: return r
        return None
    def get_object(self, resid):
        """Get the appropriate kind of object for a specified resource."""
        r = self.get_resource(resid)
        if not r: return None
        C = hints.class_by_resid(r.resid)
        if not C: return None
        return C(r)
