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
import util, archive, store
from util import bitstruct_pack, bits_pack,bits_of
import array
import cStringIO as StringIO
import binascii

class SoundError(Exception): pass

class Sound(store.Store):
    pass

class Asnd(Sound):
    """Class for Delver sound resources. (Might be 'asnd' for "Ambrosia 
       Sound Tool" but that's speculative.)"""
    def __init__(self, src=None):
        self.samples = array.array('h')
        self.rate = 22050
        self.duration =0 
        self.data = None
        store.Store.__init__(self, src)
        self.set_source(src)
        if self.src: self.load_from_bfile()
        
    def write_to_bfile(self, dest=None):
        if dest is None: dest = self.src
        dest.seek(0)
        dest.write('asnd')
        dest.write_uint32(self.duration)
        dest.write_uint16(self.rate)
        dest.write_uint16(self.flags)
        for sample in self.samples:
            # Yes, this seems stupid, but it's the way it is
            # No idea why 8 bit sound is stored in 16 bit shorts.
            dest.write_sint16(sample>>8)
        
    def load_from_bfile(self):
        self.src.seek(0)
        if self.src.read(4) != 'asnd': raise SoundError, "Bad magic number"
        self.duration = self.src.read_uint32()
        self.rate = self.src.read_uint16()
        self.flags = self.src.read_uint16()
        # decode pcm
        samp = 0
        while not self.src.eof():
            #samp += self.src.read_sint16()
            #self.samples.append(samp) 
            self.samples.append(self.src.read_sint16()<<8)
        self.data = None
    def get_rate(self):
        return self.rate
    def get_samples(self):
        "Get an array of 16-bit signed integers."
        return self.samples
    def set_samples(self, newsamples):
        self.samples = array.array('h',newsamples)
        self.data = None
        # It's actually size, not duration... anyway, may need to pad.
        
        if len(self.samples) < 512:
            self.samples.extend([0]*(512-len(self.samples)))
            self.duration = 0
        else:
            self.samples.extend([0]*(1024 - len(self.samples)%1024))
            self.duration = (len(self.samples)-512)/1024
    def set_rate(self, newrate):
        self.rate = newrate
        self.data = None
        
    
class SoundSND(Sound):
    pass


class MusicError(Exception): pass

