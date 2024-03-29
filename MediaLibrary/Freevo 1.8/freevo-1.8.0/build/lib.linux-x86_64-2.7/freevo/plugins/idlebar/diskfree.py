# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# IdleBar plug-in for showing the freedisk space for recording
# -----------------------------------------------------------------------
# $Id: diskfree.py 10387 2008-02-20 20:40:25Z duncan $
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

__author__ = 'Tanja Kotthaus <owigera@web.de>'

# python modules
import time
import os, pygame

# freevo modules
from plugins.idlebar import IdleBarPlugin
import plugin, config
import util.fileops as util


class PluginInterface(IdleBarPlugin):
    """
    Displays the amount of free disk space

    Activate with:
    | plugin.activate('idlebar.diskfree', level=30)

    This plugin displays the total amount of free disk space for recordings
    """

    def __init__(self):
        if not config.TV_RECORD_DIR:
            self.reason = 'TV_RECORD_DIR is not set'
            return
        if not os.path.isdir(config.TV_RECORD_DIR):
            self.reason = 'TV_RECORD_DIR "%s" is not a directory' % (config.TV_RECORD_DIR)
            return
        IdleBarPlugin.__init__(self)
        self.plugin_name = 'idlebar.diskfree'
        self.time = 0
        self.diskfree = 0
        self.freespace = 0
        self.totalspace = 0
        self.percent = 0.0

        self.diskimg = os.path.join(config.ICON_DIR, 'status/diskfree.png')
        self.goodimg = os.path.join(config.ICON_DIR, 'status/diskfree-good.png')
        self.poorimg = os.path.join(config.ICON_DIR, 'status/diskfree-poor.png')
        self.badimg  = os.path.join(config.ICON_DIR, 'status/diskfree-bad.png')
        self.cacheimg = {}


    def config(self):
        return [
            ('TV_RECORD_DIR', None, 'Directory for TV recordings'),
            ('DISKFREE_LOW', 20, 'Amount of space in GB to show the low warning icon'),
            ('DISKFREE_VERY_LOW', 8, 'Amount of space in GB to show the very low warning icon'),
        ]

    def getimage(self, image, osd, cache=False):
        if image.find(config.ICON_DIR) == 0 and image.find(osd.settings.icon_dir) == -1:
            new_image = os.path.join(osd.settings.icon_dir, image[len(config.ICON_DIR)+1:])
            if os.path.isfile(new_image):
                image = new_image
        if cache:
            if image not in self.cacheimg.keys():
                self.cacheimg[image] = pygame.image.load(image)
            return self.cacheimg[image]

        return pygame.image.load(image)

    def getDiskFree(self):
        """
        Determine amount of freedisk space
        Update maximum every 30 seconds

        """
        if not os.path.isdir(config.TV_RECORD_DIR):
            return

        self.time = time.time()
        freespace = util.freespace(config.TV_RECORD_DIR)
        totalspace = util.totalspace(config.TV_RECORD_DIR)
        self.diskfree = _('%iGB') % (((freespace / 1024) / 1024) / 1024)
        self.freespace = (((freespace / 1024) / 1024) / 1024)
        self.totalspace = (((totalspace / 1024) / 1024) / 1024)
        if self.totalspace == 0:
            self.percent = 0
        else:
            self.percent = (self.totalspace - self.freespace) * 1.0 / self.totalspace


    def draw(self, (type, object), x, osd):
        """
        Drawing to idlebar
        """
        self.getDiskFree()
        diskimg = self.getimage(self.diskimg, osd)
        w, h = diskimg.get_size()
        if self.freespace < config.DISKFREE_VERY_LOW:
            diskbar = self.getimage(self.badimg, osd, True)
        elif self.freespace < config.DISKFREE_LOW:
            diskbar = self.getimage(self.poorimg, osd, True)
        else:
            diskbar = self.getimage(self.goodimg, osd, True)
        diskimg.blit(diskbar, (0, 0), (0, 0, (w * self.percent), h))
        self.cacheimg['cached'] = diskimg
        font = osd.get_font('small0')
        widthdf = font.stringsize(self.diskfree)
        diskfree_x = x + ((w - widthdf) / 2)
        diskfree_y = osd.y + 55 - font.h
        w = osd.drawimage(diskimg, (x, osd.y + 7, -1, -1) )[0]
        osd.write_text(self.diskfree, font, None, diskfree_x, diskfree_y, widthdf, font.h, 'center', 'top')

        return widthdf + 15
