# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# irsend_generic.py - Send commands to an external tv receiver using a
#                     shell command like irsend from Lirc.
# -----------------------------------------------------------------------
# $Id: irsend_generic.py 9999 2007-10-18 15:31:31Z duncan $
#
# Notes:  Plugin wrapper for irsend or any other remote controll command.
#
# Todo:
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


import os, sys, time, string
import plugin


class PluginInterface(plugin.Plugin):
    """
    Use this plugin if you need to use Lirc's irsend (or similar) command
    to tell an external tuner to change the channel.

    Example usage (local_conf.py):
    | plugin_external_tuner = plugin.activate('tv.irsend_generic', args=('/usr/bin/irsend SEND_ONCE <remote_name>',))

    Where <remote_name> is the name of the remote you are using to send codes
    with in lircd.conf.
    """

    def __init__(self, command, enterkey=None):
        plugin.Plugin.__init__(self)

        self.command = command
        self.enterkey = enterkey

        plugin.register(self, 'EXTERNAL_TUNER')


    def setChannel(self, chan):
        chan = str(chan)
        digits = len(chan)
        chan_args = ''

        for i in range(digits):
            chan_args += chan[i] + ' '

        self.transmitSignal(chan_args)
        if self.enterkey:
            # Sometimes you need to send a "ENTER" or a "SELECT"
            # after keying in a code.
            self.transmitSignal(self.enterkey)


    def transmitButton(self, button):
        print 'sending button: %s\n' % button
        self.transmitSignal(code)


    def transmitSignal(self, code):
        sendcmd = '%s %s' % (self.command, code)
        os.system(sendcmd)
