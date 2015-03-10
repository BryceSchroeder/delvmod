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
import graphics, sound, store, level, script
GRAPHICS_LANDSCAPE = 131
GRAPHICS_PORTRAIT = 135
GRAPHICS_TILESHEET = 141
_OBJECT_SI_HINTS = {
   127: level.Map,
   128: level.PropList,
   131: graphics.Landscape, 
   135: graphics.Portrait,
   137: graphics.SkillIcon,
   141: graphics.TileSheet,
   142: graphics.General,
   144: sound.Asnd,
   15: script.ClassContainer,
   16: script.ClassContainer,
   17: script.ClassContainer,
   18: script.ClassContainer,
}
for n in xrange(15,30): 
    if not n in _OBJECT_SI_HINTS:
        _OBJECT_SI_HINTS[n] = script.ClassContainer
for n in xrange(0x7E): 
    if not n in _OBJECT_SI_HINTS:
        _OBJECT_SI_HINTS[n] = script.Script

_OBJECT_SI_HINTS[n] = store.Store

_OBJECT_RESID_HINTS = {
  0xF004: store.TileNameList,
  0xF000: store.PropTileList,
  0xF010: store.TileFauxPropsList,
  0xF011: store.ByteList,
  0xF012: store.ByteList,
  0xF002: store.TileAttributesList, 
  0xF013: store.TileCompositionList,
  0x0201: script.CharacterNames,
  0x8EFF: graphics.General,
}
def class_by_resid(resid):
    """Try to get a class that can handle the resource provided,
       otherwise return None"""
    return _OBJECT_RESID_HINTS.get(resid,
           _OBJECT_SI_HINTS.get((resid >> 8) - 1, None))
    


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

 0x0410: "Attack Nearest",
 0x0411: "Attack Weakest",
 0x0413: "Defend",
 0x0414: "Berserk",
 0x0415: "Missile Script",
 0x0A00: "Sustenance Potion",
 0x0A01: "Healing Potion",
 0x0A02: "Mage's Friend Potion",
 0x0A03: "Free Motion Potion",
 0x0A04: "Antidote Potion",
 0x0A05: "Clear Mind Potion",
 0x0A06: "Smith's Friend Potion",
 0x0A07: "Far Sight Potion",
 0xF008: "Monster Statistics",
 0xF000: "Prop-Tile Associations",
 0xF004: "Tile Names",
 0xF002: "Tile Attributes",
 0xF013: "Composed Tiles",
 0xF010: "Faux Prop Information",
 0xF011: "Prop-aspect X offsets",
 0xF012: "Prop-aspect Y offsets",
 0xF015: "Peristence Store Symbols"
}
_SCEN_HINTS = {
    1: "String Lists",2: "Static Data",3: "AI Scripts",4: "Script Data",
    7: "Shared Dialogue Scripts",
    8: "Scripts", 9: "Potion Scripts", 10: "Scripts", 11: "Scripts", 
    12: "Scripts",
    13: "Game Mechanics Scripts", 14: "Scripts", 
    16: "Object Scripts", 19: "Zone Scripts",
    15: "Object Scripts",17:"Object Scripts",18:"Object Scripts",
    20: "Composite Zone Scripts", 
    23: "Character Scripts", 25: "Skill and Action Scripts", 
    26: "Area Scripts", 27: "Area Scripts", 47: "Character Action Scripts",
    127: "Maps", 128: "Prop Lists", 131: "Landscape Graphics", 
    135: "Character Portraits", 137: "Skill Icons", 141: "Tile Graphics",
    142: "General Graphics", 143: "Music", 144: "Sounds", 
    239: "Script Data", 254: "Patch Description",
    187: "Metadata from delv",
    129: "Explored Area Bitmaps", 223: "Journal Entries"
}

