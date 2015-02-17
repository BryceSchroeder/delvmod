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

import os
import util
#import numpy as np
import operator
import json, string, cStringIO as StringIO
from hints import _RES_HINTS, _SCEN_HINTS

def decrypt(data, prokey):
    """Decrypt the data provided with the given pro-key. The prokey is
       used to generate the seed value and parameters for the 
       pseudorandom number generator that is used to create the key."""
    cleartext = bytearray(len(data))
    key = prokey ^ (prokey>>8)
    m = ((prokey & 0x3f) <<2) + 1
    b = prokey >> 6

    for i in xrange(len(data)):
        key = (key*m + b) & 0xFFFF
        cleartext[i] = (data[i]^key)&0xFF

    return cleartext

encrypt = decrypt # Symmetric.

def entropy(data):
    """Return a statistical measure of the entropy of the given data.
       Encrypted (or compressed) data has high entropy. Note that this is
       not infallable and if the cleartext has very high entropy, e.g. in
       the case of compressed data, it may not be able to distinguish
       a successful decryption, at least in principle."""
    counts = [0]*256
    #counts = np.zeros(256) # Uncomment for faster entropy calculations
    # in exchange for a numpy dependency
    for c in data: counts[c] += 1
    base = len(data)/256.0
    for i in xrange(256):
         counts[i] -= base
         counts[i] *= counts[i]
    #counts -= len(data)/256.0
    #counts *= counts
    #return 1 - ((counts.sum()**0.5)/len(data))
    return 1 - sum(counts)**0.5/len(data)

def validate_resource_id(resid):
    """Returns True if resid is valid, False otherwise. Note that validity
       does not imply the resource currently exists in an archive.
       (use .get for that.)"""
    return 0x0100 <= resid <= 0xFFFF
def resid(subindex, n=0):
    """Given a major (master) index page subindex and minor (page) index n,
       return the resource ID."""
    if isinstance(subindex,Resource): subindex,n=subindex.subindex,subindex.n
    assert n < 0x100 and subindex < 0x100
    return ((subindex+1)<<8) | n
def master_index(resid):
    """Return the major (master) index page associated with a resource ID."""
    return ((resid & 0xFF00) >> 8) - 1
def index(resid):
    """Return the minor (page) index associated with a resource ID."""
    return resid & 0xFF
def indices(resid):
    """Return the major and minor indicies associatied with a resource ID.
       If resid is infact already a tuple, return it. """
    return resid if isinstance(resid,tuple) else (master_index(
        resid), index(resid))

class ResourceFile(util.BinaryHandler):
    """Implements a simple file-like interface for resources, with the
       binary utility functions of BinaryHandler."""
    def __init__(self, resource):
        self.resource = resource
        self.position = 0
        self.name = repr(self)
    def __repr__(self):
        return '<ResourceFile from %s. P=%d>'%(self.resource, self.position)
    def tell(self):
        return self.position
    def seek(self, offset, whence=0):
        if whence == 2: # Who uses this?
            self.position = len(self.resource.data) - offset
        elif whence == 1:
            self.position += offset
        elif whence == 0:
            self.position = offset
        else:
            assert False, "Illegal seek whence: %d"%whence
        if self.position >= len(self.resource.data):
            raise IndexError, "Bad seek to 0x%08X, size 0x%08X"%(
                offset, len(self.resource.data))
    def truncate(self, size=None):
        if size is None: size = self.position
        self.resource.data = self.resource.data[:size]
        self.resource.dirty = True
    def read(self, length=None):
        if length is None:
            rv = self.resource.data[self.position:]
            self.position = len(self.resource.data)
        else:
            rv = self.resource.data[self.position:self.position+length]
            self.position += length
        return rv
    def write(self, string):
        self.resource.data[self.position:self.position+len(string)] = string
        self.resource.dirty = True
        self.position += len(string)
    
        

