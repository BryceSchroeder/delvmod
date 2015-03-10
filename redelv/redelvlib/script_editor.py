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
#
# "Cythera" and "Delver" are trademarks of either Glenn Andreas or 
# Ambrosia Software, Inc. 
import csv
import gtk, pango
import editors
import delv.store
import sys
import images
class ScriptEditor(editors.Editor):
    name = "Scripting System Editor"
    default_size = 680,512
    icon = images.script_path
    def gui_setup(self): 
        pbox = gtk.VBox(False,0)
        self.set_default_size(*self.default_size)
        menu_items = (
            ("/File/Import Text", "<control>I", self.file_import, 0, None),
            ("/File/Export Text", "<control>E", self.file_export, 0, None),
            ("/File/Save Resource", "<control>S", self.file_save, 0, None),
            ("/File/Revert", None, self.load, 0, None),
            ("/Edit/Edit in External Text Editor", "<control>G", 
                 self.edit_external, 0, None),
            ("/Edit/Check Syntax", "<control>T", 
                 self.edit_syntax, 0, None),

            #("/Edit/Copy", "<control>C", self.edit_copy, 0, None),
            #("/Edit/Paste","<control>V", self.edit_paste, 0, None),
            )
        accel = gtk.AccelGroup()
        ifc = gtk.ItemFactory(gtk.MenuBar, "<main>", accel)
        self.add_accel_group(accel)
        ifc.create_items(menu_items)
        self.menu_bar = ifc.get_widget("<main>")
        pbox.pack_start(self.menu_bar, False, True, 0)

        self.text_buf = gtk.TextBuffer()
        self.text_buf.set_text(" Nothing Loaded ".center(78,'#'))
        self.text_view = gtk.TextView()
        self.text_view.set_buffer(self.text_buf)
        fontdesc = pango.FontDescription("monospace 10")
        self.text_view.modify_font(fontdesc)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        sw.add(self.text_view)
        pbox.pack_start(sw, True, True, 0)
        hbox = gtk.HBox(False,0)
        hbox.pack_start(gtk.Label("Status:"), False, True, 0)
        self.asm_status = gtk.Entry()
        self.asm_status.set_editable(False)
        self.asm_status.set_text("Disassembling binary... ")
        hbox.pack_start(self.asm_status, True, True, 0)
        pbox.pack_start(hbox, False, True, 0)
        self.add(pbox)

    
    def editor_setup(self):
        self.load()
    def load(self, *argv):
        self.canonical_object.load_from_library(self.redelv.get_library())
        asmc = self.canonical_object.disassemble()
        self.text_buf.set_text("<DISASSEMBLING>")
        self.text_buf.set_text(asmc)
        self.set_title("Script Editor [%04X]"%self.res.resid)
        self.asm_status.set_text("Disassembly complete.")
        #self.canonical_object.printout(sys.stdout,0)
    def edit_external(self, *argv):
        self.open_external_editor(
            self.redelv.preferences['assembly_editor_cmd'],
            self.external_writeout, self.external_readin,
            file_extension = '.rasm')
    def external_writeout(self, target, cbdata):
        target.write(str(self.text_buf.get_text(
             *self.text_buf.get_bounds())))
        target.flush()
    def external_readin(self, path, cbdata):
        self.asm_status.set_text("Changed in external editor.")
        self.text_buf.set_text(open(path,'rb').read())
        self.set_unsaved()
    def file_import(self,*args):
        #if self.unsaved and self.warn_unsaved_changes(): return 
        path = "<undefined>"
        try:
            path = self.ask_open_path()
            if not path: return
            data = open(path,'rb').read()
        except Exception,e:
            self.error_message("Couldn't open '%s': %s"%(path,
                repr(e)))
            return
        self.set_unsaved()
        self.asm_status.set_text("Imported a file (not assembled yet.)")
        # set text to data here
    
    def file_export(self, *args):
        path = self.ask_save_path(default = "Script%04X.txt"%self.res.resid)
        if not path: return
        if not path.endswith(".rdsm"): path += ".rdsm"
        try:
            open(path,'rb').write("EXPROT TEST")
        except Exception,e:
            self.error_message("Couldn't open '%s': %s"%(path,
                repr(e)))
            return
    def edit_syntax(self, *args):
        try:
            av = self.assemble()
        except delv.script.AssemblerError, e:
            self.error_message(str(e))
            self.asm_status(str(e))
        self.asm_status.set_text("Assembled successfully; %d bytes."%len(av))
    def file_save(self, *args):
        # Assemble of course.
        # try:
        #     self.res.set_data(self.assemble())
        # except syntax errors blah:
        self.asm_status.set_text("I only pretended to save your work.")
        self.set_saved()
