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
import colormap

class DelvImage(object):
    """This is the base class for all forms of Delver Compressed (sprite)
       graphics, images in the proprietary format used by the Delver Engine.
       Unless you are loading graphics from a delv Resource,
       you should probably not instantiate this class directly, but instead
       one of its child classes (General, for sized images; TileSheet, for
       32x512 sets of sixteen 32x32 tiles; Portrait, for 64x64 character
       portraits; or Landscape, for 288x32 level images.
       
       The file format used, is documented here in detail:
       http://www.ferazelhosting.net/wiki/Delver%20Compressed%20Graphics
    """
    canonical_size = None,None
    has_header = False
    def __init__(self, src=None):
        """Create a new Delver Compressed Graphics Image. src can be None,
           the default, which creates an empty image of the default size
           for this type, or an random-access indexable item such as a list,
           string or numpy array, which will be assumed to be compressed data, 
           a delv Resource object (also assumed to be compressed data.)"""
        pass

    def decompress(self, data):
        """Decompress the indexable-item data provided into this image.
           You shouldn't normally need to call this explicitly."""
        pass

    def compress(self):
        """Create the compressed version of the graphic. You shouldn't
           normally need to call it explicitly."""
        pass

    def get_data(self):
        """Return the compressed image data, as a string."""
        pass

    def get_image(self,form='numpy'):
        """Get the whole image. By default returns a two-dimensional
           numpy array (the internal storage format), but it will also
           accept the form parameters 'numpy1' for a 1D array, 
           and 'pil' for a Python Imaging Library indexed color image."""
        pass

    def draw_into(self,src,x=0,y=0,w=0,h=0):
        """Draw an image src into this object, optionally specifying
           destination coordinates and a width and height if you wish
           to copy less than the entirety of the source image.
           src may be a PIL image, or anything that can be indexed 
           like src[x,y].
           The source must already be 8-bit indexed color using the colormap
           for your target game (e.g the Cythera CLUT); dithering
           and color-matching are beyond the scope of this project."""
        pass
    def draw_into_tile(self,src,n):
        """Conveninence method to draw to a particular tile. n has the
           same semantics as for get_tile below, including for situations
           in which non-canonical tileset shapes are addressed."""
        pass

    def get_tile(self,n,form='numpy'):
        """Get the nth 32x32 tile of this image. Clasically meaningful only
           for tile sheets, where it returns the nth from the top (counting
           from zero.) For the sake of completeness, though, it will work
           on other images, in which case the tiles are numbered top to 
           bottom, left to right. formats returnable are the same as those
           for get_image."""
        pass

    def tile_rect(self,n):
        """Return the bounding rectangle of the nth tile."""
        pass
  
    def get_size(self):
        """Return (width,height)."""
        pass
    ##########################  PRIVATE METHODS  #######################
    # The methods below may change freely between delv versions, and are
    # intended for the internal use of other delv code only.
    def run(self, length, color):
        pass
    def copy(self, length, origin):
        pass
    def data(self, pixels):
        pass
    def put_pixel(self, color):
        pass

class General(DelvImage):
    has_header = True

class TileSheet(DelvImage):
    canonical_size = 32,512

class Portrait(DelvImage):
    canonical_size = 64,64

class Landscape(DelvImage):
    canonical_size = 288,32

