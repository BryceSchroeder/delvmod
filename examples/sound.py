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

from __future__ import absolute_import, division, print_function, unicode_literals

import delv
import delv.archive
import delv.sound
import sys
import wave
import struct

USAGE = '''
Usage: ./sound.py archive resid out.wav 
Or:    ./sound.py file out.wav

Converts Delver sound resources (91xx) to .wav.
Using delv Version: %s
'''%delv.version


if len(sys.argv)<3:
    print(USAGE, file=sys.stderr)
    sys.exit(-1)

source = open(sys.argv[1],'rb')

if len(sys.argv)<4: # individual file
    data = source.read()
    sound = delv.sound.Asnd(data)
else: # archive
    resource = delv.archive.Scenario(source).get(int(sys.argv[2],16))
    if not resource:
        print("No resource", sys.argv[2],"found in that archive.", file=sys.stderr)
        sys.exit(-1)
    sound = delv.sound.Asnd(resource.get_data())

outfile = wave.open(sys.argv[-1], 'wb')
outfile.setnchannels(1)
outfile.setsampwidth(2)
outfile.setframerate(sound.get_rate())

# wave integers are backward, i.e. little-endian
lsint16 = struct.Struct('<h')

frames = bytearray()
for sample in sound.get_samples():
    frames += lsint16.pack(sample)


outfile.writeframes(frames)

outfile.close()



