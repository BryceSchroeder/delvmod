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
import delv
import delv.sound
import os, tempfile, struct, wave, subprocess

MAGPIE_WARN = """This patch is currently in Magpie format. Saving it will
change the format to mag.py format, which is not compatible with Magpie. 
Proceed?
"""
class SoundEditor(editors.Editor):
    name = "Sound Editor"
    default_size = 320,128
    s_lsint16 = struct.Struct('<h')
    def gui_setup(self):
        self.set_default_size(*self.default_size)
        pbox = gtk.VBox(False,0)
        menu_items = (
            ("/File/Import WAV", "<control>I", self.file_import, 0, None),
            ("/File/Export WAV", "<control>E", self.file_export, 0, None),
            ("/File/Save Resource", "<control>S", self.file_save, 0, None),
            ("/File/Revert", None, self.load, 0, None),)
        accel = gtk.AccelGroup()
        ifc = gtk.ItemFactory(gtk.MenuBar, "<main>", accel)
        self.add_accel_group(accel)
        ifc.create_items(menu_items)
        self.menu_bar = ifc.get_widget("<main>")
        pbox.pack_start(self.menu_bar, False, True, 0)
        hbox = gtk.HBox(False,0)
        hbox.pack_start(gtk.Label("Sampling Rate:"),False,True,0)
        self.sample_rate = gtk.Entry()
        self.sample_rate.set_width_chars(10)
        self.sample_rate.set_editable(False)
        hbox.pack_start(self.sample_rate, True,True,0)
        hbox.pack_start(gtk.Label("Flags:"),False,True,0)
        self.flags = gtk.Entry()
        self.flags.set_width_chars(10)
        self.flags.set_editable(False)
        hbox.pack_start(self.flags, True,True,0)
        self.flags2 = gtk.Entry()
        self.flags2.set_width_chars(6)
        self.flags2.set_editable(False)
        hbox.pack_start(self.flags2, True,True,0)
        pbox.pack_start(hbox,False)
        self.play_button = gtk.Button("Play Sound")
        pbox.pack_start(self.play_button, False, True, 0)
        pbox.pack_start(gtk.Label("Sound Player Command"),False,True,0)
        self.play_command = gtk.Entry()
        self.play_command.set_text(self.redelv.preferences['play_sound_cmd'])
        pbox.pack_start(self.play_command, True,True,5)
        self.add(pbox)
        self.play_button.connect("clicked", self.play_sound)
    def file_import(self,*argv):
        self.error_message("Not implemented yet")
        self.unsaved = True
    def file_export(self,*argv):
        path = self.ask_save_path(default = "Asnd%04X.wav"%self.res.resid)
        if not path: return
        if not path.endswith(".wav"): path += ".wav"
        try:
            self.wave_out(open(path, 'wb'))
        except Exception, e:
            self.error_message("Couldn't write %s: %s"%(path,repr(e))
    def wave_out(self, fileobj):
        wavout = wave.open(fileobj, 'wb')
        wavout.setnchannels(1)
        wavout.setsampwidth(2)
        wavout.setframerate(self.sound.get_rate())
        frames = bytearray()
        for sample in self.sound.get_samples():
            frames += self.s_lsint16.pack(sample)
        wavout.writeframes(frames)
        wavout.close()
    def file_save(self,*argv):
        
        self.redelv.unsaved = True
        self.unsaved = False
    def play_sound(self, *argv):
        self.temp = tempfile.NamedTemporaryFile('wb')
        self.wave_out(self.temp)
        command = self.play_command.get_text()
        subprocess.Popen(command%self.temp.name, shell=True)
    def editor_setup(self):
        self.load()

    def load(self, *argv):
        self.rfile = self.res.as_file()
        self.set_title("Sound Editor - %04X"%self.res.resid)
        self.sound = delv.sound.Asnd(self.rfile)
        self.sample_rate.set_text("%d Hz"%self.sound.get_rate())
        self.flags.set_text("0x%08X"%self.sound.flags)
        self.flags2.set_text("0x%04X"%self.sound.flags2)
        self.unsaved = False
