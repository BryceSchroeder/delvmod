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
import pygtk
pygtk.require('2.0')
import gtk, os, sys
import images
import graphics_editors
import generic_editors
import level_editors
import patch_editor
import sound_editors
import script_editor
import schedule_editor

# hokey
_EDITORS_BY_NAME = {
    "TileNameList": generic_editors.TileNameListEditor,
    "Map": level_editors.MapEditor,
    "PropList": level_editors.PropListEditor,
    "Landscale": graphics_editors.LandscapeEditor,
    "Portrait": graphics_editors.PortraitEditor,
    "Icon": graphics_editors.IconEditor,
    "TileSheet": graphics_editors.TileSheetEditor, 
    "ScheduleEditor": schedule_editor.ScheduleEditor,
    "Sized": graphics_editors.SizedEditor,
    "Sound": sound_editors.SoundEditor,
    "Patch": patch_editor.PatchEditor,
    "Hex": generic_editors.HexEditor,
    "Script": script_editor.ScriptEditor,
}
_EDITORS_FOR_RESOURCE = {
    0xF004: generic_editors.TileNameListEditor,
    0xF00B: schedule_editor.ScheduleEditor,
    0x8EFF: graphics_editors.SizedEditor,
}
_EDITORS_FOR_SUBINDEX = {
    127: level_editors.MapEditor,
    128: level_editors.PropListEditor,
    131: graphics_editors.LandscapeEditor,
    135: graphics_editors.PortraitEditor,
    137: graphics_editors.IconEditor,
    141: graphics_editors.TileSheetEditor,
    142: graphics_editors.SizedEditor,
    144: sound_editors.SoundEditor,
    254: patch_editor.PatchEditor,
}
for n in xrange(0x7F): _EDITORS_FOR_SUBINDEX[n] = script_editor.ScriptEditor
del _EDITORS_FOR_SUBINDEX[3]

def editor_for_name(name):
    return _EDITORS_BY_NAME.get(name, generic_editors.HexEditor)

def editor_for_subindex(subindex):
    return _EDITORS_FOR_SUBINDEX.get(subindex, generic_editors.HexEditor)
def editor_for_resource(resid):
    return _EDITORS_FOR_RESOURCE.get(resid, 
           _EDITORS_FOR_SUBINDEX.get((resid>>8)-1, generic_editors.HexEditor))

class Receiver(gtk.Window):
    pass

class FileInfo(Receiver):
    def __init__(self,redelv, *args,**argk):
        gtk.Window.__init__(self, *args, **argk)
        self.redelv = redelv
        self.set_title('Information')
        self.set_default_size(320,128)
        self.set_icon(gtk.gdk.pixbuf_new_from_file(images.inspect_path))
        #self.redelv.filechange.append(self)
        #self.redelv.subindexchange.append(self)
        self.redelv.resourcechange.append(self)
        self.connect("delete_event", (lambda *x: self.hide() or True))
        
        pbox = gtk.VBox(False, 5)

        hrow = gtk.HBox(False, 0)
        hrow.pack_start(gtk.Label("Resource ID"),False,True,0)
        self.resource_id = gtk.Entry()
        self.resource_id.set_editable(False)
        hrow.pack_start(self.resource_id, True,True,0)
        hrow.pack_start(gtk.Label("Index Page"),False,True,0)
        self.subindex = gtk.Entry()
        self.subindex.set_editable(False)
        hrow.pack_start(self.subindex, True,True,0)
        hrow.pack_start(gtk.Label("Index"),False,True,0)
        self.n = gtk.Entry()
        self.n.set_editable(False)
        hrow.pack_start(self.n, True,True,0)
        pbox.pack_start(hrow,True,True,0)

        hrow = gtk.HBox(False, 0)
        hrow.pack_start(gtk.Label("Size"),False,True,0)        
        self.size = gtk.Entry()
        self.size.set_editable(False)
        hrow.pack_start(self.size,True,True,0)
        hrow.pack_start(gtk.Label("Offset on Disk"),False,True,0)
        self.offset = gtk.Entry()
        self.offset.set_editable(False)
        hrow.pack_start(self.offset,True,True,0)
        pbox.pack_start(hrow,True,True,0)

        hrow = gtk.HBox(False, 0)
        self.encrypted = gtk.CheckButton("Known Encryption?")
        self.encrypted.set_sensitive(False)
        self.encrypted.set_mode(True)
        self.changed = gtk.CheckButton("Loaded?")
        hrow.pack_start(self.encrypted,False,True,0)
        self.changed.set_sensitive(False)
        self.changed.set_mode(True)
        hrow.pack_start(self.changed,False,True,0)
        pbox.pack_start(hrow,True,True,0)


        self.add(pbox)
        
        self.signal_resourcechange(None)
    def signal_filechange(self,d=None):
        self.signal_resourcechange(d)
    #def signal_subindexchange(self,d=None):
    #    self.signal_change(d)
    def signal_resourcechange(self,d=None):
        res = self.redelv.current_resource
        if res:
            self.set_title(
                'Information on [%04X]'%self.redelv.current_resource_id)
            self.resource_id.set_text("0x%04X"%self.redelv.current_resource_id)
            self.n.set_text("%d"%res.n)
            self.subindex.set_text("%d"%res.subindex)
            self.size.set_text("0x%08X"%len(res.data))
            self.offset.set_text("0x%08X"%res.offset)
            self.encrypted.set_active(bool(res.canon_encryption))
            self.changed.set_active(bool(res.loaded))
            
        else:
            self.set_title("Information")
            for field in [self.n,self.subindex,self.resource_id,
                self.offset,self.size]:
                field.set_text("")
            for field in [self.encrypted,self.changed]: field.set_active(False)
