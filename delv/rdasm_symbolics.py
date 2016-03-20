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
ASM_GUI_NAME_HINTS = {
    0x04: 'Create',
    0x06: 'Text',
    0x08: 'Button',
    0x0F: 'Instrument',
    0x11: 'Spinner',
    0x14: 'TextBox',
}
DASM_GUI_NAME_HINTS = {v:k for k,v in ASM_GUI_NAME_HINTS.items()}
DASM_GUI_NAME_HINTS['_size'] = 1
DASM_GUI_NAME_HINTS['_name'] = 'GUI'



DASM_GLOBAL_NAME_HINTS = {
    0x00: "CurrentHour",
    0x01: "CurrentTime",
    0x02: "PlayerCharacterName",
    0x05: "PlayerCharacter", # Seems to have to be cast to character
    0x06: "CharactersInParty",
    0x07: "CharactersInParty2",
    0x09: "CurrentCharacter", 
    0x0A: "ConversationResponse",
    0x0C: "Karma",
    0x0D: "Registered",
    0x0E: "LanguagesKnown",
    0x0F: "GameDay",
    0x10: "CurrentZone",
    0x12: "StateTracker",
    0x13: "IsPlayerTurn",
}
ASM_GLOBAL_NAME_HINTS = {v:k for k,v in DASM_GLOBAL_NAME_HINTS.items()}
DASM_GLOBAL_NAME_HINTS['_size'] = 1
DASM_GLOBAL_NAME_HINTS['_name'] = 'Globals'

DASM_OBJ_NAME_HINTS = {
   0x00: "Prop",
#   0x10: "Unknown_10",
#   0x20: "Unknown_20",
   0x40: "Character",
   0x48: "Monster",
   0x50: "Skill",
}
ASM_OBJ_NAME_HINTS = {v:k for k,v in DASM_OBJ_NAME_HINTS.items()}
DASM_OBJ_NAME_HINTS['_size'] = 1
DASM_OBJ_NAME_HINTS['_name'] = 'Types'

ASM_SYSCALL_NAMES = {
    'RangeIterator':          (0xA0),
    'ArrayIterator':          (0xA1),
    'GameOver':               (0xA2), 
    #A3! A4! A5-
    'TalkParticipant':        (0xA4),

    'Delay':                  (0xA6), # Probably frames.
    'Delete':                 (0xA7),
    'Create':                 (0xA8),
    'GetMapTile':             (0xA9),
    # AA- 
    'TakeItem':               (0xAB), #difference from B1?
    'Random':                 (0xAC),
    'New':                    (0xAD),
    'WhoHasItem':             (0xAE), # propaspect, data. returns char.
    'UnseenAF':               (0xAF),
    'UnseenB0':               (0xB0),
    'RemoveItem':             (0xB1),
    'UnseenB2':               (0xB2), 
    'UnseenB3':               (0xB3), 
    'ModalNumberInput':       (0xB4), # (str prompt, int min, int max (inclusive))
    'UnseenB5':               (0xB5),
    'UnseenB6':               (0xB6),
    'WeightCapacity':         (0xB7), #returns number of grains remaining, >=0
    'GetWeight':              (0xB8),
    'JoinParty':              (0xB9),
    'LeaveParty':             (0xBA),
    'ModalPartySelector':     (0xBB),#BB doesn't quite work, might be dead code
    'IsInParty':              (0xBC),
    'PassTime':               (0xBD),
    'UpdateLighting':         (0xBE),
    'ChangeZone':             (0xBF),
    'ShowMenu':               (0xC0),
    'SetFlag':                (0xC1),
    'ClearFlag':              (0xC2),
    #C3! -- seems to set up temporary effects
    'TestFlag':               (0xC4),
    'EmitSignal':             (0xC5),
    'PropListIterator':       (0xC7),
    'ContainerIterator':      (0xC8),
    'RecursiveContainerIterator': (0xC9),
    'PartyIterator':          (0xCA),
    'LocationIterator':       (0xCB),
    'EquipmentIterator':      (0xCC),
    # CD- unseen
    'EnemyIterator':          (0xCE),
    'EffectIterator':         (0xCF),
    'MonsterIterator':        (0xD0), # angers conspecific mons when 1 atkd
    'NearbyIterator':         (0xD1),
    'PlayNote':               (0xD2),
    'PlaySound':              (0xD3),
    'PlayMusic':              (0xD6),
    'PlayAmbientSound':       (0xD7),
    'SetAmbientLighting':     (0xD8),
    'SetLandscapeImage':      (0xD9), # negative for indoors/ no sky.
    'SetTitle':               (0xDA),
    'HasWindow':              (0xDB),
    'GetState':               (0xDC),
    'SetState':               (0xDD),
    'GetStateFlag':           (0xDE), # the address space does not seem to be
    'SetStateFlag':           (0xDF), # shated with DD/DE above.
    'UnknownE0':              (0xE0), # investigation has showed no function
    'MagicAuraEffect':        (0xE1),
    'ShootEffect':            (0xE2),
    'FlashTile':              (0xE3), # momentarily flash a tile
    'HitWithTile':            (0xE4), # flash tile aligning it twixt two props
    'GetNextProp':            (0xE5), # Gets the next prop on the proplist in a
                                      # map or container. If you are calling it
                                      # on a prop on the map, it will skip over
                                      # props in containers. None returned if 
                                      # called on the last prop in a container.
                                      # this is used to implement bellows.
    'RefreshView':            (0xE6),
    'SpecialView':            (0xE7), # 0 For earthquakes, 2 for far sight
    'OpenConversation':       (0xE8),
    'FinishConversation':     (0xE9),
    'BeginCutscene':          (0xEA),
    'EndCutscene':            (0xEB),
    'BeginSlideshow':         (0xEC),
    'EndSlideshow':           (0xED),
    'Slideshow':              (0xEE), #pict resid, text as resref
    'UnseenEF':               (0xEF),
    'AddTask':                (0xF0),
    'FinishTasks':            (0xF1),
    'AddQuest':               (0xF2),
    'CompleteQuest':          (0xF3),
    'AddConversationKeyword': (0xF4),
    'GetSkill':               (0xF5),
    'SetViewPosition':        (0xF6),
    'HasSightLine':           (0xF7),
    'UnseenF8':               (0xF8),
    'UnseenF9':               (0xF9),
    'GetProp':                (0xFA), # get prop from the propref field in map
    'UnseenFB':               (0xFB),
    'SetAutomapping':         (0xFC),
    'SetBackgroundColor':     (0xFD), # parameter is cythera clut color   
    'UnseenFE':               (0xFE),
    'UnseenFF':               (0xFF)
}
DASM_SYSCALL_NAMES = {v:k for k,v in ASM_SYSCALL_NAMES.items()}
DASM_SYSCALL_NAMES['_size'] = 0
DASM_SYSCALL_NAMES['_name'] = 'System'

