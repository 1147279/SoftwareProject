#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# iceslistchanger.rpy - change ices playlist via web interface.
# -----------------------------------------------------------------------
# $Id: iceslistchanger.rpy,v 1.5 2004/02/19 04:57:59 gsbarbieri Exp $
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log: iceslistchanger.rpy,v $
# Revision 1.5  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# To use this, I need to get the gettext() translations in unicode, so some changes are required to files that use "print _('string')", need to make them "print String(_('string'))".
#
# Revision 1.4  2004/02/09 21:23:42  outlyer
# New web interface...
#
# * Removed as much of the embedded design as possible, 99% is in CSS now
# * Converted most tags to XHTML 1.0 standard
# * Changed layout tables into CSS; content tables are still there
# * Respect the user configuration on time display
# * Added lots of "placeholder" tags so the design can be altered pretty
#   substantially without touching the code. (This means using
#   span/div/etc. where possible and using 'display: none' if it's not in
#   _my_ design, but might be used by someone else.
# * Converted graphical arrows into HTML arrows
# * Many minor cosmetic changes
#
# Revision 1.3  2003/11/28 19:31:52  dischi
# renamed some config variables
#
# Revision 1.2  2003/09/05 02:48:13  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.1  2003/06/24 17:52:00  dischi
# added iceslistchanger
#
# Revision 1.1  2003/05/12 23:27:11  mruelle
# The start of an m3u list changer page.
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
#endif

import sys, time, os, urllib

from www.web_types import HTMLResource, FreevoResource
import util, config

TRUE = 1
FALSE = 0

class IceslistchangerResource(FreevoResource):

    def change2m3u(self, mylist):
        myfile = file(os.path.join(config.FREEVO_CACHEDIR, 'changem3u.txt'), 'wb')
        myfile.write(mylist)
        myfile.flush()
        myfile.close()

    def _render(self, request):
        fv = HTMLResource()
        form = request.args
 
        directories = config.AUDIO_ITEMS
        rpyscript = 'iceslistchanger.rpy'
        #rpyscript = os.path.basename(os.environ['SCRIPT_FILENAME'])
        rpydir = fv.formValue(form, 'dir')
        rpym3u = fv.formValue(form, 'm3u')

        fv.printHeader('Change ICES Play List', 'styles/main.css')

        #make the file to change m3u list ices plugin will pick up on poll
        if rpym3u:
            self.change2m3u(rpym3u)
            fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Music List', 'class="guidehead" colspan="1"')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('List has been changed to %s' % rpym3u, 'class="basic" colspan="1"')
            fv.tableRowClose()
            fv.tableClose()

        if rpydir:
            fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Pick a Music List', 'class="guidehead" colspan="1"')
            fv.tableRowClose()
            # find m3u's
            rpym3ulist = util.match_files_recursively(rpydir, config.PLAYLIST_SUFFIX)
            for m3u in rpym3ulist:
                title = os.path.basename(m3u)
                link = '<a href="' + rpyscript +'?m3u='+urllib.quote(m3u)+'">'+title+'</a>'

                fv.tableRowOpen('class="chanrow"')
                fv.tableCell(link, 'class="basic" colspan="1"')
                fv.tableRowClose()
            fv.tableClose()
        else:
            fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Pick a Music Directory', 'class="guidehead" colspan="1"')
            fv.tableRowClose()
            for d in directories:
                (title, dir) = d
                link = '<a href="' + rpyscript +'?dir='+urllib.quote(dir)+'">'+title+'</a>'
                fv.tableRowOpen('class="chanrow"')
                fv.tableCell(link, 'class="basic" colspan="1"')
                fv.tableRowClose()
            fv.tableClose()

    
        fv.printSearchForm()
        fv.printLinks()
        fv.printFooter()
        fv.res+=('</ul>')

        return String( fv.res )



resource = IceslistchangerResource()
