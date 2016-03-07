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
#
# "Cythera" and "Delver" are trademarks of either Glenn Andreas or 
# Ambrosia Software, Inc. 
# FIXME
import csv
import gtk
import editors

def int_parser(s):
    base = 10
    if '0x' in s:
        base = 16
        s = s.replace('0x','')
    return int(s.strip().split()[0],base)


class RLCol(object):
    # Formatter: given a row from delv and the column assignment,
    # produce string to go in the table.
    _def_formatter = {
        int: (lambda d: str(d)),
        str: (lambda d: d),
        bool: (lambda d: str(d))
    }
    # Parser: given a row from the table and a column assignment,
    # produce a row to 
    _def_parser = {
        int: int_parser,
        str: (lambda s: s),
        bool: (lambda b: bool(b))
    }
    _def_validator = {
        int: (lambda _:  True),
        str: (lambda _:  True),
        bool: (lambda _:  True),
    }
    def __init__(self, title, dtype=int, formatter=None,parser=None,
                 validator=None):
        self.title = title
        self.dtype = dtype
        self.formatter= formatter if formatter else self._def_formatter[dtype]
        self.parser = parser if parser else self._def_parser[dtype]
        self.validator= validator if validator else self._def_validator[dtype]
    def assign_col(self,col):
        self.tree_col = n
    def assign_field(self,field):
        self.delv_field = field
    def format(self, delv_row):
        pass
    

class RecordListEditor(editors.Editor):
    """Delver has many resources that take the form of an array of some kind
       of binary records. This is a generic editor for them. It edits 
       delv.store.RecordList objects implementing .rows() (and subclasses 
       thereof.)"""
    name = "Unimplemented (Record List Editor)"
    default_size = 512,400

class PropTileAssociation(RecordListEditor):
    name = "Prop-Tile Associations Editor"
    columns_setup = [
        RLCol("Prop ID"),
        RLCol("Tile ID")
    ]
