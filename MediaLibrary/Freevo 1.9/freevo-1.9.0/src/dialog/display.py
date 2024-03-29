# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
#
# -----------------------------------------------------------------------
# $Id: display.py 11345 2009-03-14 14:35:42Z duncan $
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

"""
Module defining the Display interface.
Displays can either support displaying dialogs or not. If they don't support dialogs
then only the following three functions will be implemented.
 - show_volume()
 - show_message()
 - show_play_state()

If dialogs are supported then they will be prioritised to allow higher priority dialogs
to be displayed over lower priority ones. The lower priority dialogs will be queued until
the higher priority dialog closes.

"""

import time
import threading

import config
import kaa
import osd
import event
import plugin

import dialogs

from pygame.locals import *

class Display(object):
    """
    Base class for all display classes.
    Subclasses of this class should implement the following functions:
     - show_volume()
     - show_message()

    If dialogs are supported by the display the following functions should also
    be implemented:
     - show_dialog()
     - hide_dialog()

    To change the display of playing state information the following function
    should overridden:
     - show_play_state()
    """
    def __init__(self, supports_dialogs):
        self.supports_dialogs = supports_dialogs

    def show_volume(self, level, muted, channel=None):
        """
        Display the volume level and whether it has been muted.

        @param level: Main volume level.
        @param muted: True if audio output has been muted, False otherwise.
        @param channel: The channel to show the volume for or None for the main level.
        Valid channels names are:
         - main
         - center
         - surround
         - lfe
        """
        pass

    def show_message(self, message):
        """
        show a generic message.

        @param message: Message to display.
        """
        pass

    def show_play_state(self, state, get_time_info=None):
        """
        show the playing state of the current media.

        @param state: The play state can be one of the following:
         - play
         - pause
         - rewind
         - fastforward
         - seekback
         - seekforward
         - slow
         - fast
        @param get_time_info: A function to call to retrieve information about the
        current position and total play time, or None if not available. The function
        will return a tuple of total time and elapsed time.
        """
        if state == 'play':
            self.show_message(_('Playing'))
        elif state == 'pause':
            self.show_message(_('Paused'))
        elif state == 'rewind':
            self.show_message(_('Rewind'))
        elif state == 'fastforward':
            self.show_message(_('Fast forward'))
        elif state == 'seekback':
            self.show_message(_('Seeking back'))
        elif state == 'seekforward':
            self.show_message(_('Seeking forward'))
        elif state == 'slow':
            self.show_message(_('Slow'))
        elif state == 'fast':
            self.show_message(_('Fast'))

    def handle_event(self, event):
        """
        Handle events from the main loop.
        If dialogs are supported by the display and a dialog is shown,
        the events should be passed to the dialogs handle_event() method.

        This method currently intercepts the following events:
         - OSD_MESSAGE : Calls show_message() on itself.
        returns False to allow other parts of the system to process the event.

        @param event: The event to process
        @return: True if the event was processed, False if it should be passed to another handler.
        @rtype: bool
        """
        if event == 'OSD_MESSAGE':
            self.show_message(event.arg)
            return True

        return False

    def show_dialog(self, dialog, duration):
        """
        Show the supplied dialog for upto duration seconds.
        @note: Subclasses that support dialogs should implement this method.

        @param dialog: The dialog to render.
        @param duration: The maximum length of time to display the dialog.
        """
        pass

    def hide_dialog(self, dialog):
        """
        Hide a currently display dialog.
        @note: Subclasses that support dialogs should implement this method.
        @param dialog: The dialog to hide.
        """
        pass

    def enabled(self):
        """
        Called to inform the display that it is now the active display.
        """
        pass

    def disabled(self):
        """
        Called to inform the display it is no longer the active display.
        """
        pass

class AppTextDisplay(Display):
    """
    Class to be used to allow messages and volume to be displayed on by an
    external application.
    """
    def __init__(self, write_message):
        """
        Create a new instance.
        @param write_message: Function used to request the external application to display some text.
        """
        super(AppTextDisplay, self).__init__(False)
        self.write_message = write_message

    def show_volume(self, level, muted, channel=None):
        if not channel:
            channel = 'Volume'

        if muted:
            self.write_message(_('%s: Muted') % channel)
        else:
            self.write_message(Unicode('%s: %d%%') % (channel,level))

    def show_message(self, message):
        self.write_message(message)


