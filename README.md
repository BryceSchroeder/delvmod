# delvmod
A Python module and demonstration programs for modding a classic computer RPG

WHAT IS delv FOR?
delv is a Python module that allows users to manipulate the archives of games
based on the "Delver" engine, written 1995-1999 by Glenn Andreas. It was only
used, as far as is known, in the 1999 game "Cythera," published by Ambrosia
Software, inc. 

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
comments.) In other cases, simple observation has sufficed, for example, the
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

WHAT CAN I DO WITH delv?
Anything permitted by the GPL version 3, but we ask you to please not attempt to
use it to circumvent Cythera's shareware restrictions, and not to distribute any
modified versions of "Cythera Data" (i.e. the scenario file). This latter action
at least would violate Ambrosia Software's copyright (and the Cythera EULA, as
it permits only redistribution of the unmodified and complete game.)

HOW IS delv DOCUMENTED?
Most of the classes and methods have docstrings. An overview is presented below:
