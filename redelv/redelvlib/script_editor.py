#!/usr/bin/env python
# Copyright 2015-16 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
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
import sys, traceback
import images
import delv.rdasm
import urllib2
from cStringIO import StringIO
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
            ("/File/Revert to Saved Source", None, self.load_source, 0, None),
            ("/File/Revert to Disassembly", None, self.load_disassemble, 0, 
                     None),
            ("/File/Load from TAUCS", None, self.load_taucs, 0, None),
            ("/File/Assemble and Save", "<control>S", self.file_save, 0, None),
            ("/File/Save Source Code", "<shift><control>S", 
                  self.do_save_source,
                  0, None),
            ("/Edit/Edit in External Text Editor", "<control>G", 
                 self.edit_external, 0, None),
            ("/Edit/Purge Source", None, 
                 self.purge, 0, None),
            #("/Edit/Check Syntax", "<control>T", 
            #     self.edit_syntax, 0, None),

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
        self.text_buf.set_text(" Nothing Loaded ".center(78,';'))
        self.text_view = gtk.TextView()
        self.text_view.set_buffer(self.text_buf)
        self.text_view.set_wrap_mode(gtk.WRAP_CHAR)
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
        self.auto_assemble = gtk.ToggleButton(
            "Auto-Assemble") 
        self.auto_assemble.set_active(True)
        hbox.pack_start(self.auto_assemble, False, True, 0)
        self.save_source = gtk.ToggleButton(
            "Auto-save Source") 
        self.save_source.set_active(True)
        hbox.pack_start(self.save_source, False, True, 0)
        pbox.pack_start(hbox, False, True, 0)
        self.add(pbox)
        self.assembler = None
        self.cycle_check = False

    def get_assembler(self):
        if not self.assembler:
            self.errorstream = StringIO()
            self.asm_status.set_text("Preparing assembler...")
            while gtk.events_pending(): gtk.main_iteration()
            self.assembler = delv.rdasm.Assembler(
                                     message_stream=self.errorstream,
                                     filename="<res 0x%04X>"%self.res.resid,
                                     )
            # check to make sure that we can assemble this file correctly
            self.asm_status.set_text("Checking cycle validity... ")
            while gtk.events_pending(): gtk.main_iteration()
        if not self.cycle_check:
            obin = self.assembler.assemble(self.original_disassembly)
            if self.canonical_object.data != obin:
                ofs1 = ((self.canonical_object.data[0]<<8)
                        |self.canonical_object.data[1])
                ofs2 = ((ord(obin[0])<<8)
                        |ord(obin[1]))
                if (ofs1 == ofs2 
                    and obin[0:ofs1] == self.canonical_object.data[0:ofs1]):
                    self.asm_status.set_text(
                    "Pass with table mismatch; ready.")
                else:
                    self.asm_status.set_text(
                        "FAILED CHECK: This resource can't be reassembled.")
                    return None
            else:
                self.asm_status.set_text("Passed validation check; ready.")
            self.cycle_check = True
            while gtk.events_pending(): gtk.main_iteration()
                

        return self.assembler
    
    def editor_setup(self):
        self.load()
        self.text_buf.connect("changed", self.textbuf_changed, None)

    def load_taucs(self, *argv):
        try:
            data = urllib2.urlopen(
                self.redelv.preferences['source_archive']%self.res.resid
                ).read()
        except urllib2.HTTPError:
            self.asm_status.set_text(
                "ERROR: Could not find canonical sources for this resource.")
            #message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, 
            #                            buttons=gtk.BUTTONS_OK)
            #message.set_markup(
            #    "Could not find canonical sources for this resource.")
            #message.run()
            return
        self.cycle_check = True
        self.asm_status.set_text(
                "Source successfully downloaded from the archive.")
        data = data[data.find('{{{')+3:data.find('}}}')
                                          ].strip().replace('\r','')
        self.text_buf.set_text(data)
        self.set_unsaved()
    def _loadsource(self):
        code = self.redelv.get_library().get_code_store()
        src = code.get(self.res.resid)
        self.cycle_check = True
        return src
    def purge(self, *argv):
        code = self.redelv.get_library().get_code_store()
        code.purge(self.res.resid)
        self.asm_status.set_text(
                "Saved source code deleted.")

    def do_save_source(self, *argv):
        code = self.redelv.get_library().get_code_store()
        code.save_source(self.res.resid, self.text_buf.get_text(
                           *self.text_buf.get_bounds()))
    def load_source(self, *argv):
        src = self._loadsource()
        if not src:
            self.asm_status.set_text(
                "ERROR: You have no saved source for this resource.")
            return False
        else:
            self.cycle_check = True
            self.text_buf.set_text(src)
            return True
    def load(self, *argv):
        src = self._loadsource()
        if src:
            self.text_buf.set_text(src)
            self.asm_status.set_text(
                "Loaded your saved source for this resource.")
        else:
            self.load_disassemble(*argv)


    def load_disassemble(self, *argv):
        self.set_title("Script Editor [%04X]"%self.res.resid)
        self.text_buf.set_text("; DISASSEMBLING")
        #self.canonical_object.load_from_library(
        #     self.redelv.get_library())
        asmc = self.canonical_object.disassemble()
        self.original_disassembly = asmc
        self.text_buf.set_text(asmc)
        self.asm_status.set_text("Disassembly complete.")
        #self.canonical_object.printout(sys.stdout,0)
    def edit_external(self, *argv):
        self.text_view.set_editable(False)
        self.open_external_editor(
            self.redelv.preferences['assembly_editor_cmd'],
            self.external_writeout, self.external_readin,
            file_extension = '.rdasm')
    def external_writeout(self, target, cbdata):
        target.write(str(self.text_buf.get_text(
             *self.text_buf.get_bounds())))
        target.flush()
    def external_readin(self, path, cbdata):
        self.asm_status.set_text("Changed in external editor.")
        self.text_buf.set_text(open(path,'rb').read())
        self.set_unsaved()
        if self.auto_assemble.get_active(): self.file_save()
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
        path = self.ask_save_path(default = "Script%04X.rdasm"%self.res.resid)
        if not path: return
        if not path.endswith(".rdasm"): path += ".rdasm"
        try:
            open(path,'rb').write("EXPORT TEST")
        except Exception,e:
            self.error_message("Couldn't open '%s': %s"%(path,
                repr(e)))
            return
    def edit_syntax(self, *args):
        #try:
        #    av = self.assemble()
        #except delv.script.AssemblerError, e:
        #    self.error_message(str(e))
             # except syntax errors blah:
        self.asm_status.set_text("Not implemented yet. Just try it and see.")
    def textbuf_changed(self, *args):
        if self.save_source.get_active():
            self.do_save_source()
        self.set_unsaved()
    def file_save(self, *args):
        # Assemble of course.
        # try:
        asm = self.get_assembler()
        if not asm:
            return
        src = str(self.text_buf.get_text(*self.text_buf.get_bounds()))
        self.asm_status.set_text("Assembling source of %d bytes..."%len(src))
        while gtk.events_pending(): gtk.main_iteration()
        av = self.get_assembler().assemble(src)
        self.asm_status.set_text("Assembled successfully; %d bytes."%len(av))
        self.res.set_data(av)
        self.redelv.set_unsaved()
        self.set_saved()
        self.assembler = None
