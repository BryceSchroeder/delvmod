#!/usr/bin/env python
# Delver Archive patcher / unpatcher for the Host System. Should be a useful
# example of how to use delv.archive.Patch
#
# Copyright 2015 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
# Wiki: http://www.ferazelhosting.net/wiki/mag.py
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


MAGPY_HELP = """
mag.py [COMMAND [arguments...]]
Program for creating and using Delver Archive patches.
Any "FILE" mentioned below can also be a directory.

Available Commands:
  patch BASE-FILE PATCH-FILE1 [... PATCH-FILEN] RESULT-FILE
     Apply a patch named PATCH-FILE to BASE-FILE, and
    save the result to RESULT-FILE. Note that BASE-FILE is not modified.
  diff BASE-FILE NEW-FILE RESULT-FILE [INFO-FILE]
     Create a patch that will modify BASE-FILE to be the same as NEW-FILE
    when it is applied, saving the new patch in RESULT-FILE. If INFO-FILE
    is supplied, it stores that in the new patch.
  info PATCH-FILE
     Print the description of the patch from its patch resource (0xFFFF)
  compatible PATCH1 PATCH2 [... PATCHN]
     Report if the listed patches are compatible, i.e. if they overwrite
    none of the same resources (0xFFFF excepted.)
  
If no command is given, mag.py with launch in GUI mode, if available.

Note that the patches mag.py creates are not compatible with Magpie. mag.py
is however compatible with Magpie patches and can apply them. Also note that
unlike Magpie, mag.py is not a patch manager; it only creates and applies 
patches. It can't unapply them.

"""
import delv

DEFAULT_INFO = "Created with mag.py, http://www.ferazelhosting.net/wiki/mag.py"
SIGNATURE = "Made with delv %s"%delv.version

import delv.archive
from sys import argv,exit,stderr
import os
import textwrap
import itertools

if len(argv) < 2:
    # GUI mode
    print >> stderr, "GUI not implemented yet; use CLI mode"
    print >> stderr, MAGPY_HELP
    exit(-1)
command = argv[1]
if command == 'info':
    patcharch = delv.archive.Patch(argv[2])
    print " ----- PATCH INFO FOR '%s' ----- "%os.path.basename(argv[2])
    pinfo = patcharch.get_patch_info()
    if not pinfo:
        print "This doesn't appear to contain a patch resource (0xFFFF);"
        print "It's probably not a patch."
    else: # Print it out nicely formatted to the terminal width
        print textwrap.fill(str(pinfo),79)
elif command == 'compatible':
    combos = itertools.combinations(
        [(delv.archive.Patch(path),
              os.path.basename(path)) for path in argv[2:]], 2)
    conflicts = False
    for (a,aname),(b,bname) in combos:
        if not a.compatible(b): 
            print aname, "conflicts with", bname
            conflicts = True
            break
    if conflicts:
        print "This combination of patches may result in undefined behavior."
        exit(-3)
    else:
        print "This combination of patches seems to be compatible."
        print "(Of course, this is not certain to be the case.)"
        exit(0)
elif command == 'diff':
    info = open(argv[5]).read() if len(argv)>5 else DEFAULT_INFO
    newpatch = delv.archive.Patch()
    newpatch.patch_info(info)
    destination = argv[4]
    base = delv.archive.Scenario(argv[2])
    newversion = delv.archive.Scenario(argv[3])
    newpatch.diff(base, newversion)
    print "New patch will modify %d resources."%len(newpatch.resources())
    newpatch.to_path(destination)
elif command == 'patch':
    base = delv.archive.Scenario(argv[2])
    patches = [delv.archive.Patch(path) for path in argv[3:-1]]
    destination = argv[-1]
    for patch in patches:
        patch.patch(base)
    print "Applied."
    base.to_path(destination)
else:
    print >> stderr, "Unrecognized command", command
    print >> stderr, MAGPY_HELP
    exit(-2)