class GraphicsDisplay(Display):
    """
    Base class for displays that can display dialogs.
    This class overrides show_message() and show_volume() to use dialogs to
    display the information.
    """
    def __init__(self):
        """
        Create a new instance.
        """
        super(GraphicsDisplay, self).__init__(True)
        self.current_dialog = None
        self.current_time_details = None
        self.waiting = {'normal':None, 'low':None}
        self.hide_dialog_timer = kaa.OneShotTimer(self.__hide_dialog)
        self._lock = threading.RLock()
        self.volume_dialog = None

    def handle_event(self, evt):
        if self.current_dialog and hasattr(self.current_dialog, 'handle_event'):
            return self.current_dialog.handle_event(evt)

        return super(GraphicsDisplay,self).handle_event(evt)

    def handle_mouse_event(self, evt):
        if self.current_dialog and hasattr(self.current_dialog, 'handle_mouse_event'):
            self.current_dialog.handle_mouse_event(evt)


    def show_volume(self, level, muted, channel=None):
        if self.volume_dialog is None:
            self.volume_dialog = dialogs.VolumeDialog()
        self.volume_dialog.set_details(level, muted, channel)
        self.volume_dialog.show()

    def show_message(self, message):
        dialog = dialogs.MessageDialog(message)
        dialog.show()

    def show_play_state(self, state, get_time_info=None):
        dialog = dialogs.PlayStateDialog(state, get_time_info)
        dialog.show()

    def show_dialog(self, dialog, duration):
        """
        Show the supplied dialog for upto duration seconds.
        @param dialog: The dialog to render.
        @param duration: The maximum length of time to display the dialog.
        """
        self._lock.acquire()
        #Stop any pending hide timers
        self.hide_dialog_timer.stop()

        if self.current_dialog and self.current_dialog != dialog:
            _debug_('Dialog already open, current priority %s new dialog priority %s' % (self.current_dialog.priority, dialog.priority))
            if self.current_dialog.priority == 'normal' and dialog.priority == 'high' or \
               self.current_dialog.priority == 'low' and dialog.priority == 'normal':

                now = time.time()

                left = self.current_time_details[1] - (now - self.current_time_details[0])
                if left > 0.0:
                    _debug_('Queuing current dialog, time left %f' % left)
                    self.waiting[self.current_dialog.priority] = (self.current_dialog, left, True)
                    # We don't finish the dialog as we will be displaying it again when
                    # the higher priority dialog closes.
                else:
                    # No time left on the clock for this dialog so finish it.
                    self.current_dialog.finish()
                self.hide_dialog_timer.stop()
                self.current_dialog = None
            elif dialog.priority == 'normal' and self.current_dialog.priority == 'high' or \
                 dialog.priority == 'low' and self.current_dialog.priority == 'normal':
                _debug_('Queuing new dialog')
                self.waiting[dialog.priority] = (dialog, duration, False)
                self._lock.release()
                return
            else:
                self.hide_dialog(self.current_dialog)

        if not self.current_dialog:
            self.current_dialog = dialog
            self.current_time_details = (time.time(), duration)
            dialog.prepare()

        self.show_image(dialog.render(), dialog.skin.position)

        if duration is not None and duration > 0:
            self.hide_dialog_timer.start(duration)

        self._lock.release()

    def hide_all_dialogs(self):
        """
        Hide currently showing and queued dialogs.
        """
        self._lock.acquire()
        if self.current_dialog:
            self.current_dialog.finish()
            self.current_dialog = None
            self.hide_dialog_timer.stop()
            self.hide_image()
            if self.waiting[dialogs.Dialog.NORMAL_PRIORITY]:
                dialog, duration, prepared = self.waiting[dialogs.Dialog.NORMAL_PRIORITY]
                dialog.finish()
            if self.waiting[dialogs.Dialog.LOW_PRIORITY]:
                dialog, duration, prepared = self.waiting[dialogs.Dialog.LOW_PRIORITY]
                dialog.finish()
        self._lock.release()

    def hide_dialog(self, dialog):
        """
        Hide a currently display dialog.
        @param dialog: The dialog to hide.
        """
        self._lock.acquire()
        if self.current_dialog is not None and self.current_dialog == dialog:
            priority = self.current_dialog.priority
            self.hide_dialog_timer.stop()
            self.current_dialog.finish()
            self.current_dialog = None
            self.hide_image()
            _debug_('Closing dialog priority %s' % priority)
            # Now check lower priority waiting queue for any dialogs waiting to be displayed
            if priority == dialogs.Dialog.HIGH_PRIORITY:
                priority = dialogs.Dialog.NORMAL_PRIORITY
            elif priority == dialogs.Dialog.NORMAL_PRIORITY:
                priority = dialogs.Dialog.LOW_PRIORITY
            else:
                priority = None

            _debug_('Checking priority %s' % priority)
            if priority:
                waiting = self.waiting[priority]
                if waiting:
                    self.waiting[priority] = None
                    dialog, duration, prepared = waiting
                    self.current_dialog = dialog
                    if not prepared:
                        dialog.prepare()

                    self.show_image(dialog.render(), dialog.skin.position)

                    if duration is not None and duration > 0:
                        self.hide_dialog_timer.start(duration)

        else:
            # Check the waiting queue and remove if found.
            waiting = self.waiting[dialog.priority]
            if waiting and waiting[0] == dialog:
                self.waiting[dialog.priority] = None

        self._lock.release()

    def __hide_dialog(self):
        """
        Called when the hide_dialog_timer fires to close the current dialog.
        """
        self.hide_dialog(self.current_dialog)

    def disabled(self):
        self.hide_all_dialogs()

    #===============================================================================
    #  Methods that should be overridden by subclasses
    #===============================================================================
    def show_image(self, image, position):
        """
        Show the supplied image on the OSD layer.

        @note: Subclasses should override this method to display the image
        using there own mechanism

        @param image: A kaa.imlib2.Image object to be displayed.
        @param position: (x, y) position to display the image.
        """
        pass

    def hide_image(self):
        """
        Hide the currently displayed image.

        @note: Subclasses should override this method to hide the image
        displayed using show_image()
        """
        pass
