#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Wrapper for xmltv
# -----------------------------------------------------------------------
# $Id: tv_grab.py 11499 2009-05-13 20:14:48Z duncan $
#
# Notes:
#
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


import sys
import os
import shutil
from optparse import Option, OptionParser, IndentedHelpFormatter

import config

def grab():
    if not config.XMLTV_GRABBER:
        print 'No program found to grab the listings. Please set XMLTV_GRABBER'
        print 'in local.conf.py to the grabber you need'

    print 'Grabbing listings.'
    xmltvtmp = '/tmp/TV.xml.tmp'
    ec = os.system('%s --output %s --days %s' % ( config.XMLTV_GRABBER, xmltvtmp, config.XMLTV_DAYS ))

    if os.path.exists(xmltvtmp) and ec == 0:
        if os.path.isfile(config.XMLTV_SORT):
            print 'Sorting listings.'
            os.system('%s --output %s %s' % ( config.XMLTV_SORT, xmltvtmp+'.1', xmltvtmp ))
            shutil.copyfile(xmltvtmp+'.1', xmltvtmp)
            os.unlink(xmltvtmp+'.1')
        else:
            print 'Not configured to use tv_sort, skipping.'

        print 'caching data, this may take a while'

        import tv.epg_xmltv
        tv.epg_xmltv.get_guide(XMLTV_FILE=xmltvtmp)
    else:
        sys.stderr.write("\n")
        sys.stderr.write("ERROR: xmltv grabbing failed; %s returned exit code %d.\n" % (config.XMLTV_GRABBER, ec >> 8))
        sys.exit(
            "If you did not change your system, it's likely that the site being grabbed did.\n"
            "You might want to try whether updating your xmltv helps in that case:\n"
            "   http://www.xmltv.org/\n")


if __name__ == '__main__':

    def parse_options():
        """
        Parse command line options
        """
        import version
        formatter = IndentedHelpFormatter(indent_increment=2, max_help_position=32, width=100, short_first=0)
        parser = OptionParser(conflict_handler='resolve', formatter=formatter, usage="freevo %prog [options]",
            version='%prog ' + str(version.version))
        prog = os.path.basename(sys.argv[0])
        parser.prog = os.path.splitext(prog)[0]
        parser.description = "Downloads the listing for xmltv and cache the data"
        parser.add_option('-q', '--query', action='store_true', default=False,
            help='print a list of all stations. The list can be used to set TV_CHANNELS [default:%default]')

        opts, args = parser.parse_args()
        return opts, args


    opts, args = parse_options()

    if opts.query:
        print
        print 'searching for station information'

        chanlist = config.detect_channels()

        print
        print 'Possible list of tv channels. If you want to change the station'
        print 'id, copy the next statement into your local_conf.py and edit it.'
        print 'You can also remove lines or resort them'
        print
        print 'TV_CHANNELS = ['
        for c in chanlist[:-1]:
            print '    ( \'%s\', \'%s\', \'%s\' ), ' % c
        print '    ( \'%s\', \'%s\', \'%s\' ) ] ' % chanlist[-1]
        sys.exit(0)

    grab()

    import kaa
    from tv.record_client import RecordClient

    def handler(result):
        if result:
            print _('Updated recording schedule')
        else:
            print _('Not updated recording schedule')
        raise SystemExit


    rc = RecordClient()
    try:
        kaa.inprogress(rc.channel).wait()
    except Exception, why:
        print 'Cannot connect to record server'
        raise SystemExit

    print 'Scheduling favorites for recording:  '
    if not rc.updateFavoritesSchedule(handler):
        print rc.recordserverdown
        raise SystemExit

    kaa.main.run()
