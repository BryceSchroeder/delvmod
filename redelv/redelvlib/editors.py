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
import gtk, images
class Editor(gtk.Window):
    name = "Unspecified Editor"
    def __init__(self, redelv, resource, *argv, **argk):
        gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL, *argv,**argk)
        self.redelv = redelv
        self.res = resource
        self.set_title(self.name)
        self.gui_setup()
        self.unsaved = False
        self.connect("delete_event", self.delete_event)
        self.set_icon(
                gtk.gdk.pixbuf_new_from_file(images.icon_path))
        self.editor_setup()
    def delete_event(self, w=None, d=None):
        if self.unsaved: return self.ask_unsaved()
        return False
    def gui_setup(self):
        self.add(gtk.Label("[Unimplemented]"))
    def ask_unsaved(self):
        dialog = gtk.MessageDialog(self, 
            gtk.DIALOG_MODAL , 
            gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
            "You will lose unsaved changes to this resource; are you sure?")
        rv= gtk.RESPONSE_YES != dialog.run()
        dialog.destroy()
        return rv
    def editor_setup(self):
        print "The unimplemented editor is running, which is probably not good..."