class Resource(object):
    """A an object that represents a an individual resource in 
       an archive. """
    def __init__(self, offset, size, subindex=0, n=0, archive=None):
        self.offset = offset # 0 if never been on disk
        self.data = bytearray(size) # Data in memory
        self.resid = resid(subindex,n)
	self.loaded = not offset
        self.dirty = True
        self.encrypted = None if not self.loaded else False
        self.canon_encryption = self.encrypted
        # Multiple archives may be open.
        self.archive = archive
        # Only needed for debugging and decryption.
        self.subindex = subindex
        self.n = n
    def preview(self): 
        """Generate a human-readable preview."""
        d = filter(
            (lambda x: chr(x) in string.printable and (
                chr(x) not in string.whitespace)), self.get_data())
        return '"%s"'%''.join(map(chr,d[:20]))
        
        
    def human_readable_size(self):
        lend = len(self.data)
        if lend < 9999: return "%d B"%lend
        elif lend < 1e6: return "%.2f kB"%(lend/1000.0)
        else: return "%.2f MB"%(lend/1e6)
    def as_file(self):
        """Return a file-like object representation of the resource.
           If you write to the object, it will indeed change the contents
           of the resource, but in all cases you need to explicitly write
           out the Archive to save changes to disk. It defines read, write,
           seek, tell, truncate, and the various binary helper methods found in 
           delv.util.BinaryHandler."""
        return ResourceFile(self)
     
    def __getitem__(self, n):
        """Return the nth byte of the resource."""
        if not self.loaded: self.load()
        return self.data[n]
    def __setitem__(self, n, v):
        """Set the nth byte of the resource to v."""
        if not self.loaded: self.load()
        self.dirty = True
        self.data[n] = v
    def set_data(self, data):
        """Replace the data of this resource."""
        self.dirty = True
        self.loaded = True
        self.data = bytearray(data)
    def get_data(self):
        """Return the data of this resource as a mutable bytearray.
           If you alter the bytearray, you must manually set .dirty to True."""
        if not self.loaded: self.load()
        return self.data
    def __repr__(self):
        return "<Resource %04X>"%resid(self.subindex,self.n)
    def __str__(self):
        """Return a string of the Resource's contents."""
        if not self.loaded: self.load()
        return str(self.data)
    def __len__(self):
        "Returns the size of the resource data."
        return len(self.data)
    def hint_encryption(self, encrypted, canon_encryption=None):
        self.encrypted = encrypted
        self.canon_encryption = canon_encryption if (
            canon_encryption is not None) else self.encrypted
    def is_encrypted(self):
        """Returns True if this resource is encrypted _in the medium 
           it was loaded from_."""
        if self.encrypted is None: self.load()
        return self.encrypted
    def canonically_encrypted(self):
        """Returns True if this resource is encrypted in the single-file
           archive. If this Resource came from a Delver Archive loaded 
           from a file (or created de novo), this function returns the
           same value as is_encrypted(). However, if we are dealing with
           an archive loaded from a directory that was dumped from an Archive,
           then this returns the original encryption state from that archive.
           (Recall that all resources are saved unencrypted when saving to
           a directory.)"""
        hint = self.archive.canon_encryption_of(self.subindex)
        if hint is not None:
            self.canon_encryption = hint
            return hint
        if self.canon_encryption is None: self.load()
        return self.canon_encryption
    # Private methods
    def write(self, dest):
        new_offset = dest.tell()
        if not self.loaded: 
            self.load()
            #dest.seek(new_offset)
        self.offset = new_offset
        if self.canon_encryption is True:
            dest.write(encrypt(self.data, resid(self.subindex,self.n)))
        elif self.canon_encryption is False:
            dest.write(self.data)
        else:
            assert False,"Writing %s - undefined encryption status"%repr(self)
    def get_metadata(self):
        return self.canon_encryption
    def write_index(self,dest):
        dest.write_offlen(self.offset, len(self.data))
    def save_to_file(self, dest):
        """Saves a resource to an individual file. Never encrypted."""
        if not self.loaded: self.load()
        dest.seek(0)
        dest.write(self.data)
        self.dirty = False  
    def load_from_file(self, src):
        self.data = bytearray(src.read())
        self.loaded = True
        self.encrypted = False
        self.canon_encryption = self.archive.canon_encryption_of(self.subindex)
    def load(self):
        fpos = self.archive.arcfile.tell()
        self.archive.arcfile.seek(self.offset)
        self.data = bytearray(self.archive.arcfile.read(len(self.data)))
        self.loaded=True
        self.archive.arcfile.seek(fpos)
        if self.encrypted is None:
            self.encrypted = self.archive.canon_encryption_of(self.subindex)
            if self.canon_encryption is None: 
                self.canon_encryption = self.encrypted
        if self.encrypted is None:
            self.decrypt_if_required()
        elif self.encrypted is True:
            self.data = decrypt(self.data, resid(self.subindex,self.n))
        
        
    def decrypt_if_required(self):
        print "Decrypt if required", repr(self), self.archive
        presumptive = decrypt(self.data, resid(self.subindex, self.n))
        if entropy(self.data) > entropy(presumptive):
            self.encrypted = True
            self.canon_encryption = True
            self.data = presumptive
        else:
            self.encrypted = False
            self.canon_encryption = False
        

