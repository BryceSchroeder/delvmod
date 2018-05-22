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

import delv
import delv.archive
import delv.sound
import sys

import midiutil

USAGE = '''
NOT FULLY IMPLEMENTED.

Usage: ./midi.py archive resid 
Or:    ./midi.py file 

Converts a Delver music resource (QTMA) to standard MIDI (SMF)

Requires midiutil.
Using delv Version: %s
'''%delv.version



if len(sys.argv)<2:
    print >> sys.stderr, USAGE
    sys.exit(-1)

source = open(sys.argv[1],'rb')

if len(sys.argv)<3: # individual file
    data = source.read()
    musi = delv.sound.Music(data)
else: # archive
    resource = delv.archive.Scenario(source).get(int(sys.argv[2],16))
    if not resource:
        print >> sys.stderr, "No resource", sys.argv[2], "found in that archive."
        sys.exit(-1)
    musi = delv.sound.Music(resource.get_data())

# Setup midi file
midi = midiutil.MIDIFile(len(list(musi.parts)), file_format=1) # tracks equal to number of original parts; format=1 adds tempo track at 0
# May need to add an empty track if error occurs (like with 9005, Danger track), probably an error with the lib but unimportant

# Tempo
tempo_track = 0 # Tempo track always added as extra track at 0 in this format
midi.addTempo(tempo_track, 0, 120)

# Channels
parts = list(musi.channels) # parts are 0-indexed, but with tempo track, must add offset
time = 0
for part in parts: # Setting instrument programs
    midi.addProgramChange(part,musi.channels[part]-1,time,program=(musi.parts[part]-1)%127) # mod 127 used to ensure valid program nums (doesn't matter when channel 10 anyways)

# Notes, Extended Notes, and Rests
for com in musi.qtma_commands:
    if com[0] == 'rest':
        time += com[4]/300.0 # 300 is the default length of a quarter note (1 beat) in QTMA, so we use that here to scale to the tempo (MIDI goes by beats, not QTMA intervals)
    else:
        midi.addNote(com[1],channel=musi.channels[com[1]]-1,pitch=com[2],time=time,duration=com[4]/300.0,volume=com[3])


# Write the resulting midi file
with open(sys.argv[1]+'.midi','wb') as output_file:
    midi.writeFile(output_file)
