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

import pygame
import pygame.midi
pygame.init()
pygame.midi.init()

PORT = 6# pygame.midi.get_default_output_id()

USAGE = '''
CURRENTLY NOT IMPLEMENTED.
Music turned out to be much more complicated than expected.
This will probably not be finished soon.

Usage: ./music.py archive resid 
Or:    ./music.py file 

Plays Delver music resources (90xx) using your computer's MIDI facilities.
If it doesn't work, try picking a different output device. Sometimes the
default is not right.

Requires pygame.
Using delv Version: %s
'''%delv.version


if len(sys.argv)<2:
    print >> sys.stderr, USAGE
    sys.exit(-1)

source = open(sys.argv[1],'rb')

if len(sys.argv)<3: # individual file
    data = source.read()
    music = delv.sound.Music(data)
else: # archive
    resource = delv.archive.Scenario(source).get(int(sys.argv[2],16))
    if not resource:
        print >> sys.stderr, "No resource", sys.argv[2], "found in that archive."
        sys.exit(-1)
    music = delv.sound.Music(resource.get_data())

print "Using port", PORT, pygame.midi.get_device_info(PORT)
output = pygame.midi.Output(PORT,0)
print "Instruments"
for part,instrument in music.part().items():
    print part, instrument
    if instrument < 128:
        print "\t",delv.sound.INSTRUMENT_NAMES[instrument]
music.setup_pygame_midi_output(output)



output.write(music.get_midi())
del output
pygame.midi.quit()
