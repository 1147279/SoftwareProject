# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# genericitem.py - Item for generic objects
# -----------------------------------------------------------------------
# $Id: genericitem.py 10224 2007-12-21 09:03:42Z duncan $
#
# Notes:
# Todo:
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
# -----------------------------------------------------------------------


import os

import config
import game

TRUE  = 1
FALSE = 0

import rc
import time
import copy

from item import Item
import event as em
from struct import *
from string import *
from re import *


class GenericItem(Item):
    def __init__(self, file, cmd=None, args=None, imgpath=None, parent=None):
        _debug_('GenericItem.__init__(file=%r, cmd=%r, args=%r, imgpath=%r, parent=%r)' % \
            (file, cmd, args, imgpath, parent), 2)
        Item.__init__(self, parent)
        self.type  = 'generic'            # fix value
        self.set_url(file, info=True)
        self.parent = parent

        self.name = os.path.splitext(os.path.basename(file))[0]

        # find image for this file
        shot = imgpath + '/' + os.path.splitext(os.path.basename(file))[0] + ".png"
        if os.path.isfile(shot):
            self.image = shot
        elif os.path.isfile(os.path.splitext(file)[0] + ".png"):
            self.image = os.path.splitext(file)[0] + ".png"

        command = ['--prio=%s' % config.GAMES_NICE, cmd]
        command.extend(args.split())
        if os.path.getsize(file) > 0:
            command.append(file)

        self.command = command

        self.game_player = game.get_singleton()


    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        _debug_('sort(mode=%r)' % (mode), 2)
        return self.name


    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        _debug_('actions()', 2)
        return [ ( self.play, 'Play' ) ]


    def play(self, arg=None, menuw=None):
        _debug_('play(arg=%r, menuw=%r)' % (arg, menuw), 2)
        self.parent.current_item = self

        if not self.menuw:
            self.menuw = menuw

        if self.menuw.visible:
            self.menuw.hide()

        _debug_("Playing:  %s" % self.filename)

        self.game_player.play(self, menuw)


    def stop(self, menuw=None):
        _debug_('stop(menuw=%r)' % (menuw), 2)
        self.game_player.stop()


    def eventhandler(self, event, menuw=None):
        _debug_('eventhandler(event=%r, menuw=%r)' % (event, menuw), 2)

        if event == em.STOP:
            self.stop()
            rc.app(None)
            if not menuw == None:
                menuw.refresh(reload=1)

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
