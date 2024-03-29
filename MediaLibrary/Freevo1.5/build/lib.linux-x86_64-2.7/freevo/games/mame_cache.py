# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mame_cache.py - Module for caching MAME rom information for Freevo.
# -----------------------------------------------------------------------
# $Id: mame_cache.py,v 1.19 2004/07/10 12:33:38 dischi Exp $
#
# Notes: This contains some rominfo code from videogame.py.
# Todo:        
#
# -----------------------------------------------------------------------
# $Log: mame_cache.py,v $
# Revision 1.19  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.18  2004/02/24 18:05:19  mikeruelle
# make the info retreival a lot better
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------- */


import sys
import random
import time, os, string

# Classes to keep track of our roms
import mame_types

# Configuration file.
import config

# Various utilities
import util

# RegExp
import re

from gui.PopupBox import PopupBox

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


#
# Lets get a MameRomList if one is available from disk.  If not 
# then we shall return an empty one.
#
def getMameRomList():
    file_ver = None
    mameRomList = None

    if os.path.isfile(config.GAMES_MAME_CACHE):
        mameRomList = util.read_pickle(config.GAMES_MAME_CACHE)

        try:
            file_ver = mameRomList.TYPES_VERSION
        except AttributeError:
            print 'The cache does not have a version and must be recreated.'

        if file_ver != mame_types.TYPES_VERSION:
            print (('MameRomList version number %s is stale (new is %s), must ' +
                    'be reloaded') % (file_ver, mame_types.TYPES_VERSION))
        else:
            if DEBUG:
                print 'Got MameRomList (version %s).' % file_ver

    if mameRomList == None:
        mameRomList = mame_types.MameRomList()

    print "MameRomList has %s items." % len(mameRomList.getMameRoms())
    return mameRomList


#
# function to save the cache to disk
#
def saveMameRomList(mameRomList):

    if not mameRomList or mameRomList == None:
        mameRomList = mame_types.MameRomList()

    util.save_pickle(mameRomList, config.GAMES_MAME_CACHE)


#
# We should keep mameRomList up to date.
# This function takes in a list of files and makes sure
# the cache has any relevant information.
#
def updateMameRomList(mame_cmd):
    # This method of running xmame --listinfo and parsing the output was
    # borrowed from pyrecade - http://pyrecade.sf.net.

    try:
        listinfo = os.popen(mame_cmd + ' --listinfo', 'r')
    except:
        print 'Unable to get mame listinfo.'
	return FALSE

    newRom = mame_types.MameRom()
    cache = {}

    for line in listinfo.readlines():
        if re.compile("^\tname").match(line):
            newRom.name = re.compile("^\tname (.*)").match(line).group(1)
        elif re.compile("^\tdescription").match(line):
            newRom.description = re.compile("^\tdescription (.*)").match(line).group(1)[1:-1]
        elif re.compile("^\tyear").match(line):
            newRom.year = re.compile("^\tyear (.*)").match(line).group(1)
        elif re.compile("^\tmanufacturer").match(line):
            newRom.manufacturer = re.compile("^\tmanufacturer (.*)").match(line).group(1)[1:-1]
        elif re.compile("^\tcloneof").match(line):
            newRom.cloneof = re.compile("^\tcloneof (.*)").match(line).group(1)
        elif re.compile("^\tromof").match(line):
            newRom.romof = re.compile("^\tromof (.*)").match(line).group(1)
        elif re.compile("^game \(").match(line):
            # We've reached a new game so dump everthing we have so far
            if newRom.name:
                # add the new rom to the cache.
                cache[newRom.name] = newRom
                # make a new mameRom
                newRom = mame_types.MameRom()

    listinfo.close()

    mameRomList = mame_types.MameRomList()
    mameRomList.setMameRoms(cache)
    saveMameRomList(mameRomList)

    return TRUE


#
# This will return a list of things relevant to MameItem based on
# which mame files we have cached.  It ignores files we don't.
# Returns: title, filename, and image file for each mame_file.
#
def getMameItemInfoList(mame_files, mame_cmd):
    items = []
    rm_files = []

    print "Call MAME command : %s" % mame_cmd
    # Only build the cache if it doesn't exis.
    if not os.path.isfile(config.GAMES_MAME_CACHE):
        waitmsg = PopupBox(text=_('Generating MAME cache, please wait.'))
	waitmsg.show()
        mame_ok = updateMameRomList(mame_cmd)
	waitmsg.destroy()

        if not mame_ok:
            return (mame_files, [])

    mameRomList = getMameRomList()
    roms = mameRomList.getMameRoms()

    for romfile in mame_files:
        key = os.path.splitext(os.path.basename(romfile))[0]
        if roms.has_key(key):
            rom = roms[key]
	    info = { 'manufacturer': rom.manufacturer,
	             'name': rom.name,
	             'description': rom.description,
	             'year': rom.year,
	             'cloneof': rom.cloneof,
	             'romof': rom.romof } 
            items += [(rom.description, romfile, None, info)]
            rm_files.append(romfile)

    return (rm_files, items)


def getMameItemInfo(mame_file):
    if not os.path.isfile(config.GAMES_MAME_CACHE):
        return
    mameRomList = getMameRomList()
    roms = mameRomList.getMameRoms()
    key = os.path.splitext(os.path.basename(mame_file))[0]
    if roms.has_key(key):
        return roms[key]
    else:
        return

