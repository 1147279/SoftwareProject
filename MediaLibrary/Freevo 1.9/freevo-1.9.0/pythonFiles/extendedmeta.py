# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Extended Metadata Reader/Cacher
# -----------------------------------------------------------------------
# $Id: extendedmeta.py 11415 2009-04-13 18:40:53Z duncan $
#
# Notes:
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


# The basics
import os, string, fnmatch, sys, md5, stat

# Metadata tools
import config, util
import util.fxdparser
import mediainfo
import plugin

try:
    from util.dbutil import *
except ImportError:
    pass

import kaa.metadata.audio.eyeD3 as eyeD3
from util import recursefolders

##### Database

dbschema = """CREATE TABLE music (id INTEGER PRIMARY KEY, dirtitle VARCHAR(255), path VARCHAR(255),
        filename VARCHAR(255), type VARCHAR(5), artist VARCHAR(255), title VARCHAR(255), album VARCHAR(255),
        genre VARCHAR(255), year VARCHAR(255), track NUMERIC(3), track_total NUMERIC(3), bpm NUMERIC(3),
        last_play float, play_count NUMERIC, start_time NUMERIC, end_time NUMERIC, rating NUMERIC, eq VARCHAR)"""


def make_query(filename, dirtitle):
    _debug_('make_query(filename=%r, dirtitle=%r)' % (filename, dirtitle), 2)
    if not os.path.exists(filename):
        print "File %s does not exist" % (filename)
        return None

    a = mediainfo.get(filename)
    t = tracknum(a['trackno'])
    ext = os.path.splitext(filename)[1]

    values = {}
    values['id'] = 'null'
    values['dirtitle'] = util.escape(dirtitle)
    values['path'] = util.escape(os.path.dirname(filename))
    values['filename'] = util.escape(os.path.basename(filename))
    values['type'] = ext
    values['artist'] = util.escape(a['artist'])
    values['title'] = util.escape(a['title'])
    values['album'] = util.escape(a['album'])
    values['genre'] = util.escape(a['genre'])
    values['year'] = inti(a['date'])
    values['track'] = int(t[0])
    values['track_total'] = int(t[1])
    values['bpm'] = a['bitrate'] and int(a['bitrate']) or -1
    values['last_play'] = float(0)
    values['play_count'] = int(0)
    values['start_time'] = inti(a['0'])
    values['end_time'] = a['length'] and inti(a['length']) or -1
    values['rating'] = int(0)
    values['eq'] = 'null'

    # if there is an error in one of the values it will show in this block
    "%(id)s" % values
    "'%(dirtitle)s'" % values
    "'%(path)s'" % values
    "'%(filename)s'" % values
    "'%(type)s'" % values
    "'%(artist)s'" % values
    "'%(title)s'" % values
    "'%(album)s'" % values
    "'%(genre)s'" % values
    "'%(year)s'" % values
    "%(track)i" % values
    "%(track_total)i" % values
    "%(bpm)i" % values
    "%(last_play)f" % values
    "%(play_count)i" % values
    "%(start_time)i" % values
    "%(end_time)i" % values
    "%(rating)i" % values
    "'%(eq)s'" % (values)

    # Assign the values
    VALUES = """%(id)s, '%(dirtitle)s', '%(path)s', '%(filename)s', '%(type)s', '%(artist)s', '%(title)s',
        '%(album)s', '%(genre)s', '%(year)s', %(track)i, %(track_total)i, %(bpm)i, %(last_play)f,
        %(play_count)i, %(start_time)i, %(end_time)i, %(rating)i, '%(eq)s'""" % (values)

    SQL = 'INSERT OR IGNORE INTO music VALUES (%s)' % VALUES
    return SQL


def addPathDB(path, dirtitle, type='*.mp3;*.ogg;*.flac', verbose=True):
    _debug_('addPathDB(path=%r, dirtitle=%r, type=%r, verbose=%r)' % (path, dirtitle, type, verbose), 2)

    # Get some stuff ready
    count = 0
    db = MetaDatabase();
    if not db.checkTable('music'):
        db.runQuery(dbschema)

    # Compare and contrast the db to the disc
    songs = util.recursefolders(path, 1, type, 1)
    for row in db.runQuery('SELECT path, filename FROM music'):
        try:
            songs.remove(os.path.join(row['path'], row['filename']))
            count = count + 1
        except ValueError:
            # Why doesn't it just give a return code
            pass

    if count > 0 and verbose:
        print "  Skipped %i songs already in the database..." % (count)

    for song in songs:
        db.runQuery(make_query(song, dirtitle))
    db.close()


##### Audio Information

various = u'__various__'