ASM_STRUCT_HINTS = {
    'flags':                0x00,
    'x':                    0x01, 
    'y':                    0x02, 
    'aspect':               0x03, 
    'obj_type':             0x04, 
    'aspect_and_proptype':  0x05,
    'data1':                0x06, 
    'data2':                0x07, 
    'data3':                0x08,
    'unkn09':               0x09,
    # 0x0A is unseen
    'container':            0x0B,
    # 0x0C-0x10 unseen
    'has_storage':          0x11,
    'storage':              0x12,
    'bit_flags':            0x13,
    'status_flags':         0x14,
    'behavior':             0x15, # behavioral mode
    # 16 appears to get the same value
    'behavior2':            0x16,
    'body':                 0x17, # characters only
    'reflex':               0x18, # cast to Character
    'mind':                 0x19, # before using.
    'exp':                  0x1A, 
    'level':                0x1B,
    'health':               0x1C,
    'full_health':          0x1D,
    'magic':                0x1E,
    'full_magic':           0x1F, 
    'dispatch_thing':       0x20, # haven't been able to figure it out yet
    'training':             0x21,
    'target':               0x22,
    'timing':               0x23, # semantics unsure
    'talk_balloon':         0x26,
    'nutrition':            0x28,
    #seen in monster.
    'monster_flags':        0x32, # 0x4000: bleeds when hit
    'alignment':            0x35,
}
DASM_STRUCT_HINTS = {v:k for k,v in ASM_STRUCT_HINTS.items()}
DASM_STRUCT_HINTS['_size'] = 1
DASM_STRUCT_HINTS['_name'] = 'DObj'

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
   'PutInside':  0x0010,
   'Relinquish': 0x0011,
   'Enter':     0x0014,
   'GetMessage': 0x0015,
   'OnDeath':    0x001D,
   'StepOn':     0x001F,
   'EveryTurn':  0x0020,
   'Weight':     0x0024,
   'AlchemicalProperties': 0x0030,
   'AskedAbout': 0x0033,
   'AIInformation':0x0036,
   'Dug':        0x0039
}
DASM_OBJECT_HINTS = {v:k for k,v in ASM_OBJECT_HINTS.items()}
DASM_OBJECT_HINTS['_size'] = 1
DASM_OBJECT_HINTS['_name'] = 'Object'

