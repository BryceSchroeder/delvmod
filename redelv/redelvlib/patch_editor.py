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
import gtk,editors
MAGPIE_WARN = """This patch is currently in Magpie format. Saving it will
change the format to mag.py format, which is not compatible with Magpie. 
Proceed?
"""
class PatchEditor(editors.Editor):
    name = "Patch Editor"
    default_size = 512,320
    def gui_setup(self):
        self.set_default_size(*self.default_size)
        pbox = gtk.VBox(False,0)
        menu_items = (
            ("/File/Import", "<control>I", self.file_import, 0, None),
            ("/File/Export", "<control>E", self.file_export, 0, None),
            ("/File/Save Resource", "<control>S", self.file_save, 0, None),
            ("/File/Revert", None, self.load, 0, None),)
        accel = gtk.AccelGroup()
        ifc = gtk.ItemFactory(gtk.MenuBar, "<main>", accel)
        self.add_accel_group(accel)
        ifc.create_items(menu_items)
        self.menu_bar = ifc.get_widget("<main>")
        pbox.pack_start(self.menu_bar, False, True, 0)
        hbox = gtk.HBox(False,0)
        hbox.pack_start(gtk.Label("Patch Format:"),False,True,0)
        self.patch_format_box = gtk.Entry()
        self.patch_format_box.set_editable(False)
        hbox.pack_start(self.patch_format_box, True,True,0)
        pbox.pack_start(hbox,False)
        pbox.pack_start(gtk.Label("Patch Information"),False,True,0)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textbox = gtk.TextView()
        self.textbox.set_editable(True)
        sw.add(self.textbox)
        self.textbox.get_buffer().connect("changed",self.changed)
        pbox.pack_start(sw, True,True,5)
        self.add(pbox)
    def file_import(self,*argv):
        if self.unsaved and self.warn_unsaved_changes(): return
        path = self.ask_open_path()
        if not path: return
        try:
            f = open(path,'r')
            patch_info = str(f.read())
            f.close()
        except Exception,e:
            self.error_message("Couldn't read from '%s': %s"%(path,repr(e)))
        self.patch_info = patch_info
        self.textbox.get_buffer().set_text(patch_info)
        self.unsaved = True
    def changed(self,*argv):
        self.unsaved = True
        # serious lack of convenience methods here:
        self.patch_info = self.textbox.get_buffer().get_text(
            *self.textbox.get_buffer().get_bounds())
    def file_export(self,*argv):
        path = self.ask_save_path(default="%04X.txt"%self.res.resid)
        if not path: return
        try:
            f = open(path,'w')
            f.write(self.patch_info)
            f.close()
        except Exception,e:
            self.error_message("Couldn't write to '%s': %s"%(path,repr(e)))
    def file_save(self,*argv):
        if 'Magpie' in self.patch_format and not self.yn_ask(MAGPIE_WARN): 
            return
        self.rfile = self.res.as_file()
        self.rfile.write("MAGPY")
        self.rfile.write(self.patch_info)
        self.rfile.truncate()
        self.redelv.unsaved = True
        self.unsaved = False
            
    def editor_setup(self):
        self.load()
    def load(self, *argv):
        self.rfile = self.res.as_file()
        if self.rfile.read(5) == 'MAGPY':
            self.patch_info = str(self.rfile.read())
            self.patch_format = "mag.py [redelv]"
        else:
            self.patch_info = str(self.rfile.read_pstring(0x138))
            self.patch_format = "Magpie [DelvEd]"
        self.textbox.get_buffer().set_text(self.patch_info)
        self.patch_format_box.set_text(self.patch_format)
        self.redelv.unsaved = False
