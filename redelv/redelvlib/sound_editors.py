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
    s_lsint8 = struct.Struct('b')
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
        hbox.pack_start(gtk.Label("Length:"),False,True,0)
        self.duration = gtk.Entry()
        self.duration.set_width_chars(10)
        self.duration.set_editable(False)
        hbox.pack_start(self.duration, True,True,0)
        hbox.pack_start(gtk.Label("Flags:"),False,True,0)
        self.flags = gtk.Entry()
        self.flags.set_width_chars(6)
        self.flags.set_editable(False)
        hbox.pack_start(self.flags, True,True,0)
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
        path = self.ask_open_path()
        if not path: return
        try:
            wavin = wave.open(path, 'rb')
        except Exception, e:
            self.error_message("Couldn't read '%s': %s"%(path,repr(e)))
            return
        if wavin.getnchannels() != 1:
            self.error_message("Only monaural (1 channel) is supported.")
            return
        if wavin.getcomptype() != 'NONE':
            self.error_message("Sound must be uncompressed. Compression  is %s"%(
                wavin.getcompname()))
            return
        if not wavin.getsampwidth() in [1,2]:
            self.error_message("Only 8 or 16 bit WAV is supported.")
            return
        pstr = self.s_lsint8 if wavin.getsampwidth() ==1 else self.s_lsint16
        self.sound.set_rate(wavin.getframerate())
        newsamples = []
        data = bytearray(wavin.readframes(wavin.getnframes()))
        i = 0
        while i < len(data):
            newsamples.append(pstr.unpack(data[i:i+pstr.size])[0])
            i += pstr.size
            
        self.sound.set_samples(newsamples)
        self.update()
        self.set_unsaved()
    def file_export(self,*argv):
        path = self.ask_save_path(default = "Asnd%04X.wav"%self.res.resid)
        if not path: return
        if not path.endswith(".wav"): path += ".wav"
        try:
            self.wave_out(open(path, 'wb'))
        except Exception, e:
            self.error_message("Couldn't write '%s': %s"%(path,repr(e)))
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
        self.res.set_data(self.sound.get_data())
        self.set_saved()
    def play_sound(self, *argv):
        self.temp = tempfile.NamedTemporaryFile('wb')
        self.wave_out(self.temp)
        command = self.play_command.get_text()
        self.temp.flush()
        subprocess.Popen(command%self.temp.name, shell=True)
    def editor_setup(self):
        self.load()
    def update(self):
        self.sample_rate.set_text("%d Hz"%self.sound.get_rate())
        self.duration.set_text("0x%08X"%self.sound.duration)
        self.flags.set_text("0x%04X"%self.sound.flags)
    def load(self, *argv):
        self.rfile = self.res.as_file()
        self.set_title("Sound Editor - %04X"%self.res.resid)
        self.sound = delv.sound.Asnd(self.rfile)
        self.update()
        self.set_saved()
