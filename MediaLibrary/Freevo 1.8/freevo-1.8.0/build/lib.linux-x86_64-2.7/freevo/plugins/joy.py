# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# joy.py - A joystick control plugin for Freevo.
# -----------------------------------------------------------------------
# $Id: joy.py 9979 2007-10-14 15:27:08Z duncan $
#
# Notes:
# To use this plugin make sure that your joystick is already working
# properly and then configure JOY_DEV and JOY_CMDS in your local_conf.py.
# You will also need to have plugin.activate('joy') in your config as well.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al.
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


import sys
import os
import select
import struct
import traceback
from time import sleep

import config
import plugin
import rc

rc = rc.get_singleton()

class PluginInterface(plugin.DaemonPlugin):
    """
    A joystick control plugin for Freevo

    To use this plugin make sure that your joystick is already working properly and
    then configure JOY_DEV and JOY_CMDS in your local_conf.py.  You will also need
    to have plugin.activate('joy') in your config as well.
    """

    def __init__(self):
        self.device_name = ''
        self.enabled = True

        if config.JOY_DEV == 0:
            self.reason = 'Joystick input module disabled'
            return

        self.device_name = '/dev/input/js' + str((config.JOY_DEV - 1))

        try:
            self.joyfd = os.open(self.device_name, os.O_RDONLY|os.O_NONBLOCK)
            _debug_('self.joyfd = %s' % self.joyfd, level=5)
        except OSError:

            print 'Unable to open %s, trying /dev/js%s...' % \
                  (self.device_name, str((config.JOY_DEV - 1)))
            self.device_name = '/dev/js' + str((config.JOY_DEV - 1))

            try:
                self.joyfd = os.open(self.device_name, os.O_RDONLY|os.O_NONBLOCK)
                _debug_('self.joyfd = %s' % self.joyfd, level=5)
            except OSError:
                print 'Unable to open %s, check modules and/or permissions' % \
                      self.device_name
                self.reason = 'unable to open device'
                return

        # ok, joystick is working
        plugin.DaemonPlugin.__init__(self)
        self.plugin_name = 'JOY'

        print 'Using joystick %s (%s) (sensitivity %s)' % (config.JOY_DEV, self.device_name, config.JOY_SENS)

        self.poll_interval  = 1
        self.poll_menu_only = False


    def config(self):
        return [
            ('JOY_DEV', 1, 'Joystick number, 1 is \'/dev/js0\' or \'/dev/input/js0\''),
            ('JOY_SENS', 16384, 'Joystick sensitivity'),
            ('JOY_LOCKFILE', None, 'Joystick lock file'),
         ]


    def poll(self):
        if not self.enabled:
            return

        command = ''
        (r, w, e) = select.select([self.joyfd], [], [], 0)
        _debug_('r,w,e = %s,%s,%s' % (r,w,e), level=5)

        self.sensitivity = config.JOY_SENS

        if r:
            c = os.read(self.joyfd, 8)
        else:
            return

        data = struct.unpack('IhBB', c)
        if data[2] == 1 & data[1] == 1:
            button = 'button '+str((data[3] + 1))
            command = config.JOY_CMDS.get(button, '')

        if data[2] == 2:
            if ((data[3] == 1) & (data[1] < -self.sensitivity)):
                button = 'up'
                command = config.JOY_CMDS['up']
            if ((data[3] == 1) & (data[1] > self.sensitivity)):
                button = 'down'
                command = config.JOY_CMDS['down']
            if ((data[3] == 0) & (data[1] < -self.sensitivity)):
                button = 'left'
                command = config.JOY_CMDS['left']
            if ((data[3] == 0) & (data[1] > self.sensitivity)):
                button = 'right'
                command = config.JOY_CMDS['right']

        if command != '':
            _debug_('Translation: "%s" -> "%s"' % (button, command))
            command = rc.key_event_mapper(command)
            if command:
                if not config.JOY_LOCKFILE:
                    rc.post_event(command)
                elif not os.path.exists(config.JOY_LOCKFILE):
                    rc.post_event(command)

    def enable(self, enable_joy=True):
        self.enabled = enable_joy
        return
