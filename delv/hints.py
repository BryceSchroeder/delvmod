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

_RES_HINTS = {
 0x0101: "Global Symbol List",

 0x0201: "Character Names",
 0x0203: "Character Class Names",
 0x0204: "Character Class Descriptions",
 0x0205: "Character Class Stats",
 0x0206: "Character Class Skills",
 0x0218: "Sign Text",
 0x0219: "Scroll Text",
 0x021A: "Quest Text",
 0x021B: "Book Item Text",
 0x021D: "Bookshelf Text",
 0x021F: "Ring Inscriptions",
 0x0220: "Gravestone Inscriptions",
 0x0241: "Death Text",
 0x0242: "Defeat Text",
 0x0243: "Victory Text",

# 0x0410: "Attack Nearest",
# 0x0411: "Attack Weakest",
# 0x0413: "Defend",
# 0x0414: "Berserk",
# 0x0415: "Missile Script"
 0xF008: "Monster Statistics",
 0xF004: "Tile Names",
 0xF002: "Tile Attributes",
 0xF015: "Peristence Store Symbols"
}
_SCEN_HINTS = {
    1: "String Lists",2: "Static Data",3: "AI Scripts",4: "Script Data",
    7: "Shared Dialogue Scripts",
    8: "Scripts", 9: "Scripts", 10: "Scripts", 11: "Scripts", 12: "Scripts",
    13: "Scripts", 14: "Scripts", 16: "Object Scripts", 19: "Zone Scripts",
    15: "Dialogue Scripts", 20: "Composite Zone Scripts", 
    23: "Dialogue Scripts", 25: "Skill and Action Scripts", 
    26: "Area Scripts", 27: "Area Scripts", 47: "Character Action Scripts",
    127: "Maps", 128: "Prop Lists", 131: "Landscape Graphics", 
    135: "Character Portraits", 137: "Skill Icons", 141: "Tile Graphics",
    142: "General Graphics", 143: "Music", 144: "Sounds", 
    239: "Script Data", 254: "Patch Description",
    129: "Explored Area Bitmaps", 223: "Journal Entries"
}

