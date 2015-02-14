# delvmod
A Python module and demonstration programs for modding a classic computer RPG


INSTALLING / USING

python setup.py install

(You will need to run it as root, e.g. "sudo python setup.py install". You can
also use "python setup.py develop" if you anticipate modifying the program.)

WHAT IS delv FOR?

delv is a Python module that allows users to manipulate the archives of games
based on the "Delver" engine, written 1995-1999 by Glenn Andreas. It was only
used, as far as is known, in the 1999 game "Cythera," published by Ambrosia
Software, inc. ("Cythera" and "Delver" are trademarks of Ambrosia Software inc 
or Glenn Andreas.)

Extensive technical documentation of this engine and game, which were used to
produce delv, can be found at http://www.ferazelhosting.net/wiki/Cythera

The wiki page for delv itself is http://www.ferazelhosting.net/wiki/delv


WHO WROTE delv AND HOW?

delv was originally written by Bryce Schroeder, bryce.schroeder@gmail.com

Website: http://www.bryce.pw

Prior work by various persons over the years and various technical information
published by the author of the engine have been used in the Technical 
Documentation Project supporting delv, but mainly the game has been documented
through meticulous black-box reverse engineering. For example, the graphics
format was successfully interpreted through systematic "mutation experiments"
on the graphics resources. (The notes run to about 40 pages of screenshots and
comments.) In other cases, simple observation has sufficed; for example, the
essentials of the Delver Archive format are almost immediately evident by 
inspection with a hex editor.

Cythera's license agreement does not appear to purport to forbid reverse 
engineering, and if it did, reverse engineering for interoperability is 
allowed in the United States and many other countries in any case. (delv is 
based heavily on the facilities offered by modern dynamic programming languages
and probably would not benefit much from the specific, highly optmized 
techniques of implementation that are likely used in Delver anyway.)


WHAT IS THE PURPOSE OF delv?

Self-evidently, you could use it to make a third-party RPG editor suite that is
interoperable with a Delver engine based game like Cythera. Another application
would, e.g. be map viewers or dynamic walkthrough/guide websites for the game.

Several examples and utilties are provided to showcase the usage of delv.


WHAT CAN I DO WITH delv?

Anything permitted by the GPL version 3, but we ask you to please not attempt 
to use it to circumvent Cythera's shareware restrictions, and not to distribute
any modified versions of "Cythera Data" (i.e. the scenario file). This latter 
action at least would violate Ambrosia Software's copyright (and the Cythera 
EULA, as it permits only redistribution of the unmodified and complete game.)


HOW IS delv DOCUMENTED?

Most of the classes and methods have docstrings. An overview is presented here:

delv.archive - Reads and writes Delver Archives (e.g. "Cythera Data")

delv.colormap - Contains the palette of indexed colors used by Cythera. You 
may need to access this if you are undertaking to display graphics.

delv.graphics - Handles the Delver Engine's custom compressed graphics format,
and also the uncompressed icon graphics.

delv.monster - Handles the special monster stats resource. (Note that in the
course of the game, the scripting system would normally access this itself
and interpret it without any special help; this module is provided for the 
convenience of editors. How monsters defined is, in principle, scenario
dependent.)

delv.script - Assembles, disassembles, and (in principle) executes scripts,
 including virtual machine scripts and AI-type scripts.

delv.sound - Handles sound and music resources.

delv.store - Utility functions for editing various kinds of binary storage
formats used by Delver, such as symbol lists and serialized scripting system
objects.

delv.tile - Handles graphical tiles and their renderer / engine properties 
(movement obstruction, vision blocking, light source specifications, etc.)

delv.util - Utilities for other delv modules, but you can use the public 
functions and classes if you like. 


GETTING AT SOUNDS AND GRAPHICS

Multimedia formats are provided in reasonably universal formats, e.g. arrays;
you will probably have to write glue code if you want to display them as PNG,
use them with pygame, or whatever. delv couldn't practically support all the
different ways of getting multimedia to the output device using python, and it
would introduce huge testing complexity and lots of dependencies for something
that is intended to also make simple command line tools and maybe even run in
a browser-based python implementation someday. Sorry about that.


EXAMPLE PROGRAMS

delv comes with some examples. Probably, it'll come with more someday. You 
will need to install delv (python setup.py install) before they will work.
All of them are, unsurprisingly, in the examples/ directory.

"archive\_example.py" - Shows how one can load, modify, and save archives.

"dcg\_encoder.py" - Saves .png images (n.b. with correct color maps) to
the Delver Compressed Graphics format. Requires  the Python Imaging Library.

"dcg\_view.py" - Simple viewer for Delver Compressed Graphics. It can view
them in archives or as single files, and save them to PNG. Requires the
Python Imaging Library.

"delvpack.py" - This just converts Delver Archives back and forth between
archive files and unpacked directories. First arguement is source, second is 
destination, it'll figure out what needs to happen. Very simple.

"icon\_view.py" - Views uncompressed icons (Resources 8Axx / subindex 137.)

"mag.py" - Command-line tool for creating and applying patches. (It can apply
patches created for the first-party patch manager Magpie, and create patches
that it can apply, but it can't create patches that can be applied by Magpie.)

"tileshow.py" - Shows tiles from their tile ID (i.e. the ID used in maps.)

FUTURE DIRECTIONS

As of the present, the scripting system's virtual machine has not been 
successfully reverse engineered and documented by the Technical Documentation 
Project. Therefore, the delv.script module remains unfinished and will likely 
remain so for some time. 

It would be nice if someone made a GUI patch manager (see the example mag.py
for how to implement patches with delv; delv has all of the actual patching
and even conflict-detection logic built in, it's just a matter of keeping
track of what patches are applied, etc.) 
