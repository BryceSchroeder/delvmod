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
import gtk
class Editor(gtk.Window):
    name = "Unspecified Editor"
    def __init__(self, redelv, resource, *argv, **argk):
        gtk.Window.__init__(gtk.WINDOW_TOPLEVEL, *argv,**argk)
        self.redelv = redelv
        self.res = resource
        self.set_title(self.name)
        self.gui_setup()
        self.unsaved = False
        self.connect("delete_event", self.delete_event)
    def delete_event(self):
        if self.unsaved: return self.ask_unsaved()
        return True
