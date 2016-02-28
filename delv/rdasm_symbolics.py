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
ASM_GLOBAL_NAME_HINTS = {
    0x00: "CurrentHour",
    0x01: "CurrentTime",
    0x02: "PlayerCharacter",
#    0x05: "gPlayerCharacter",
    0x09: "CurrentCharacter", 
    0x0A: "ConversationResponse",
    0x0C: "Karma",
    0x0D: "Registered",
    0x10: "CurrentZone",
}

ASM_OBJ_NAME_HINTS = {
   0x00: "Prop",
   0x10: "Unknown_10",
   0x20: "Unknown_20",
   0x40: "Character"
}

ASM_SYSCALL_NAMES = {
    'Delete':                 (0xA7),
    'Create':                 (0xA8),
    'Random':                 (0xAC),
    'New':                    (0xAD),
    'GetWeight':              (0xB8),
    'JoinParty':              (0xB9),
    'ChangeZone':             (0xBF),
    'SetFlag':                (0xC1),
    'ClearFlag':              (0xC2),
    'TestFlag':               (0xC4),
    'EmitSignal':             (0xC5),
    'PlayNote':               (0xD2),
    'PlaySound':              (0xD3),
    'PlaySound2':             (0xD7),
    'SetAmbientLighting':     (0xD8),
    'SetTitle':               (0xDA),
    'HasWindow':              (0xDB),
    'GetState':               (0xDC),
    'SetState':               (0xDD),
    'MagicAuraEffect':        (0xE1),
    'ShootEffect':            (0xE2),
    'AddQuest':               (0xF2),
    'AddConversationKeyword': (0xF4),
    'GetSkill':               (0xF5),
}

ASM_STRUCT_HINTS = {
    'flags': 0,
    'x': 1, 'y': 2, 'aspect': 3, 
    'prop_type': 4, 'aspect_and_proptype': 5,
    'd1': 6, 'd2': 7, 'd3': 8,
    'unkn09': 9,

    'magic': 0x1E, 
    'talk_balloon': 0x26,
    'nutrition': 0x28,
}


ASM_OBJECT_HINTS = {
   '__init__':   0x0000,
   'Look':       0x0002,
   'LookAtRoom': 0x0007,
   'Examine':    0x0008,
   'Use':        0x0009,
   'UseOn':      0x000A,
   'UseAt':      0x000B,
   'Talk':       0x000C,
   'Wear':       0x000D,
   'UnWear':     0x000E,
   'CanUnwear':  0x0010,
   'Beheld':     0x0014,
   'EveryTurn':  0x0020,
   'AskedAbout': 0x0033,
   'Dug':        0x0039
}
DASM_OBJECT_HINTS = {v:k for k,v in ASM_OBJECT_HINTS.items()}


