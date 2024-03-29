# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
#
# -----------------------------------------------------------------------
# $Id: osd_display.py 11268 2009-01-26 18:46:48Z duncan $
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

import pygame.image
import pygame.draw

import osd

import plugin
import dialog
from dialog.display import GraphicsDisplay
import config

class PluginInterface(plugin.Plugin):
    """
    Enables the use of the dialog layer in the menu screens to show messages,
    volume and dialogs.
    """
    def __init__(self):
        dialog.set_osd_display(OSDGraphicsDisplay())
        plugin.Plugin.__init__(self)


class OSDGraphicsDisplay(GraphicsDisplay):
    """
    Display class that uses the osd.dialog_layer to display dialogs/volume and messages.
    """
    def __init__(self):
        super(OSDGraphicsDisplay, self).__init__()
        self.osd = osd.get_singleton()
        self.last_dialog = None

    def show_image(self, image, position):
        """
        Show the supplied image on the OSD layer.

        @note: Subclasses should override this method to display the image
        using there own mechanism

        @param image: A kaa.imlib2.Image object to be displayed.
        @param position: (x, y) position to display the image.
        """
        buf = str(image.get_raw_data('RGBA'))
        surface = pygame.image.frombuffer(buf, image.size, 'RGBA')
        # If the dialog handles events then dim the background to show the
        # dialog now has focus.
        if hasattr(self.current_dialog, 'handle_event'):
            fill_color = (0,0,0,config.OSD_DIALOG_BACKGROUND_DIM)
        else:
            fill_color = (0,0,0,0)
        # Only clear the screen if the dialog is different to last time.
        if self.last_dialog != self.current_dialog:
            self.osd.dialog_layer.fill(fill_color)
            self.last_dialog = self.current_dialog
        else:
            pygame.draw.rect(self.osd.dialog_layer, fill_color, (position[0], position[1], image.width, image.height))

        self.osd.drawsurface(surface, position[0], position[1], layer=self.osd.dialog_layer)
        self.osd.dialog_layer_enabled= True
        self.osd.update()


    def hide_image(self):
        """
        Hide the currently displayed image.

        @note: Subclasses should override this method to hide the image
        displayed using show_image()
        """
        self.osd.dialog_layer_enabled= False
        self.osd.update()