# Primary command types
# type.3 : 3 bit part types
T3_REST = 0 # 4 byte len
T3_NOTE = 1 # 4 byte len
T3_CONTROL = 2 # 4 byte len
T3_MARKER = 3 # 4 byte len
# type.4 : 4 bit part types
T4_ENOTE = 9 # 8 byte len
T4_ECONTROL = 10 # 8 byte len
T4_GENERAL = 15 # variable len
# Subtype command types
# T3_CONTROL event controllers
CON_MOD = 1 # kControllerModulationWheel
CON_VOL = 7 # kControllerVolume
CON_PAN = 10 # kControllerPan, more commonly used than kControllerBalance for handling L/R balance
CON_PITCH = 32 # kControllerPitchBend
CON_PRESS = 33 # kControllerAfterTouch or channel pressure
CON_SUSTAIN = 64 # kControllerSustain, positive for on, 0 for off (64 and 64 in midi, respectively)
CON_REVERB = 91 # kControllerReverb, 0-127 in midi
# T3_MARKER event subtypes
MARK_END = 0
MARK_BEAT = 1
MARK_TEMPO = 2
# T4_GENERAL event subtypes
GEN_NOTE_REQUEST = 1
GEN_PART_KEY = 4
GEN_TUNE_DIFF = 5
GEN_MIDI_CHANNEL = 8
GEN_USED_NOTES = 11
# Synth types
MUSIC_COMPONENT_TYPE = 'musi'
SOFT_SYNTH_COMPONENT_SUBTYPE = 'ss  '
GM_SYNTH_COMPONENT_SUBTYPE = 'gm  '
# GM instrument mapping
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
        self.instruments = {} # instruments used, maps directly to midi instruments
        self.channels = {} # channels, 10 is drums
        self.qtma_commands = []
        self.midi_commands = []
        self.flags = [0,1,1] # no idea what these do, if anything
        if src: self.load_from_file(src)

    def load_from_file(self, src):
        self.src = util.BinaryHandler(src)
        body_offset = self.src.read_uint32() # body_offset tells when the general commands stop and others begin; may not need it, just read through
        musi = self.src.read(4)
        if musi != MUSIC_COMPONENT_TYPE: 
            raise ValueError, "%s is not a music resource"%src
        self.flags = [self.src.read_uint32() for _ in xrange(3)]
 
        # while self.src.tell() < body_offset:
        while not self.src.eof():
            command = self.src.readb(4)
            t4 = bits_of(command, 4, 0)
            t3 = bits_of(command, 3, 0)
            if t4 == T4_GENERAL:
                part = bits_of(command, 12, 4)
                event_length = bits_of(command, 16, 16)
                data_len = (event_length-2)*4
                data_offs = self.src.tell()
                self.src.seek(data_offs+data_len)
                footer = self.src.readb(4)
                subtype = bits_of(footer, 14, 2)
                event_length2 = bits_of(footer, 16,16)
                if event_length != event_length2:
                    raise MusicError, "Failed QTMA validity check: General Event at ",self.src.tell()
                # pass data length validity check, move cursor to read data
                next_op = self.src.tell()
                self.src.seek(data_offs)
                if subtype == GEN_MIDI_CHANNEL: # Need to know if MIDI channel is 10 (percussion) since changes behavior
                    midi_channel = self.src.read_uint32()
                    self.channels[part] = midi_channel
                elif subtype == GEN_PART_KEY: # Detect key changes, not using
                    value = self.src.readb(next_op - data_offs - 4) # data chunk is everything from start to next op (-4 bytes of end of gen event)
                    # print "General: KEY CHANGE ", part, binascii.hexlify(value), self.src.tell()
                elif subtype == GEN_TUNE_DIFF: # sequence with tune difference, not using # TODO: maybe support tune diff?
                    # tune diffs appear to be tiny in Cythera, very little reason to include
                    # tuning even less widely supported than pitch bend, which varies greatly among synths itself
                    # given the lack of support, difficulty of using with the library, and seemingly tiny impact -- not using tune diffs now
                    value = self.src.readb(next_op - data_offs - 4)
                    # print "General: TUNE DIFF ", part, binascii.hexlify(value), self.src.tell()
                elif subtype == GEN_USED_NOTES: # Note used list is not necessary (probably used for QT pre-buffering), not using
                    value = self.src.readb(next_op - data_offs - 4)
                    # print "General: NOTES USED ", part, binascii.hexlify(value), self.src.tell()
                elif subtype == GEN_NOTE_REQUEST: # Set instrument number
                    nrflags = self.src.read_uint8() # control behavior if exact instrument not found in qt synth: either play best match or nothing
                    reserved = self.src.read_uint8() # unused
                    polyphony = self.src.read_uint16() # max voices for quicktime synth
                    typical = self.src.read_fixed16() # general num voices for volume control in qt synth
                    _align = self.src.read_uint16()
                    synthesizer_type = self.src.read(4) # all the next few are for instrument and synth type
                    synthesizer_name = self.src.read_str31()
                    instrument_name = self.src.read_str31()
                    instrument_number = self.src.read_uint32()
                    gm_number = self.src.read_uint32()
                    self.instruments[part] = gm_number # midi instrument num; really nothing else useful in midi, all qt synth controls
                else:
                    raise MusicError, "Unsupported General Event subtype %d for part %d at %d"%(subtype,part,self.src.tell())
                # Restore cursor for next op after processing general event and data
                self.src.seek(next_op)
            elif t4 == T4_ECONTROL: # Extended control, not needed for Cythera? not using
                tail = self.src.readb(4)
                part = bits_of(command, 12, 4)
                if bits_of(tail, 2, 0) != 2:
                    raise MusicError, "Failed QTMA validity check: Econtrol Event at ", self.src.tell()
                controller = bits_of(tail, 14, 2)
                value = bits_of(tail, 16, 16)
                # print "Extended Controller ", part, controller, value, self.src.tell()
            elif t4 == T4_ENOTE:
                tail = self.src.readb(4)
                part = bits_of(command, 12, 4)
                pitch = bits_of(command, 15, 17)
                if bits_of(tail, 2, 0) != 2:
                    raise MusicError, "Failed QTMA validity check: Enote Event at ", self.src.tell()
                velocity = bits_of(tail, 7, 3)
                duration = bits_of(tail, 22, 10)
                self.qtma_commands.append(["enote",part,pitch,velocity,duration])
            elif t3 == T3_MARKER: # Marker, not needed?  not using; can use rests/notes/enotes to increment time, no need for markers
                subtype = bits_of(command, 8, 8)
                value = bits_of(command, 16, 16)
                # if subtype == MARK_END:
                #     print "Marker: END " ,value, self.src.tell()
                # elif subtype == MARK_BEAT:
                #     print  "Marker: BEAT " ,value, self.src.tell()
                # elif subtype == MARK_TEMPO:
                #     print "Marker: TEMPO " ,value, self.src.tell()
                # else:
                #     print "Unsupported Marker Event subtype %d with value %d at %d"%(subtype,value,self.src.tell())
            elif t3 == T3_CONTROL:
                part = bits_of(command, 5, 3)
                controller = bits_of(command, 8, 8)
                value = bits_of(command, 16, 16)
                if controller == CON_MOD:
                    self.src.seek(self.src.tell()-2) # backup 2 bytes; easiest way to read fixed 16 bit float is with self.src functions
                    new_value = self.src.read_fixed16() # modulation value, and cursor moved back up to 2 bytes; modulations tiny in Cythera
                    self.qtma_commands.append(["mod",part,new_value,0,0])
                elif controller == CON_PAN:
                    new_value = (value - 256)/2 # scale from 256 - 512 to 0 - 127
                    if new_value > 127:
                        new_value = 127
                    self.qtma_commands.append(["pan",part,new_value,0,0])
                elif controller == CON_VOL: # global channel volume saved in 16.16 floating point
                    self.src.seek(self.src.tell()-2) # backup 2 bytes; easiest way to read fixed 16 bit float is with self.src functions
                    new_value = self.src.read_fixed16() # volume value, and cursor moved back up to 2 bytes
                    self.qtma_commands.append(["vol",part,new_value,0,0])
                elif controller == CON_PITCH: # QTMA uses 14-bit num for pitch bend, postive and negative fractional semitones, 7 bits each
                    # QTMA spec doesn't explain at all, and this is quite different than standard midi pitch bend
                    # HACK! Attempt to adjust value to expected output based on "Stairway" and Odemia tracks
                    # Center on 0; if upper 7 is 0, assume positive; if upper 7's are 1, assume negative and scale from positive value
                    # In actuality, there's undoubtedly a function mapping the binary representation through fractional semitones to the pitch bend
                    # TODO: Decode actual QTMA pitch bend value based on fractional semitones and replace hack
                    # An additional note - this isn't too serious since the pitch bends are tiny fractions of a semitone in Cythera
                    # Plus different synthesizers (including QT itself) will interpret differently over a wide range of full semitones
                    # So the hack is sufficiently close to sound identical on pretty much any synthesizer
                    MSB = bits_of(command,7,25) # MSB in last 7 bits like MIDI? 8th reserved in midi
                    LSB = bits_of(command,7,17) # LSB in upper 7? minus reserved one like in midi
                    if LSB != 0: # if non-zero, center and scale
                        new_value = (MSB - 127)*7.4 # rough approximation of actual mapping function
                    else:
                        new_value = MSB # just use positive value directly
                    self.qtma_commands.append(["pitch",part,int(new_value),0,0]) # ensure integer value
                elif controller == CON_PRESS: # After touch or channel pressure; stripped from QT 2.0 and some other synths; tiny in Cythera anyways
                    self.qtma_commands.append(["press",part,value,0,0])
                elif controller == CON_SUSTAIN: # Damper pedal / sustain; binary value
                    if value > 0: # any positive value is qtma for on
                        new_value = 64 # midi for on
                    else:
                        new_value = 63 # midi for off
                    self.qtma_commands.append(["sustain",part,new_value,0,0])
                elif controller == CON_REVERB: # Effects 1 / Reverb
                    new_value = bits_of(command,8,16) # qtma appears to only use the upper 8 bits of the value; not clear from docs
                    self.qtma_commands.append(['reverb',part,new_value,0,0])
                else:
                    raise MusicError, "Unsupported Controller Event controller type %d for part %d with value %d at %d"%(controller,part,value,self.src.tell())
            elif t3 == T3_NOTE:
                part = bits_of(command, 5, 3)
                pitch = bits_of(command, 6,8) + 32 # 32 bit offset in qtma
                velocity = bits_of(command, 7, 14)
                duration = bits_of(command, 11,21)
                self.qtma_commands.append(["note",part,pitch,velocity,duration])
            elif t3 == T3_REST:
                duration = bits_of(command, 24, 8)
                self.qtma_commands.append(["rest",0,0,0,duration])
            else:
                raise MusicError, "Unknown event %s at %d"%(binascii.hexlify(command),self.src.tell())
        # self.src.seek(body_offset)
        # Before handling QTMA events, must ensure coherence of tracks for MIDI formatting; MIDI count needs to be consecutive
        # Find the max track value, and make sure there are at least empty tracks to avoid track count errors with MIDI
        for i in range(max(list(self.instruments))):
            if i not in self.instruments:
                if i > 0:
                    self.instruments[i] = self.instruments[i-1] # If missing, fill in blank instrument with type next to it
                else:
                    self.instruments[i] = 1 # Default to standard piano
                self.channels[i] = 1 # Channel doesn't matter
        # self.load_qtma()


    def setup_pygame_midi_output(self, output):
        "Set up the MIDI output to play this music."
        for partnumber,instrument in self.instruments.items():
            if instrument > 0x80: instrument &= 0x7F 
            output.set_instrument(instrument,partnumber)
    def part(self,partnumber=None):
        """Return the general midi instrument associated with a part number."""
        return self.instruments if partnumber is None else self.instruments[partnumber]
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