class Archive(object):
    """Class for representing Delver Archives. The implementation is 
       eager; the entire file is loaded into memory when it is opened."""
    known_encrypted = []
    known_clear = []
    def __init__(self, src=None, archive_type='scenario', gui_treestore=None):
        """If src is None, then the constructor creates a new empty archive.
           If src is a file-like object, it will read in an archive from 
           that file. If src is a string, it will attempt to open it as
           a file read-only."""
        self.gui_treestore=gui_treestore
        self.player_name = ''
        self.encryption_knowledge = {}
        for si in self.known_encrypted: self.encryption_knowledge[si] = True
        for si in self.known_clear: self.encryption_knowledge[si] = False

        if type(src) is str:
            if os.path.isfile(src):
                self.from_file(open(src, 'rb'))
            elif os.path.isdir(src):
                self.from_directory(src)
            else:
                assert False, "'%s' isn't a directory or file."%src
        elif src is None:
            self.arcfile = None
            self.source_string = 'Created de novo by delv'
            self.create_header()
            self.create_index()
        else:
            self.from_file(src)
    def from_directory(self, path):
        """Load a delver archive from the provided path."""
        metadata = json.load(open(os.path.join(path, "metadata.json"),'r'))
        self.source_string = metadata['source']+' (From directory %s)'%path
        encrypt = metadata['should_encrypt']
        self.create_header()
        self.create_index()
        self.scenario_title = metadata['scenario_title']
        self.player_name = metadata['player_name']
        for rid,canon_e in encrypt.items():
            rid = int(rid,16)
            subindex,ri = indices(rid)
            nres = Resource(0,0,subindex,ri, self)
            dfile = open(os.path.join(path, '%04X.data'%rid), 'r')
            nres.load_from_file(dfile)
            nres.hint_encryption(False, canon_e)
            self[rid] = nres
            
        self.source_string = 'Packed from %s'%path
        if self.gui_treestore: self.add_gui_tree()
    def from_file(self, src): 
        """Load a delver archive from a file-like object."""
        self.arcfile = util.BinaryHandler(src)
        self.load_header()
        self.load_index()
        self.source_string = "Loaded from file object %s"%src
    def from_string(self, src):
        """Load a delver archive from an indexable object."""
        self.from_file(cStringIO.StringIO(src))
        self.source_string = "Loaded from string"
    def from_path(self, path):
        """Load a Delver archive from a file system path."""
        self.source_string = "Loaded from path %s"%path
        if os.path.isdir(path):
            self.from_directory(path)
        else:
            self.from_file(open(path, 'rb'))
    def source(self):
        '''Return a string explaining where this archive came from.'''
        return self.source_string
    def to_directory(self, path):
        """Dump the contents of the archive, unencrypted, to path."""
        assert os.path.isdir(path)
        metadata = {'source': self.source(), 
            'creator': 'delv (www.ferazelhosting.net/wiki/delv)',
            'scenario_title': self.scenario_title,
            'player_name': self.player_name}
        encrypt = {}
        for resource in self.resources():
            if not resource: continue # don't preserve empties
            outf = open(os.path.join(path, "%04X.data"%resid(resource)), 'w')
            resource.save_to_file(outf)
            encrypt["%04X"%resid(resource)] = resource.get_metadata()
            outf.close()
        metadata['should_encrypt'] = encrypt
        metafile = open(os.path.join(path, "metadata.json"), 'w')
        json.dump(metadata, metafile)
        metafile.close
    def to_file(self, dest):
        """Write a Delver archive to the destination file-like
           object (must be open for writing, obviously)"""
        dest = util.BinaryHandler(dest)
        self.save_header(dest)
        # Skip to just past the spot where we'll put the master index later
        dest.write(bytearray(0x800))
        # Write all the resources. 
        for n,subindex in enumerate(self.all_subindices):
            if not subindex:
                self.master_index[n] = 0,0
                continue
            at_least_one = False
            for m,res in enumerate(subindex):
                if res: 
                    res.write(dest)
                    at_least_one = True
            if not at_least_one: # Prune empty subindices, if any arise
                self.master_index[n] = 0,0
                self.all_subindices[n] = []
        # Write all our resource indices, now that they know where they are.
        for n,subindex in enumerate(self.all_subindices):
            if not subindex: continue

            # Can make it only as long as it needs to be...?
            self.master_index[n] = dest.tell(), 2048 
            for res in subindex:
                if res:
                    res.write_index(dest)
                else:
                    dest.write_offlen(0,0)
        # Now write the master index:
        dest.seek(self.master_index_offset + 8)
        for offset,length in self.master_index:
            dest.write_offlen(offset,length)
                
    def canon_encryption_of(self, subindex):
        return self.encryption_knowledge.get(subindex, None)

    def to_string(self):
        """Produces one (possibly very large) string with the 
           archive in it. Mainly here for front-end web stuff."""
        stio = StringIO.StringIO()
        self.to_file(stio)
        return stio.getvalue()

    def to_path(self, path):
        """Save the archive to a location on disk."""
        if os.path.isdir(path):
            self.to_directory(path)
        else:
            self.to_file(open(path, 'wb'))

    def get(self, idx, create_new=False):
        """Get a resource by its two-byte-integer composite resource ID,
           or by a tuple of integers (subindex, ID).
           A Resource object is returned if the resource exists, otherwise
           None is returned. (This can be efficiently used to check if a
           Resource exists.)"""
        subindex,n = indices(idx)
        if not self.all_subindices[subindex]:
            if create_new:
                self.all_subindices[subindex] = [None]*256
            else:
                return None
        r = self.all_subindices[subindex][n]
        if r is None and create_new:
            r = Resource(0,0,subindex,n,self)
            self.all_subindices[subindex][n] = r
        return r
                

    def __getitem__(self, idx): 
        """Retrieve the data of a resource using the index[] operator. 
           Its sematics differ slightly from .get in that it will raise 
           IndexError if the resource does not exist, whereas .get will not 
           produce exceptions. idx can be the two-byte resource ID or it can be
           a tuple with the subindex and individual resource ID. Another
           difference is that the content of the resource, and not the
           corresponding Resource object, is returned."""
        res = self.get(idx)
        if res is None:
            raise IndexError("Resource %s is not in use"%idx)
        return res.get_data()
        
    def __setitem__(self, idx, value):
        """idx sematics are the same as __getitem__. If value is not 
           already a Resource object, it will be automatically wrapped.
           New resources are created if needed."""
        subindex,n = indices(idx)
        if isinstance(value, Resource):
            if not self.all_subindices[subindex]:
                self.all_subindices[subindex] = [None]*256
            if not self.master_index[subindex]:
                self.master_index[subindex] = (-1,-1)
            self.all_subindices[subindex][n] = value
            if not value.loaded: value.load()
            value.archive = self
        else:
            res = self.get(idx, True)
            res.set_data(value)
    def resource_ids(self, subindex=None):
        """If subindex is not None, returns a list of valid resource IDs
           (not resource objects) for that subindex, possibly empty if
           the subindex is empty or does not exist. If subindex is None,
           it returns a list of all resource IDs that are valid for this
           archive in toto."""
        if subindex is not None:
            sx = self.all_subindices[subindex]
            return [resid(subindex,n) for n,r in enumerate(sx) if r]
        else:
            return reduce(operator.add, 
                [self.resource_ids(si) for si in self.subindices()])
    def subindices(self):
        """Return a list of valid subindices for this archive."""
        return [n for n in xrange(len(self.master_index)
            ) if self.master_index[n]]


    def resources(self, subindex=None):
        """Returns a list of all the Resource objects in the subindex
           provided. (Possibly an empty list.) If no subindex is provided,
           returns a list of all the resources in the archvie."""
        if subindex is not None:
            sx = self.all_subindices[subindex]
            return [r for r in sx if r]
        else:
            return reduce(operator.add, 
                [self.resources(si) for si in self.subindices()])
    def __iter__(self):
        """This iterator is over all extant resources in the archive. That
           is, if d is an Archive, the following are equivalent:
           for resource in d: ...
           for resource in d.resources(): ...
           Perhaps a future lazy version could be made, in which case the
           iterator would be more efficient.
        """
        return iter(self.resources())
    # --------------------------- Private methods ------------------------
    def create_header(self, scenario="Cythera: Fate of Alaric"):
        self.scenario_title = scenario
        # What these are for, we don't know.
        self.unknown_40 = 0x13
        self.unknown_42 = 2
        self.unknown_48 = 2
        self.master_index_offset = 0x80
        self.master_index_length = 2048
    def create_index(self, size=256):
        self.master_index = [None]*size
        self.all_subindices = []
        for _ in xrange(size): self.all_subindices.append([])
        self.master_index_length = 8*size
    def load_header(self):
        self.scenario_title = self.arcfile.read_pstring(0)
        self.player_name = self.arcfile.read_pstring(0x20)
        self.unknown_40 = self.arcfile.read_uint8(0x40)
        self.unknown_42 = self.arcfile.read_uint8(0x42)
        self.unknown_48 = self.arcfile.read_uint8(0x48)
        self.master_index_offset = self.arcfile.read_uint32(0x80)
        self.master_index_length = self.arcfile.read_uint32(0x84)
    def save_header(self,dest):
        dest.write_pstring(self.scenario_title, 0)
        dest.write_pstring(self.player_name, 0x20)
        dest.write_uint8(self.unknown_40, 0x40)
        dest.write_uint8(self.unknown_42, 0x42)
        dest.write_uint8(self.unknown_48, 0x48)
        dest.write_offlen(self.master_index_offset, self.master_index_length,
            self.master_index_offset)
    def load_index(self):
        self.arcfile.seek(self.master_index_offset+8)
        self.master_index = [None]*(self.master_index_length//8 - 1)
        for n in xrange(len(self.master_index)):
             self.master_index[n] = self.arcfile.read_offlen()
        self.all_subindices = []
        for subn,(offset, length) in enumerate(self.master_index):
            
            if not offset: 
                self.all_subindices.append([])
                continue
            subindex = []
            self.arcfile.seek(offset)
            size = length / 8
            rescount = 0
            for n in xrange(size):
                res_offset, res_length = self.arcfile.read_offlen()
                if res_offset:
                    subindex.append(Resource(res_offset, res_length, 
                       subn, n, self))
                    rescount += 1
                else:
                    subindex.append(None)
            self.all_subindices.append(subindex)
        if self.gui_treestore: self.add_gui_tree()
    def add_gui_tree(self):
        self.gui_tree_rows = {}
        for subn,subindex in enumerate(self.all_subindices):
             rescount = len([r for r in subindex if r])
             if not rescount: continue
             t=self.gui_treestore.append(None,["%3d [%02Xxx]"%(subn,subn+1),
                 "%3d item%s"%(rescount, '' if rescount == 1 else 's'),
                   _SCEN_HINTS.get(subn, "Unknown"), subn,-1])
             self.gui_tree_rows[subn] = t
             for r in subindex:
                 if not r: continue
                 self.gui_treestore.append(t, [
                     "%04X"%resid(r.subindex,r.n),
                     r.human_readable_size(),
                     _RES_HINTS.get(resid(r.subindex,r.n),""),
                     r.subindex,r.n
                     ])

    
        
class Player(Archive):
    """Class for manipulating Delver Player Files, i.e. saved games."""
    

class Scenario(Archive):
    """Class for manipulating Delver Scenario files."""
    known_encrypted = [1,2,4,7,8,9,10,11,12,13,14,15,16,
                       19,20,23,24,25,26,27,29,47]
    known_clear = [0,3,127,128,131,135,137,141,142,143,
                   144,187,239,254]

class Patch(Scenario):
    """Class for manipulating Delver patchfiles."""
    # public:
    patch_info = "This patch created by delv.archive.Patch"
    def patch_info(self, infostring):
        "Set the description of the patch."
        self[0xFFFF] = 'MAGPY'+infostring
        self.patch_info = infostring
    def get_patch_info(self):
        """Return the patch info string. mag.py and Magpie formats supported."""
        patchres = self.get(0xFFFF)
        if not patchres: return ''
        data = patchres.as_file()
        if data.read(5) == 'MAGPY': # mag.py format
            self.patch_info = data.read()
        else: # Magpie format
            self.patch_info = data.read_pstring(0x138)
        return self.patch_info
        
        
    def compatible(self, other_patch, exclude = [0xFFFF,0xBC00,0xBC35]):
        """Returns False if two patches are not compatible. Returns True
           if they might be compatible. ;) """
        exclude = set(exclude)
        set_res = set(self.resource_ids())
        patch_res = set(other_patch.resource_ids())
        return not (set_res-exclude).intersection(patch_res-exclude)
    def patch(self, target):
        "Apply this patch to the target."
        for resource in self:
            target[resid(resource)] = resource
    def diff(self, base, modified,exclude=[0xFFFF]):
        """Add the differences between Archives base and modified to this
           patch archive, such that if .apply(base) is subsequently used,
           base will come to contain the same data as modified."""
        exclude = set(exclude)
        for resid in modified.resource_ids():
            if resid in exclude: continue
            eq = base.get(resid)
            if (not eq) or (eq.get_data() != modified.get(resid).get_data()):
                nd = modified.get(resid)
                if not nd.loaded: nd.load() 
                self[resid] = nd
         
            