class AudioParser:
    """
    """
    def __init__(self, dirname, force=False, rescan=False):
        self.artist  = ''
        self.album   = ''
        self.year    = ''
        self.length  = 0
        self.changed = False
        self.force   = force
        self.tag     = eyeD3.Tag()

        cachefile    = vfs.getoverlay(os.path.join(dirname, '..', 'freevo.cache'))
        subdirs      = util.getdirnames(dirname, softlinks=False)
        filelist     = None

        if not rescan:
            for subdir in subdirs:
                d = AudioParser(subdir, rescan)
                if d.changed:
                    break

            else:
                # no changes in all subdirs, looks good
                if os.path.isfile(cachefile) and os.stat(dirname)[stat.ST_MTIME] <= os.stat(cachefile)[stat.ST_MTIME]:
                    # and no changes in here. Do not parse everything again
                    if force:
                        # forces? We need to load our current values
                        info = mediainfo.get(dirname)
                        if info:
                            for type in ('artist', 'album', 'year', 'length'):
                                if info.has_key(type):
                                    setattr(self, type, info[type])
                    return

        if not filelist:
            filelist = util.match_files(dirname, config.AUDIO_SUFFIX)

        if not filelist and not subdirs:
            # no files in here? We are done
            return

        # ok, something changed here, too bad :-(
        self.changed = True
        self.force   = False

        # scan all subdirs
        for subdir in subdirs:
            d = AudioParser(subdir, force=True, rescan=rescan)
            for type in ('artist', 'album', 'year'):
                setattr(self, type, self.strcmp(getattr(self, type), getattr(d, type)))
            self.length += d.length

        # cache dir first
        mediainfo.cache_dir(dirname)

        use_tracks = True

        for song in filelist:
            try:
                data = mediainfo.get(song)
                for type in ('artist', 'album'):
                    setattr(self, type, self.strcmp(getattr(self, type), data[type]))
                self.year = self.strcmp(self.year, data['date'])
                if data['length']:
                    self.length += int(data['length'])
                use_tracks = use_tracks and data['trackno']
            except OSError:
                pass

        if use_tracks and (self.album or self.artist):
            mediainfo.set(dirname, 'audio_advanced_sort', True)

        if not self.length:
            return

        for type in ('artist', 'album', 'year', 'length'):
            if getattr(self, type):
                mediainfo.set(dirname, type, getattr(self, type))

        data    = mediainfo.get(dirname)
        modtime = os.stat(dirname)[stat.ST_MTIME]
        if not data['coverscan'] or data['coverscan'] != modtime:
            data.store('coverscan', modtime)
            self.extract_image(dirname)


    def strcmp(self, s1, s2):
        s1 = Unicode(s1)
        s2 = Unicode(s2)

        if not s1 or not s2:
            return s1 or s2
        if s1 == various or s2 == various:
            return various

        if s1.replace(u' ', u'').lower() == s2.replace(u' ', u'').lower():
            return s1
        return various


    def get_md5(self, obj):
        m = md5.new()
        if isinstance(obj, file):     # file
            for line in obj.readlines():
                m.update(line)
            return m.digest()
        else:                        # str
            m.update(obj)
            return m.digest()


    def extract_image(self, path):
        for i in util.match_files(path, ['mp3']):
            try:
                self.tag.link(i)
            except eyeD3.InvalidAudioFormatException:
                print 'Cannot get tag for "%s"' % (String(i))
                continue
            except:
                continue
            iname = os.path.splitext(os.path.basename(i))[0]+'.jpg'
            myname = vfs.getoverlay(os.path.join(path, iname))
            images = self.tag.getImages();
            for img in images:
                if vfs.isfile(myname) and (self.get_md5(vfs.open(myname, 'rb')) == self.get_md5(img.imageData)):
                    # Image already there and has identical md5, skip
                    pass
                else:
                    f = vfs.open(myname, "wb")
                    f.write(img.imageData)
                    f.flush()
                    f.close()



class PlaylistParser(AudioParser):
    """
    """
    def __init__(self, item, rescan=False):

        self.artist  = ''
        self.album   = ''
        self.year    = ''
        self.length  = 0

        item.build()
        songs = []
        for i in item.playlist:
            if not callable(i):
                for p in plugin.mimetype('audio'):
                    songs += p.get(None, [ i ])
            else:
                songs.append(i)

        for song in songs:
            if not hasattr(song, 'filename'):
                continue
            try:
                data = mediainfo.get(song.filename)
                for type in ('artist', 'album'):
                    setattr(self, type, self.strcmp(getattr(self, type), data[type]))
                self.year = self.strcmp(self.year, data['date'])
                if data['length']:
                    self.length += int(data['length'])
            except OSError:
                pass

        if not self.length:
            return

        for type in ('artist', 'album', 'year', 'length'):
            if getattr(self, type):
                mediainfo.set(item.filename, type, getattr(self, type))