class FileMetadata(Receiver):
    def __init__(self,redelv, *args,**argk):
        gtk.Window.__init__(self, *args, **argk)
        self.redelv = redelv
        self.set_title('File Metadata for "%s"'%redelv.opened_file)
        self.set_default_size(320,128)
        self.set_icon(gtk.gdk.pixbuf_new_from_file(images.inspect_path))
        self.redelv.filechange.append(self)
        self.connect("delete_event", (lambda *x: self.hide() or True))

	pbox = gtk.VBox(False,2)
        trow = gtk.HBox(False,0)
        trow.pack_start(gtk.Label("Scenario Title:"),False,True,0)
        self.scenario_title = gtk.Entry(255)
        trow.pack_start(self.scenario_title, True,True,0)
        pbox.pack_start(trow,False,True,0)
        trow = gtk.HBox(False,0)
        trow.pack_start(gtk.Label("Player Name:"),False,True,0)
        self.player_name = gtk.Entry(255)
        trow.pack_start(self.player_name, True,True,0)
        pbox.pack_start(trow,False,True,0)
        trow = gtk.HBox(False,0)
        trow.pack_start(gtk.Label("Unknown 0x40:"),False,True,0)
        self.unknown_40 = gtk.Entry(4)
        self.unknown_40.set_editable(False)
        trow.pack_start(self.unknown_40,True,True,0)
        trow.pack_start(gtk.Label("Unknown 0x42:"),False,True,0)
        self.unknown_42 = gtk.Entry(4)
        self.unknown_42.set_editable(False)
        trow.pack_start(self.unknown_42,True,True,0)
        trow.pack_start(gtk.Label("Unknown 0x48:"),False,True,0)
        self.unknown_48 = gtk.Entry(4)
        self.unknown_48.set_editable(False)
        trow.pack_start(self.unknown_48,True,True,0)
        pbox.pack_start(trow,False,True,0)

        trow = gtk.HBox(False,0)
        trow.pack_start(gtk.Label("Master Index Offset:"),False,True,0)
        self.master_index_offset = gtk.Entry(10)
        self.master_index_offset.set_editable(False)
        trow.pack_start(self.master_index_offset,True,True,0)
        trow.pack_start(gtk.Label("Master Index Length:"),False,True,0)
        self.master_index_length = gtk.Entry(10)
        self.master_index_length.set_editable(False)
        trow.pack_start(self.master_index_length,True,True,0)
        pbox.pack_start(trow,False,True,0)

        trow = gtk.HBox(False,0)
        trow.pack_start(gtk.Label("Source:"),False,True,0)
        self.source_string = gtk.Entry()
        self.source_string.set_editable(False)
        trow.pack_start(self.source_string,True,True,0)
        pbox.pack_start(trow,False,True,0)
 	self.add(pbox)


        self.scenario_title.connect("changed", self.edit_scenario_title)
        self.player_name.connect("changed", self.edit_player_name)
        self.signal_filechange(None)
    def edit_scenario_title(self,w,data=None):
        newtitle = self.scenario_title.get_text()
        self.redelv.set_savedstate(
             newtitle !=  self.redelv.archive.scenario_title)
        self.redelv.archive.scenario_title = newtitle
    def edit_player_name(self, *argv):
        newname = self.player_name.get_text()
        self.redelv.set_savedstate(newname != self.redelv.archive.player_name)
        self.redelv.archive.player_name = newname

    def signal_filechange(self, d=None):
        if not self.redelv.archive:
            for box in [self.scenario_title,self.unknown_40,self.unknown_42,
                        self.unknown_48,self.master_index_length, 
                        self.master_index_offset,self.player_name]: 
                box.set_text("")
                box.set_editable(False)
            self.source_string.set_text("[No File Opened]")
        else:
            for box in [self.scenario_title,self.player_name]:
                box.set_editable(True)
            self.player_name.set_text(self.redelv.archive.player_name)
            self.scenario_title.set_text(self.redelv.archive.scenario_title)
            self.unknown_40.set_text("0x%02X"%self.redelv.archive.unknown_40)
            self.unknown_42.set_text("0x%02X"%self.redelv.archive.unknown_42)
            self.unknown_48.set_text("0x%02X"%self.redelv.archive.unknown_48)
            self.master_index_offset.set_text(
                "0x%08X"%self.redelv.archive.master_index_offset)
            self.master_index_length.set_text(
                "0x%08X"%self.redelv.archive.master_index_length)
            self.source_string.set_text(self.redelv.archive.source_string)