DASM_CYTHERA_CHARACTERS = {
    0x00: "NoCharacter",
    0x01: "Hero",
    0x02: "Alaric",
    0x03: "Magpie",
    0x04: "Hadrian",
    0x05: "Emesa",
    0x06: "Hector",
    0x07: "LKH_Guard",
    0x08: "Cademia_Guard",
    0x09: "Ruins_Guard",
    0x0A: "Myus",
    0x0B: "Naxos",
    0x0C: "Darius",
    0x0D: "Pelagon",
    0x0E: "Deiphobus",
    0x0F: "Kosha_Guard",
    0x10: "Atreus",
    0x11: "Ennomus",
    0x12: "Ariethous",
    0x13: "Laodice",
    0x14: "Thuria",
    0x15: "Malis",
    0x16: "Cybele",
    0x17: "Amphidamas",
    0x18: "Eurybates",
    0x19: "Rhesus",
    0x1A: "Lycurgus",
    0x1B: "Erechtheus",
    0x1C: "Thamyris",
    0x1D: "Atymnius",
    0x1E: "Milcom",
    0x1F: "Sardis",
    0x20: "Ake",
    0x21: "Neoptolemus",
    0x22: "Meleager",
    0x23: "Hebe",
    0x24: "Antenor",
    0x25: "Alastor",
    0x26: "Aeneas",
    0x27: "Eioneus",
    0x28: "Parium",
    0x29: "Crito",
    0x2A: "Apis",
    0x2D: "Dares",
    0x2E: "Diomede",
    0x30: "Thetis",
    0x31: "Bias",
    0x32: "Philinus",
    0x33: "Opheltius",
    0x34: "Ascalon",
    0x35: "Ariadne",
    0x36: "Odemia_Guard",
    0x37: "Tlepolemus",
    0x38: "Eteocles",
    0x39: "Laomedon",
    0x3A: "Ilus",
    0x3B: "Autonous",
    0x3C: "Propontis",
    0x3D: "Mantinea",
    0x3E: "Halos",
    0x3F: "Catamarca_Guard",
    0x40: "Oeneus",
    0x41: "Periphas",
    0x42: "Theano",
    0x43: "Hypsenor",
    0x44: "Thoas",
    0x45: "Dymas",
    0x46: "Sacas",
    0x47: "Metopes",
    0x48: "Berossus",
    0x49: "Itanos",
    0x4A: "Timon",
    0x4B: "Prusa",
    0x4C: "Bryaxis",
    0x4D: "Anisa",
    0x4E: "Pheres",
    0x4F: "Charax",
    0x50: "Lindus",
    0x51: "Selinus",
    0x52: "Palaestra",
    0x53: "Tros",
    0x54: "Pnyx_Guard",
    0x55: "Alcestris",
    0x56: "Asius",
    0x57: "Paris",
    0x58: "Helen",
    0x59: "Niobe",
    0x5A: "Larisa",
    0x5B: "Joppa",
    0x5C: "Eudoxus",
    0x5D: "Eumelus",
    0x5E: "Antiphus",
    0x5F: "Polydamas",
    0x60: "Peirithous",
    0x61: "Aethon",
    0x62: "Dryas",
    0x64: "Gate_Guard",
    0x65: "Thersites",
    0x66: "Glaucus",
    0x67: "Borus",
    0x68: "Briseis",
    0x69: "Pelops",
    0x6A: "Alcmena",
    0x6B: "Asteropaeus",
    0x6C: "Stentor",
    0x6D: "Demodocus",
    0x6E: "Thrasymedes",
    0x6F: "Protesilaus",
    0x70: "Menelaus",
    0x71: "Lycaon",
    0x72: "Peleus",
    0x73: "Peisander",
    0x74: "Danae",
    0x75: "Semele",
    0x76: "Alcyone",
    0x77: "Clytemnestra",
    0x78: "Sabinate",
    0x79: "Jhiaxus",
    0x7A: "Unhayt",
    0x7B: "Seqedher",
    0x7C: "Uset",
    0x7D: "Ignae",
    0x7E: "Omen",
    0x7F: "UrSylph",
    0xBD: "Wishing_Fountain",
    0xBE: "Degree_Hall_Door",
}
ASM_CYTHERA_CHARACTERS = {v:k for k,v in DASM_CYTHERA_CHARACTERS.items()}
DASM_CYTHERA_CHARACTERS['_size'] = 2
DASM_CYTHERA_CHARACTERS['_name'] = 'Characters'

