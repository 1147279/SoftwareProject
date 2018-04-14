# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# A plugin to view your list of scheduled recordings.
# -----------------------------------------------------------------------
# $Id: scheduled_recordings.py 10467 2008-03-05 22:26:47Z duncan $
#
# Notes:
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


import os
import config, plugin, menu, rc
from tv.record_client import RecordClient

from gui.AlertBox import AlertBox
from item import Item
from tv.programitem import ProgramItem


class ScheduledRecordingsItem(Item):
    def __init__(self, parent):
        Item.__init__(self, parent, skin_type='tv')
        self.name = _('Scheduled Recordings')
        self.menuw = None
        self.recordclient = RecordClient()


    def actions(self):
        return [ ( self.display_schedule , _('Display Scheduled Recordings') ) ]


    def display_schedule(self, arg=None, menuw=None):
        if not self.recordclient.pingNow():
            AlertBox(self.recordclient.recordserverdown).show()
            return

        items = self.get_items()
        if not len(items):
            AlertBox(_('Nothing scheduled.')).show()
            return

        schedule_menu = menu.Menu(_('Scheduled Recordings'), items,
            reload_func=self.reload, item_types='tv program menu')
        self.menuw = menuw
        rc.app(None)
        menuw.pushmenu(schedule_menu)
        menuw.refresh()


    def reload(self):
        menuw = self.menuw

        menu = menuw.menustack[-1]

        new_choices = self.get_items()
        if not menu.selected in new_choices and len(new_choices):
            sel = menu.choices.index(menu.selected)
            if len(new_choices) <= sel:
                menu.selected = new_choices[-1]
            else:
                menu.selected = new_choices[sel]

        menu.choices = new_choices

        return menu


    def get_items(self):
        items = []

        if not self.recordclient.pingNow():
            AlertBox(self.recordclient.recordserverdown).show()
            return []

        (status, schedule) = self.recordclient.getScheduledRecordingsNow()
        if status:
            progs = schedule.getProgramList()

            f = lambda a, b: cmp(a.start, b.start)
            progs = progs.values()
            progs.sort(f)
            for prog in progs:
                items.append(ProgramItem(self, prog, context='schedule'))
        else:
            AlertBox(_('Get scheduled recordings failed')+(':\n%s' % schedule)).show()
            return []

        return items


class PluginInterface(plugin.MainMenuPlugin):
    """
    This plugin is used to display your currently scheduled recordings.

    | plugin.activate('tv.scheduled_recordings')
    """

    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)

    def items(self, parent):
        return [ ScheduledRecordingsItem(parent) ]