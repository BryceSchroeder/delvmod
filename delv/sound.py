#!/usr/bin/env python
# Copyright 2014-2015 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
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
# Maps and prop lists. Convenience utilities for map visualization.
import util
from util import bitstruct_pack, bits_pack,bits_of

class SoundError(Exception): pass

class Sound(object):
    pass

class Asnd(Sound):
    def __init__(self, src=None):
        self.samples = []
        self.rate = 22050
        self.flags =0 
        if src and issubclass(src.__class__, util.BinaryHandler):
            self.src = src
        elif src:
            self.src = util.BinaryHandler(src)
        else: return
        self.load_from_file()
    def load_from_file(self):
        self.src.seek(0)
        if self.src.read(4) != 'asnd': raise SoundError, "Bad magic number"
        self.flags = self.src.read_uint32()
        self.rate = self.src.read_uint16()
        self.flags2 = self.src.read_uint16()
        # decode pcm
        samp = 0
        while not self.src.eof():
            #samp += self.src.read_sint16()
            #self.samples.append(samp) 
            self.samples.append(self.src.read_sint16()<<8)
    def get_rate(self):
        return self.rate
    def get_samples(self):
        return self.samples
    
class SoundSND(Sound):
    pass


class MusicError(Exception): pass

MUSIC_COMPONENT_TYPE = 'musi'
SOFT_SYNTH_COMPONENT_SUBTYPE = 'ss  '
GM_SYNTH_COMPONENT_SUBTYPE = 'gm  '
NOTE_REQUEST = 1
PART_KEY = 4
MIDI_CHANNEL = 8
USED_NOTES = 11
GENERAL_EVENT = 0xF
INSTRUMENT_NAMES = """Acoustic Grand Piano
Bright Acoustic Piano 
Electric Grand Piano
Honky-tonk Piano 
Electric Piano 1 
Electric Piano 2 
Harpsichord 
Clavi 
Celesta 
Glockenspiel 
Music Box 
Vibraphone 
Marimba 
Xylophone 
Tubular Bells 
Dulcimer 
Drawbar Organ 
Percussive Organ 
Rock Organ 
Church Organ 
Reed Organ 
Accordion 
Harmonica 
Tango Accordion 
Acoustic Guitar (nylon) 
Acoustic Guitar (steel) 
Electric Guitar (jazz) 
Electric Guitar (clean) 
Electric Guitar (muted) 
Overdriven Guitar 
Distortion Guitar 
Guitar harmonics 
Acoustic Bass 
Electric Bass (finger) 
Electric Bass (pick) 
Fretless Bass 
Slap Bass 1 
Slap Bass 2 
Synth Bass 1 
Synth Bass 2 
Violin 
Viola
Cello 
Contrabass 
Tremolo Strings 
Pizzicato Strings 
Orchestral Harp 
Timpani 
String Ensemble 1 
String Ensemble 2 
SynthStrings 1 
SynthStrings 2 
Choir Aahs 
Voice Oohs 
Synth Voice 
Orchestra Hit 
Trumpet 
Trombone 
Tuba 
Muted Trumpet 
French Horn 
Brass Section 
SynthBrass 1 
SynthBrass 2 
Soprano Sax
Alto Sax 
Tenor Sax 
Baritone Sax 
Oboe 
English Horn
Bassoon 
Clarinet 
Piccolo
Flute 
Recorder 
Pan Flute
Blown Bottle
Shakuhachi 
Whistle 
Ocarina 
Lead 1 (square) 
Lead 2 (sawtooth)
Lead 3 (calliope) 
Lead 4 (chiff) 
Lead 5 (charang) 
Lead 6 (voice) 
Lead 7 (fifths) 
Lead 8 (bass + lead)
Pad 1 (new age)
Pad 2 (warm) 
Pad 3 (polysynth)
Pad 4 (choir) 
Pad 5 (bowed) 
Pad 6 (metallic) 
Pad 7 (halo) 
Pad 8 (sweep) 
FX 1 (rain) 
FX 2 (soundtrack) 
FX 3 (crystal) 
FX 4 (atmosphere) 
FX 5 (brightness) 
FX 6 (goblins) 
FX 7 (echoes) 
FX 8 (sci-fi) 
Sitar 
Banjo 
Shamisen 
Koto 
Kalimba 
Bag pipe 
Fiddle 
Shanai 
Tinkle Bell 
Agogo 
Steel Drums 
Woodblock 
Taiko Drum 
Melodic Tom 
Synth Drum 
Reverse Cymbal 
Guitar Fret Noise 
Breath Noise 
Seashore 
Bird Tweet 
Telephone Ring 
Helicopter 
Applause 
Gunshot""".strip().split('\n')

