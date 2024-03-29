# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# autocolor.py - An tool for Freevo
# -----------------------------------------------------------------------
# $Id: autocolor.py 8441 2006-10-21 11:15:52Z duncan $
#
# Notes:
#
#       This plugin allows you to call an arbitrary system command
# before playing video. I use it to adjust the brightness/contrast on
# my G400 using the hardware, which provides a good quality video display,
# but I prefer to have a darker menu because it's not the "focus" when
# not playing video.
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
import sys
import copy

import config
import plugin

from event import *


class PluginInterface(plugin.DaemonPlugin):
    """
    autocolor plugin.

    This plugin allows you to run an arbitrary command before playing
    a video file. I use this because I prefer to adjust brightness/contrast
    in hardware before playing a video file.

    activate with plugin.activate('plugin.autocolor')

    Yes, I spelled it the American way. No, I'm not American.

    """
    def __init__(self,before='/bin/true', after='/bin/true'):
        """
        init the autocolor plugin
        """
        plugin.DaemonPlugin.__init__(self)
        self.poll_interval   = 200
        self.plugins = None
        plugin.register(self, 'autocolor')
        self.before = before
        self.after = after
        
    def eventhandler(self, event, menuw=None):
        """
        catch VIDEO_START/VIDEOEND and run a command, return False, maybe someone
        else is watching for the event.
        """


        if event == VIDEO_START:
            _debug_('Recieved VIDEO_START event',2)
            os.system(self.before)

        if event == VIDEO_END:
            _debug_('Recieved VIDEO_STOP event',2)
            os.system(self.after)

        return False
