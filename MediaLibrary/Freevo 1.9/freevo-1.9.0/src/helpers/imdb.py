#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# IMDB helper script to generate fxd files
# -----------------------------------------------------------------------
# $Id: imdb.py 11565 2009-05-25 18:36:59Z duncan $
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
from optparse import OptionParser

try:
    import config
except ImportError:
    print 'imdb.py can\'t be executed outside the Freevo environment.'
    print 'Please use \'freevo imdb [args]\' instead'
    sys.exit(0)

from util.fxdimdb import FxdImdb, makeVideo
from random import Random


def parse_options(defaults):
    """
    Parse command line options
    """
    parser = OptionParser(version='%prog 1.0', conflict_handler='resolve', usage="""
Search IMDB for a movie or a TV show

freevo imdb [options] <search> [<output> <video file> [<video file>]]

Generate <output>.fxd for the movie.  Files is a list of files that belongs to
this movie.  Use [dvd|vcd] to add the whole disc or use [dvd|vcd][title] to add
a special DVD or VCD title to the list of files""")
    parser.add_option('-v', '--verbose', action='count', default=0,
        help='set the level of verbosity [default:%default]')
    parser.add_option('-s', '--search', action='store_true', dest='search', default=False,
        help='search imdb for string [default:%default]')
    parser.add_option('-g', '--guess', action='store_true', dest='guess', default=False,
        help='search imdb for possible filename match [default:%default]')
    parser.add_option('--tv', action='store_true', dest='tv', default=False,
        help='specify the search is a tv programme [default:%default]')
    parser.add_option('--season', dest='season', default=None,
        help='specify the season in the search [default:%default]')
    parser.add_option('--episode', dest='episode', default=None,
        help='specify the episode in the search [default:%default]')
    parser.add_option('-d', '--rom-drive', action='store', dest='rom_drive',
        help='specify the CD/DVD device [default:%default]')
    parser.add_option('-a', '--add', action='store_true', dest='add', default=False,
        help='add a video file to the fxd file [default:%default]')
    parser.add_option('--encoding', action='store', dest='encoding', default='utf-8', metavar='ENC',
        help='terminal encoding to display the results [default:%default]')
    return parser.parse_args()


def parse_file_args(input):
    files = []
    cdid  = []
    for i in input:
        if i == 'dvd' or i == 'vcd' or i == 'cd':
            cdid += [ i ]
        else:
            files += [ i ]
    return files, cdid



#
# Main function
#
if __name__ == "__main__":
    drive = '/dev/cdrom'
    driveset = False

    task = ''
    search_arg = ''

    (opts, args) = parse_options({})
    if args[0] == 'imdb':
        args.pop(0)
    _debug_('opts=%r' % (opts,))
    _debug_('args=%r' % (args,))

    # check the aruments
    if opts.search and opts.guess:
        sys.exit(u'--search and --guess are mutually exclusive')
    elif opts.add and len(args != 2):
        sys.exit(u'--add requires <fxd filename> <video file>')
    elif opts.search and len(args) < 1:
        sys.exit(u'--search requires <search pattern>')
    elif opts.guess and len(args) < 1:
        sys.exit(u'--guess requires <guess pattern>')
    tv_marker = (opts.tv or opts.season or opts.episode) and '"' or ''

    if opts.rom_drive is not None:
        driveset = True

    fxd = FxdImdb()

    if opts.add:
        fxd.setFxdFile(args[0])
        fxd.setFxdFile(arg[0])
        if fxd.isDiscset() is None:
            sys.exit(u'Fxd file is not valid, updating failed')
        elif fxd.isDiscset():
            fxd.setDiscset(opts.rom_drive, None)
        else:
            type = 'file'
            if arg[1].find('[dvd]') != -1: type = 'dvd'
            if arg[1].find('[vcd]') != -1: type = 'vcd'

            id = abs( Random() * 100 )
            if driveset:
                video = makeVideo(type, 'f'+str(id), arg[1], device=opts.rom_drive)
            else:
                video = makeVideo(type, 'f'+str(id), arg[1])
            fxd.setVideo(video)
        fxd.writeFxd()
        sys.exit(0)

    if opts.search:
        title = tv_marker+' '.join(args)+tv_marker
        print "Searching IMDB for '%s'..." % title
        results = fxd.searchImdb(title, opts.season, opts.episode)
        if len(results) == 0:
            print 'No results'
        for result in results:
            if result[3]:
                title = 'http://www.imdb.com/title/tt%s/  %s  %s (%s) %s' % (result[:1] + result[:4])
            elif result[2]:
                title = 'http://www.imdb.com/title/tt%s/  %s  %s (%s)' % (result[:1] + result[:3])
            else:
                title = 'http://www.imdb.com/title/tt%s/  %s  %s' % (result[:1] + result[:2])
            print '%s' % title.encode(opts.encoding)
        sys.exit(0)

    if opts.guess:
        filename = ' '.join(args)
        print "Searching IMDB for '%s'..." % filename
        results = fxd.guessImdb(filename)
        if len(results) == 0:
            print 'No results'
        for result in results:
            if result[3]:
                title = 'http://www.imdb.com/title/tt%s/  %s  %s (%s) %s' % (result[:1] + result[:4])
            elif result[2]:
                title = 'http://www.imdb.com/title/tt%s/  %s  %s (%s)' % (result[:1] + result[:3])
            else:
                title = 'http://www.imdb.com/title/tt%s/  %s  %s' % (result[:1] + result[:2])
            print '%s' % title.encode(opts.encoding)
        sys.exit(0)

    # normal usage
    if len(args) < 3:
        sys.exit(u'requires <imdb id> <fxd filename> <video file>|<cd id>')
    imdb_number = args[0]
    filename = args[1]

    files, cdid = parse_file_args(args[2:])
    if not (files or cdid):
        sys.exit(u'no files or CDID specified')

    fxd.getIMDBid(imdb_number, opts.season, opts.episode)
    fxd.setFxdFile(filename, overwrite=True)

    x=0
    for file in files:
        type = 'file'
        if file.find('[dvd]') != -1: type = 'dvd'
        if file.find('[vcd]') != -1: type = 'vcd'
        if driveset:
            video = makeVideo(type, 'f'+str(x), file, device=drive)
        else:
            video = makeVideo(type, 'f'+str(x), file)
        fxd.setVideo(video)
        x = x+1

    if not files:
        fxd.setDiscset(drive, None)

    fxd.writeFxd()