class Music(Sound):
    SxCD = 1
    TxCD = 0
    def __init__(self, src=None):
        self.parts = {}
        self.qtma_commands = []
        self.midi_commands = []
        self.flags = [0,1,1] # no idea what these do, if anything
        if src: self.load_from_file(src)

    def load_from_file(self, src):
        self.src = util.BinaryHandler(src)
        body_offset = self.src.read_uint32()
        musi = self.src.read(4)
        if musi != MUSIC_COMPONENT_TYPE: 
            raise ValueError, "%s is not a music resource"%src
        self.flags = [self.src.read_uint32() for _ in xrange(3)]
 
        while self.src.tell() < body_offset:
            command = self.src.readb(4)
            operation = bits_of(command, 4, 0)
            if operation == GENERAL_EVENT:
                part = bits_of(command, 12, 4)
                event_length = bits_of(command, 16, 16)
                data_len = (event_length-2)*4
                data_offs = self.src.tell()
                self.src.seek(data_offs+data_len)
                footer = self.src.readb(4)
                subtype = bits_of(footer, 14, 2)
                event_length2 = bits_of(footer, 16,16)
                if event_length != event_length2:
                    raise MusicError, "Failed QTMA validity check."
                #print "General", part, event_length, subtype
                if subtype == MIDI_CHANNEL or subtype == USED_NOTES:
                    continue # we don't care
                elif subtype == NOTE_REQUEST:
                    next_op = self.src.tell()
                    self.src.seek(data_offs)
                    nrflags = self.src.read_uint8()
                    reserved = self.src.read_uint8()
                    polyphony = self.src.read_uint16()
                    typical = self.src.read_fixed16()
                    _align = self.src.read_uint16()
                    synthesizer_type = self.src.read(4)
                    synthesizer_name = self.src.read_str31()
                    instrument_name = self.src.read_str31()
                    instrument_number = self.src.read_uint32()
                    gm_number = self.src.read_uint32()
                    #print "\tNote request", nrflags, reserved,polyphony,
                    #print typical,repr(synthesizer_type),synthesizer_name,
                    #print instrument_name,instrument_number,gm_number
                    self.parts[part] = gm_number
                    self.src.seek(next_op)
                else:
                    raise MusicError, "Unknown QTMA general subtype %d"%subtype
            elif operation == 0x6: # End (marker event)
                #print "End    ", self.src.tell()
                break
            else:
                raise MusicError, "Unrecognized op, 0x%X@%d"%(
                    operation, self.src.tell()-4)
        self.src.seek(body_offset)
        self.load_qtma()
    def setup_pygame_midi_output(self, output):
        "Set up the MIDI output to play this music."
        for partnumber,instrument in self.parts.items():
            if instrument > 0x80: instrument &= 0x7F 
            output.set_instrument(instrument,partnumber)
    def load_qtma(self):
        # Load the body commands
        while not self.src.eof():
            command = self.src.readb(4)
            if   bits_of(command, 3, 0) == 1: # note event
                part = bits_of(command, 5, 3)
                pitch = bits_of(command, 6,8) + 32
                velocity = bits_of(command, 7, 14)
                duration = bits_of(command, 11,21)
                print "note", part, pitch,velocity,duration
            #elif bits_of(command, 4, 0) == 9: # extended note
            #    tail = self.src.readb(4)
            #    print "enote"
            elif bits_of(command, 3, 0) == 0: # rest 
                duration = bits_of(command, 24, 8)
                print "rest", duration
            elif bits_of(command, 4, 0) == 0xF: # general
                event_length = bits_of(command, 16, 16)
                data_len = (event_length-2)*4
                self.src.seek(data_len,1)
            #else:
            #    print "Unknown",("%02X "*4)%tuple(command), self.src.tell()


        
    def part(self,partnumber=None):
        """Return the general midi instrument associated with a part number."""
        return self.parts if partnumber is None else self.parts[partnumber]
    def set_midi(self, new):
        self.midi_commands = new
        self.qtma_commands = []
    def set_qtma(self, new):
        self.qtma_commands = new
        self.midi_commands = []
    def get_midi(self):
        "Return list of MIDI commands - in the format pygame.midi.write wants."
        if not self.midi_commands: self.convert_to_midi()
        return self.midi_commands
    def get_qtma(self):
        """Return list of QTMA commands."""
        if not self.qtma_commands: self.convert_to_qtma()
        return self.qtma_commands
    # private methods
    def convert_to_midi(self):
        pass
    def convert_to_qtma(self):
        pass
